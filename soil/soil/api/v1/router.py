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

import functools
import six

from soil.api import extensions
from soil.api import server
from soil.api.server import wsgi
from soil.api import versions
from soil.api.v1.openstack.compute import instances
from soil.api.v1.openstack.network import networks
from soil.api.v1.vmware.vcenter import vcenter


def _create_controller(main_controller, action_controller_list):
    """This is a helper method to create controller with a
    list of action controller.
    """

    controller = wsgi.Resource(main_controller())
    for ctl in action_controller_list:
        controller.register_actions(ctl())
    return controller


version_controller = functools.partial(_create_controller, 
    versions.VersionsController, [])

instances_controller = functools.partial(_create_controller,
    instances.InstancesController, [])

networks_controller = functools.partial(_create_controller, 
   networks.NetworksController,  [])

vcenter_controller = functools.partial(_create_controller,
    vcenter.vCenterController, [])


ROUTE_LIST = (
    ('', '/'),
    ('/', {
        'GET': [version_controller, 'all']
    }),
    ('/versions', {
        'GET': [version_controller, 'index']
    }),
    ('/osp/instances', {
        'GET': [instances_controller, 'index'],
        'POST': [instances_controller, 'create'],
    }),
    ('/osp/networks', {
        'POST': [networks_controller, 'create'],
    }),
    ('/vmware/vcenter', {
        'GET': []
    })
)


class APIRouter(server.APIRouter):
    ExtensionManager = extensions.ExtensionManager

    def _setup_routes(self, mapper):
        for path, methods in ROUTE_LIST:
            if isinstance(methods, six.string_types):
                mapper.redirect(path, methods)
                continue
            
            for method, controller_info in methods.items():
                controller = controller_info[0]()
                action = controller_info[1]
                mapper.create_route(path, method, controller, action)
