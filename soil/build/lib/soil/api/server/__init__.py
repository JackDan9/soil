# Copyright 2020 Soil, Inc.
# Copyright 2011 OpenStack Foundation
#
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

"""
WSGI middleware for API controllers
"""

from oslo_log import log as logging
from oslo_service import wsgi as base_wsgi
import routes

from soil.api.server import wsgi 
from soil.i18n import _, _LI, _LW, _LE


LOG = logging.getLogger(__name__)


class APIMapper(routes.Mapper):
    def routematch(self, url=None, environ=None):
        if url is "":
            result = self._match("", environ)
            return result[0], result[1]
        return routes.Mapper.routematch(self, url, environ)
    
    def connect(self, *args, **kwargs):
        # Note(jackdan): Default the format part of a route to only accept json
        # so it doesn't eat all characters after a '.'
        # in the url.
        kwargs.setdefault('requirements', {})
        if not kwargs['requirements'].get('format'):
            kwargs['requirements']['format'] = 'json'
        return routes.Mapper.connect(self, *args, **kwargs)
    

class ProjectMapper(APIMapper):
    def resource(self, member_name, collection_name, **kwargs):
        if not ('parent_resource' in kwargs):
            kwargs['path_prefix'] = '{project_id}/'
        else:
            parent_resource = kwargs['parent_resource']
            p_collection = parent_resource['collection_name']
            p_member = parent_resource['member_name']
            kwargs['path_prefix'] = '{project_id}/%s/:%s_id' % (p_collection, p_member)
        
        routes.Mapper.resource(self, 
                               member_name,
                               collection_name,
                               **kwargs)

    def create_route(self, path, method, controller, action):
        self.connect(path,
                     conditions=dict(method=[method]),
                     controller=controller,
                     action=action)


class APIRouter(base_wsgi.Router):
    """
    Routes requests on the API to the appropriate controller and method.
    """

    ExtensionManager = None # override the subclasses

    @classmethod
    def factory(cls, global_config, **local_config):
        """
        Simple paste factory, :class:`soil.wsgi.Router` doesn't have.
        """
        return cls()
    
    def __init__(self, ext_mgr=None):
        if ext_mgr is None:
            if self.ExtensionManager:
                ext_mgr = self.ExtensionManager()
            else:
                raise Exception(_LE("Must specify an ExtensionManager class"))
        
        mapper = ProjectMapper()
        self.resources = {}
        self._setup_routes(mapper)
        self._setup_ext_routes(mapper, ext_mgr)
        self._setup_extensions(ext_mgr)
        super(APIRouter, self).__init__(mapper)
    
    def _setup_ext_routes(self, mapper, ext_mgr):
        for resource in ext_mgr.get_resources():
            LOG.debug("Extended resources: %s", resource.collection)

            wsgi_resource = wsgi.Resource(resource.controller)
            self.resources[resource.collection] = wsgi_resource
            kwargs = dict(
                controller=wsgi_resource,
                collection=resource.collection_actions,
                member=resource.member_actions)
            
            if resource.parent:
                kwargs['parent_resource'] = resource.parent
            
            mapper.resource(resource.collection, resource.collection, **kwargs)

            if resource.custom_routes_fn:
                resource.custom_routes_fn(mapper, wsgi_resource)
            
    def _setup_extensions(self, ext_mgr):
        for extension in ext_mgr.get_controller_extensions():
            collection = extension.collection
            controller = extension.controller

            if collection not in self.resources:
                LOG.warning(_LW('Extension %(ext_name)s: Cannot extend '
                                'resource %(collection)s: No such resource',
                                {'ext_name': extension.extension.name,
                                 'collection': collection}))
                continue
            
            LOG.debug('Extension %(ext_name)s extending resource: '
                      '%(collection)s',
                      {'ext_name': extension.extension.name,
                       'collection': collection})
            
            resource = self.resources[collection]
            resource.register_actions(controller)
            resource.register_extensions(controller)

    def _setup_routes(self, mapper):
        raise NotImplementedError
