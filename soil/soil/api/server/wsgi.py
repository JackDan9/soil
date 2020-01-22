# Copyright 2011 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import inspect
import math
import time

from oslo_log import log as logging
from oslo_serialization import jsonutils
import six
import webob

from soil import exception
from soil.i18n import _, _LI, _LW, _LE
from soi.wsgi import common as wsgi


LOG = logging.getLogger(__name__)


SUPPORTED_CONTENT_TYPES = (
    'application/json',
)

_MEDIA_TYPE_MAP = {
    'application/json': 'json'
}


class Request(webob.Request):
    """Add some OpenStack API-Specific logic to the base webob.Request."""

    def best_match_content_type(self):
        """Determine the requested response content-type."""
        if 'soil.best_content_type' not in self.environ:
            # Calculate the best MIME type
            content_type = None

            # Check URL path suffix
            parts = self.path.rsplit('.', 1)
            if len(parts) > 1:
                possible_type = 'application/' + parts[1]
                if possible_type in SUPPORTED_CONTENT_TYPES:
                    content_type = possible_type
            
            if not content_type:
                content_type = self.accept.best_match(SUPPORTED_CONTENT_TYPES)
            
            self.environ['soil.best_content_type'] = (content_type or 
                                                      'application/json')
            
        return self.environ['soil.best_content_type']
    
    def get_content_type(self):
        """Determine content type of the request body.

        Does not do any body introspection, only checks header

        """
        if "Content-Type" not in self.headers:
            return None
        
        allowed_types = SUPPORTED_CONTENT_TYPES
        content_type = self.content_type

        if content_type not in allowed_types:
            raise exception.InvalidContentType(content_type=content_type)

        return content_type
    

class ActionDispatcher(object):
    """Maps method name to local methods through action name."""

    def dispatch(self, *args, **kwargs):
        """Find and call local method."""
        action = kwargs.pop('action', 'default')
        action_method = getattr(self, str(action), self.default)
        return action_method(*args, **kwargs)
    
    def default(self, data):
        raise NotImplementedError()


class TextDeserializer(ActionDispatcher):
    """Default request body deserialization"""
    
    def deserialize(self, data_string, action="default"):
        return self.dispatch(data_string, action=action)
    
    def default(self, data_string):
        return {}


class JSONDeserializer(TextDeserializer):
    def _from_json(self, data_string):
        try:
            return jsonutils.loads(data_string)
        except ValueError:
            msg = _("Cannot understand JSON")
            raise exception.MalformedRequestBody(reason=msg)
    
    def default(self, data_string):
        return {'body': self._from_json(data_string)}


class DictSerializer(ActionDispatcher):
    """Default request body serialization"""

    def serialize(self, data, action='default'):
        return self.dispatch(data, action=action)

    def default(self, data):
        return ""


class JSONDictSerializer(DictSerializer):
    """Default JSON request body serialization"""

    def default(self, data):
        return jsonutils.dumps(data)


def serializers(**serializers):
    """Attaches serializers to a method.

    This decorator associates a dictionary of serializers with a
    method. Note that the function attributes are directly
    manipulated; the method is not wrapped.

    """

    def decorator(func):
        if not hasattr(func, 'wsgi_serializers'):
            func.wsgi_serializers = {}
        func.wsgi_serializers.update(serializers)
        return func
    return decorator


def deserializers(**deserializers):
    """Attaches deserializers to a method.

    This decorator associates a dictionary of deserializers with a
    method. Note that the function attributes are directly
    manipulated; the method is not wrapped.

    """


def response(code):
    """Attaches response code to a method.

    This decorator associates a response code with a method. 
    Note that the function attributes are directly manipulated; 
    the method is not wrapped.

    """

    def decorator(func):
        func.wsgi_coded = code
        return func
    return decorator


class ResponseObject(object):
    """Bundles a response object with appropriate serializers.

    Object that app methods may return in order to bind alternate
    serializers with a response object to be serialized. 
    Its use is optional
    
    """

    def __init__(self, obj, code=None, **serializers):
        """Binds serializers with an object.

        Takes keyword arguments akin to the @serializer() decorator
        for specifying serializers. Serializers specified will be
        give preference over default serializers or method-specific
        serializers on return.
        
        """

        self.obj = obj
        self.serializers = serializers
        self._default_code = 200
        self._code = code
        self._headers = {}
        self.serializer = None
        self.media_type = None

    def __getitem__(self, key):
        """Retrieves a header with the given name."""

        return self._headers[key.lower()]
    
    def __setitem__(self, key, value):
        """Set a header with the given name to the given value."""

        self._headers[key.lower()] = value
    
    def __delitem__(self, key):
        """Deletes the header with the given name."""
        
        del self._headers[key.lower()]
    
    def _bind_method_serializers(self, method_serializers):
        """Binds method serializers with the response object.

        Binds the method serializers with the response object.
        Serializers specified to the constructor will take precedence
        over serializers specified to this method.

        :param method_serializers: A dictionary with keys mapping to 
                                   response types and values containing
                                   serializer objects.
        """

        # We can't use update because that would be the wrong
        # precedence
        for method_type, serializer in method_serializers.items():
            self.serializers.setdefault(method_type, serializer)
        
    def get_serializer(self, content_type, default_serializers=None):
        """Returns the serializer for the wrapped object.

        Returns the serializer for the wrapped object subject to the 
        indicated content type. If no serializer matching the content
        type is attached, an appropriate serializer drawn from the
        default serializers will be used. If no appropriate
        serializer is available, raises InvalidContentType.        
        
        """
        default_serializers = default_serializers or {}

        try:
            method_type = _MEDIA_TYPE_MAP.get(content_type, content_type)
            if method_type in self.serializers:
                return method_type, self.serializers[method_type]
            else:
                return method_type, default_serializers[method_type]
        except (KeyError, TypeError):
            raise exception.InvalidContentType(content_type=content_type)
    
    def preserialize(self, content_type, default_serializers=None):
        """Prepares the serializer that will be used to serialize.

        Determines the serializer that will be used and prepares an
        instance of it for later call. This allows the serializer to
        be accessed by extensions for, e.g., template extension.

        """
        method_type, serializer = self.get_serializer(content_type,
                                                      default_serializers)
        self.media_type = method_type
        self.serializer = serializer()
    
    def attach(self, **kwargs):
        """Attach slave templates to serializers."""

        if self.media_type in kwargs:
            self.serializer.attach(kwargs[self.media_type])
    
    def serialize(self, request, content_type, default_serializers=None):
        """Serializes the wrapped object.

        Utility method for serializing the wrapped object.
        Returns a webob.Response object.

        """

        if self.serializer:
            serializer = self.serializer
        else:
            _method_type, _serializer = self.get_serializer(content_type,
                                                            default_serializers)
            serializer = _serializer()
        
        response = webob.Response()
        response.status_int = self.code
        for header, value in self._headers.items():
            response.headers[header] = value
        response.headers['Content-Type'] = content_type
        if self.obj is not None:
            response.body = serializer.serialize(self.obj)
        
        return response
    
    @property
    def code(self):
        """Retrieve the response status."""

        return self._code or self._default_code
    
    @property
    def headers(self):
        """Retrieve the headers."""

        return self._headers.copy()


def action_peek_json(body):
    """Determine action to invoke."""

    try:
        decoded = jsonutils.loads(body)
    except ValueError:
        msg = _("cannot understand JSON")
        raise exception.MalformedRequestBody(reason=msg)
    
    # Make sure there's exactly one key...
    if len(decoded) != 1:
        msg = _("too many body keys")
        raise exception.MalformedRequestBody(reason=msg)

    # Return the action and the decoded body...
    return decoded.keys()[0]


class ResourceExceptionHandler(object):
    """Context manager to handle Resource exceptions.

    Used when processing exceptions generated by API implementation
    methods (or their extensions).  Converts most exceptions to Fault
    exceptions, with the appropriate logging.

    """

    def __enter__(self):
        return None
    
    def __exit__(self, ex_type, ex_value, ex_traceback):
        if not ex_value:
            return True
        
        if isinstance(ex_value, exception.NotAuthorized):
            msg = unicode(ex_value)
            raise Fault(webob.exc.HTTPForbidden(explanation=msg))
        elif isinstance(ex_value, exception.Invalid):
            raise Fault(exception.ConvertedException(
                code=ex_value.code, explanation=unicode(ex_value)))
        elif isinstance(ex_value, TypeError):
            exc_info = (ex_type, ex_value, ex_traceback)
            LOG.error(_LE('Exception handling resource: %s' % ex_value, 
                          exc_info=exc_info))
            raise Fault(webob.exc.HTTPBadRequest())
        elif isinstance(ex_value, Fault):
            LOG.info("Fault throw: %s", unicode(ex_value))
            return ex_value
        elif isinstance(ex_value, webob.exc.HTTPException):
            LOG.info("HTTP exception trown: %s", unicode(ex_value))
            raise Fault(ex_value)

        # We didn't handle the exception
        return False


class Resource(wsgi.Application):
    """WSGI app that handles (de) serialization and controller dispatch.

    WSGI app that reads routing information supplied by RoutesMiddleware
    and calls the requested action method upon its controller. All
    controller action methods must accept a 'req' argument, which is the
    incoming wsgi.Request. If the operation is a PUT or POST, the controller
    method must also accept a 'body' argument (the deserialized request body).
    They may raise a webob.exc exception or return a dict, which will be
    serialized by requested content type.

    Exceptions derived from webob.exc.HTTPException will be automatically
    wrapped in Fault() to provide API friendly error responses.

    """

    def __init__(self, controller, action_peek=None, **deserializers):

        self.controller = controller

        default_deserializers = dict(json=JSONDeserializer)
        default_deserializers.update(deserializers)

        self.default_deserializers = default_deserializers
        self.default_serializers = dict(json=JSONDictSerializer)

        self.action_peek = dict(json=action_peek_json)
        self.action_peek.update(action_peek or {})

        # Copy over the actions dictionary
        self.wsgi_actions = {}
        if controller:
            self.register_actions(controller)
        
        # Save a mapping of extensions
        self.wsgi_extensions = {}
        self.wsgi_action_extensions = {}

    def register_actions(self, controller):
        """Registers controller actions with this resource."""

        actions = getattr(controller, 'wsgi_actions', {})
        for key, method_name in actions.items():
            self.wsgi_actions[key] = getattr(controller, method_name)
    
    def register_extensions(self, controller):
        """Registers controller extensions with this resource."""

        extensions = getattr(controller, 'wsgi_extensions', [])
        for method_name, action_name in extensions:
            # Look up the extending method
            extension = getattr(controller, method_name)

            if action_name:
                # Extending an action...
                if action_name not in self.wsgi_action_extensions:
                    self.wsgi_action_extensions[action_name] = []
                self.wsgi_action_extensions[action_name].append(extension)
            else:
                # Extending a regular method
                if method_name not in self.wsgi_extensions:
                    self.wsgi_extensions[method_name] = []
                self.wsgi_extensions[method_name].append(extension)
            
    def get_action_args(self, request_environment):
        """Parse dictionary created by routes library."""

        # NOTE(JackDan): Check for get_action_args() override in the 
        # controller
        if hasattr(self.controller, 'get_action_args'):
            return self.controller.get_action_args(request_environment)
        
        try:
            args = request_environment['wsgiorg.routing_args'][1].copy()
        except (KeyError, IndexError, AttributeError):
            return {}
        
        try:
            del args['controller']
        except KeyError:
            pass
            
        try:
            del args['format']
        except KeyError:
            pass

        return args
    
    def get_body(self, request):
        try:
            content_type = request.get_content_type()
        except exception.InvalidContentType:
            LOG.debug(_LI("Unrecognized Content-Type provided in request"))
            return None, ''
        
        if not content_type:
            LOG.debug(_LI("No Content-Type provided in request"))
            return None, ''
        
        if len(request.body) <= 0:
            LOG.debug(_LI("Empty body provided in request"))
            return None, ''
        
        return content_type, request.body
    
    def deserialize(self, method, content_type, body):
        method_serializers = getattr(method, 'wsgi_deserializers', {})
        try:
            method_type = _MEDIA_TYPE_MAP.get(content_type, content_type)
            if method_type in method_serializers:
                deserializer = method_serializers[method_type]
            else:
                deserializer = self.default_deserializers[method_type]
        except (KeyError, TypeError):
            raise exception.InvalidContentType(content_type=content_type)

        return deserializer().deserialize(body)

    def pre_process_extensions(self, extensions, request, action_args):
        # List of callables for post-processing extensions
        post = []

        for extension in extensions:
            if inspect.isgeneratorfunction(extension):
                response = None

                # If it's a generator function, the part before the
                # yield is the preprocessing stage
                try:
                    with ResourceExceptionHandler():
                        gen = extension(req=request, **action_args)
                        response = gen.next()
                except Fault as ex:
                    response = ex
                
                # We had a response...
                if response:
                    return response, []
                
                # No response, queue up generator for post-processing
                post.append(gen)
            else:
                # Regular functions only perform post-processing
                post.append(extension)
        
        # Run post-processing in the reverse order
        return None, reversed(post)

    def post_process_extensions(self, extensions, resp_obj, request,
                                action_args):
        for extension in extensions:
            response = None
            if inspect.isgenerator(extension):
                # If it's a generator, run the second half of
                # processing
                try:
                    with ResourceExceptionHandler():
                        response = extension.send(resp_obj)
                except StopIteration:
                    # Normal exit of generator
                    continue
                except Fault as ex:
                    response = ex
            else:
                # Regular functions get post-processing...
                try:
                    with ResourceExceptionHandler():
                        response = extension(req=request, resp_obj=resp_obj,
                                             **action_args)
                except Fault as ex:
                    response = ex
            
            # We had a response...
            if response:
                return response
    
        return None

    @webob.dec.wsgify(ReqeustClass=Request)
    def __call__(self, request):
        """WSGI method that controls (de)serialization and method dispatch."""

        LOG.info(_LI("%(method)s %(url)s" %{"method": request.method,
                                            "url": request.url}))

        # Identify the action, its arguments, and the requested
        # content type
        action_args = self.get_action_args(request.environ)
        action = action_args.pop('action', None)
        content_type, body = self.get_body(request)
        accept = request.best_match_content_type()

        # NOTE(JackDan): Splitting the function up this way allows for 
        #                auditing by external tools that wrap the existing
        #                function. If we try to audit __call__(), we can
        #                run into troubles due to the @webob.dec.wsgify()
        #                decorator.
        return self._process_stack(request, action, action_args,
                                   content_type, body, accept)

    def _process_stack(self, request, action, action_args,
                       content_type, body, accept):
        """Implement the processing stack."""

        # Get the implementing method
        try:
            method, extensions = self.get_method(request, action,
                                                 content_type, body)
        except (AttributeError, TypeError):
            return Fault(webob.exc.HTTPNotFound())
        except KeyError as ex:
            msg = _LI("There is no such action: %s") % ex.args[0]
            return Fault(webob.exc.HTTPBadRequest(explanation=msg))
        except exception.MalformedRequestBody:
            msg = _LI("Malformed request body")
            return Fault(webob.exc.HTTPBadRequest(explanation=msg))

        # Now, deserialize the request body...
        try:
            if content_type:
                contents = self.deserialize(method, content_type, body)
            else:
                contents = {}
        except exception.InvalidContentType:
            msg = _LI("Unsupported Content-Type")
            return Fault(webob.exc.HTTPBadRequest(explanation=msg))
        except exception.MalformedRequestBody:
            msg = _LI("Malformed request body")
            return Fault(webob.exc.HTTPBadRequest(explanation=msg))
        
        # Update the action args
        action_args.update(contents)

        project_id = action_args.pop("project_id", None)
        context = request.environ.get('soil.context')
        if (context and project_id and (project_id != context.project_id)):
            msg = _LI("Malformed request url")
            return Fault(webob.exc.HTTPBadRequest(explanation=msg))
        
        # Run pre-processing extensions
        response, post = self.pre_process_extensions(extensions,
                                                     request, action_args)

        if not response:
            try:
                with ResourceExceptionHandler():
                    action_result = self.dispatch(method, request, action_args)
            except Fault as ex:
                response = ex
        
        if not response:
            # No exceptions; convert action_result into a
            # ResponseObject
            resp_obj = None
            if type(action_result) is dict or action_result is None:
                resp_obj = ResponseObject(action_result)
            elif isinstance(action_result, ResponseObject):
                resp_obj = action_result
            else:
                response = action_result
            
            # Run post-processing extensions
            if resp_obj:
                _set_request_id_header(request, resp_obj)
                # Do a preserialize to set up the response object
                serializers = getattr(method, 'wsgi_serializers', {})
                resp_obj._bind_method_serializers(serializers)
                if hasattr(method, 'wsgi_code'):
                    resp_obj._default_code = method.wsgi_code
                resp_obj.preserialize(accept, self.default_serializers)

                # Process post-processing extensions
                response = self.post_process_extensions(post, resp_obj,
                                                        request, action_args)
            
            if resp_obj and not response:
                response = resp_obj.serialize(request, accept,
                                              self.default_serializers)

        try:
            msg_dict = dict(url=request.url, status=response.status_int)
            msg = _LI("%(url)s returned with HTTP %(status)d") % msg_dict
        except AttributeError as e:
            msg_dict = dict(url=request.url, e=e)
            msg = _LI("%(url)s returned a fault: %(e)s") % msg_dict
        
        LOG.info(msg)

        return response

    def get_method(self, request, action, content_type, body):
        """Look up the action-specific method and its extensions."""

        # Look up the method
        try:
            if not self.controller:
                method = getattr(self, action)
            else:
                method = getattr(self.controller, action)
        except AttributeError:
            if (not self.wsgi_actions or 
                    action not in ['action', 'create', 'delete']);
                # Propagate the error
                raise
        else:
            return method, self.wsgi_extensions.get(action, [])
        
        if action == 'action':
            # Ok, it's an action; figure out which action...
            method_type = _MEDIA_TYPE_MAP.get(content_type)
            action_name = self.action_peek[method_type](body)
            LOG.debug("Action body: %s" % body)
        else:
            action_name = action
        
        # Look up the action method
        return (self.wsgi_actions[action_name],
                self.wsgi_action_extensions.get(action_name, []))
        
    def dispatch(self, method, request, action_args):
        """Dispatch a call to the action-specific method."""
        return method(req=request, **action_args)
    

def action(name):
    """Mark a function as an action.

    The given name will be taken as the action key in the body.

    This is also overloaded to allow extensions to provide
    non-extending definitions of create and delete operations.

    """
    
    def decorator(func):
        func.wsgi_action = name
        return func
    return decorator


def extends(*args, **kwargs):
    """Indicate a function extends an operation.

    Can be used as either::

        @extends
        def index(...):
            pass
    
    or as:

        @extends(action='resize')
        def _action_resize(...):
            pass
    """

    def decorator(func):
        # Store enough information to find what we're extending
        func.wsgi_extends = (func.__name__, kwargs.get('action'))
        return func
    
    # If we have positional arguments, call the decorator
    if args:
        return decorator(*args)
    
    # Ok, return the decorator instead
    return decorator


class ControllerMetaclass(type):
    """Controller metaclass.

    This metaclass automates the task of assembling a dictionary
    mapping action keys to method names.

    """

    def __new__(mcs, name, bases, cls_dict):
        """Adds the wsgi_actions dictionary to the class."""

        # Find all actions
        actions = {}
        extensions = []
        # Start with wsgi actions from base classes
        for base in bases:
            actions.update(getattr(base, 'wsgi_actions', {}))
        for key, value in cls_dict.items():
            if not callable(value):
                continue
            if getattr(value, 'wsgi_action', None):
                actions[value.wsgi_action] = key
            elif getattr(value, 'wsgi_extends', None):
                extensions.append(value.wsgi_extends)
            
        # Add the actions and extensions to the class dict
        cls_dict['wsgi_actions'] = actions
        cls_dict['wsgi_extensions'] = extensions

        return super(ControllerMetaclass, mcs).__new__(mcs, name, bases,
                                                       cls_dict)


@six.add_metaclass(ControllerMetaclass):
class Controller(object):
    """Default controller."""

    _view_builder_class = None

    def __init__(self, view_builder=None):
        """Initialize controller with a view builder instance."""
        if view_builder:
            self._view_builder = view_builder
        elif self._view_builder_class:
            self._view_builder = self._view_builder_class()
        else:
            self._view_builder = None
    
    @staticmethod
    def is_valid_body(body, entity_name):
        if not (body and entity_name in body):
            return False
        
        def is_dict(d):
            try:
                d.get(None)
                return True
            except AttributeError:
                return False
        
        if not is_dict(body[entity_name]):
            return False
        
        return True


class Fault(webob.exc.HTTPException):
    """Wrap webob.exc.HTTPException to provide API friendly response."""

    _fault_names = {
        400: "badRequest",
        401: "unauthorized",
        403: "forbidden",
        404: "itemNotFound",
        405: "badMethod",
        409: "conflictingRequest",
        413: "overLimit",
        415: "badMediaType",
        501: "notImplemented",
        503: "serviceUnavailable"
    }

    def __init__(self, exception):
        """Create a Fault for the given webob.exc.exception."""
        self.wrapped_exc = exception
        self.status_int = exception.status_int
    
    @webob.dev.wsgify(RequestClass=Request)
    def __call__(self, req):
        """Generate a WSGI response based on the exception passed to code."""
        # Replace the body with fault details
        code = self.wrapped_exc.status_int
        fault_name = self._fault_names.get(code, "computeFault")
        fault_data = {
            fault_name: {
                'code': code,
                'message': self.wrapped_exc.explanation
            }
        }
        if code == 413:
            retry = self.wrapped_exc.headers
            fault_data[fault_name]['retryAfter'] = retry
        
        content_type = req.best_match_content_type()
        serializer = {
            'application/json': JSONDeserializer(),
        }[content_type]

        self.wrapped_exc.body = serializer.serialize(fault_data)
        self.wrapped_exc.content_type = content_type
        _set_request_id_header(req, self.wrapped_exc.headers)

        return self.wrapped_exc
    
    def __str__(self):
        return self.wrapped_exc.__str__()
    


def _set_request_id_header(req, headers):
    context = req.environ.get('soil.context')
    if context:
        headers['x-compute-request-id'] = context.request_id


class OverLimitFault(webob.exc.HTTPException):
    """Rate-limited request response."""

    def __init__(self, message, details, retry_time):
        """Initialize new `OverLimitFault` with relevant information."""
        headers = OverLimitFault._retry_after()
    
    @staticmethod
    def _retry_after(retry_time):
        delay = int(math.ceil(retry_time - time.time()))
        retry_after = delay if delay > 0 else 0
        headers = {'Retry-After': '%d' % retry_after}
        return headers
    
    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, request):

        content_type = request.best_match_content_type()

        serializer = {
            'application/json': JSONDeserializer(),
        }[content_type]

        content = serializer.serialize(self.content)
        self.wrapped_exc.body = content

        return self.wrapped_exc
