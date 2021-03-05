# Copyright 2020 Soil, Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""Soil base exception handling.

Includes decorator for re-raising Soil-type exceptions.

SHOULD include dedicated exception logging.

"""

import sys
import json

from oslo_config import cfg
from oslo_log import log as logging
import six
import webob.exc
from webob import util as woutil
from webob.util import status_generic_reasons
from webob.util import status_reasons

from soil.i18n import _, _LE, _LI, _LW


LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='Make exception message format errors fatal.'),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


class ConvertedException(webob.exc.WSGIHTTPException):
    """Converted Exception"""

    def __init__(self, code=500, title="", explanation=""):
        self.code = code
        # There is a strict rule about constructing status line for HTTP:
        # '...Status-Line, consisting of the protocol version followed by a
        # numeric status code and its associated textual phrase, with each
        # element separated by SP characters'
        # (http://www.faqs.org/rfcs/rfc2616.html)
        # 'code' and 'title' can not be empty because they correspond
        # to numeric status code and its associated text
        if title:
            self.title = title
        else:
            try:
                self.title = status_reasons[self.code]
            except KeyError:
                msg = _LE("Improper or unknown HTTP status code used: %d")
                LOG.error(msg, code)
                self.title = woutil.status_generic_reasons[self.code // 100]
        self.explanation = explanation
        super(ConvertedException, self).__init__()


class Error(Exception):
    pass


class RequestException(Exception):
    """ Base Request Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property.
    """

    def __init__(self, code, message):
        self.code = code
        super(Exception, self).__init__(
            json.dumps({'code': code, 'message': message}))


class SoilException(Exception):
    """ Base Soil Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        self.kwargs['message'] = message

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        for k, v in self.kwargs.items():
            if isinstance(v, Exception):
                self.kwargs[k] = six.text_type(v)

        if self._should_format():
            try:
                message = self.message % kwargs
            except Exception:
                exc_info = sys.exc_info()
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception(_('Exception in string format operation'))
                for name, value in kwargs.items():
                    LOG.error(_LE('%(name)s: %(value)s',
                                  {'name': name, 'value': value}))
                if CONF.fatal_exception_format_errors:
                    six.reraise(*exc_info)
                # at least get the core message out if something happened
                message = self.message
        elif isinstance(message, Exception):
            message = six.text_type(message)

        # NOTE(luisg): We put the actual message in 'msg' so that we can access
        # it, because if we try to access the message via 'message' it will be
        # overshadowed by the class' message attribute
        self.msg = message
        super(SoilException, self).__init__(message)

    def _should_format(self):
        return self.kwargs['message'] is None or '%(message)' in self.message

    # NOTE(tommylikehu): This method can be used to
    # translate translatable variables (Mesage object here), do not
    # wrap it with str(), unicode(), six.text_type().
    def __unicode__(self):
        return self.msg


class HttpException(Exception):
    """A class for http exception"""

    def __init__(self, code, message=None):
        self.code = code
        super(HttpException, self).__init__(
            json.dumps({'code': code, 'message': message}))


class TimeoutHttpException(HttpException):
    """A class for http timeout exception"""

    def __init__(self, code=None, message=None):
        if not code:
            # code is 408 means Request Timeout
            code = 408

        if not message:
            message = _LW("Wait Time Out")
        super(TimeoutHttpException, self).__init__(code=code, message=message)


class Invalid(SoilException):
    message = _("Unacceptable paraneters.")
    code = 400


class InvalidContentType(Invalid):
    message = _("Invalid content type %(content_type)s.")


class InvalidInput(Invalid):
    message = _("Invalid input received: %(reason)s")


class MalformedRequestBody(SoilException):
    message = _("Malformed message body: %(reason)s")


class NotAuthorized(SoilException):
    message = _("Not Authorized.")
    code = 403


class NotFound(SoilException):
    message = _("Resource could not be found.")
    code = 404
    safe = True


class ConfigNotFound(NotFound):
    message = _("Could not find config at %(path)s")


class PasteAppNotFound(NotFound):
    message = _("Could not load paste app '%(name)s' from %(path)s")


class ServiceNotFound(NotFound):

    def __init__(self, message=None, **kwargs):
        if not message:
            if kwargs.get('host', None):
                self.message = _("Service %(service_id)s could not be "
                                 "found on host %(host)s.")
            else:
                self.message = _("Service %(service_id)s could not be found.")
        super(ServiceNotFound, self).__init__(message, **kwargs)


class LicenseExc(ConvertedException):
    def __init__(self, code=593, title="", exception=""):
        self.code = code
        if title:
            self.title = title
        else:
            try:
                self.title = woutil.status_reasons[self.code]
            except KeyError:
                msg = _LE("Improper or unknown HTTP status code: %d")
                LOG.error(msg, code)
                self.title = woutil.status_generic_reasons[self.code // 100]
        self.explanation = explanation
        super(ConvertedException, self).__init__()
