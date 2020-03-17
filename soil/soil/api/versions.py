# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import copy

from soil.api import extensions
from soil.api import server
from soil.api.server import wsgi
from soil.api.views import versions as views_versions

_KNOWN_VERSIONS = {
    "v1.0": {
        "id": "v1.0",
        "status": "SUPPORTED",
        "version": "",
        "updated": "2017-06-20T20:20:00Z",
    },
}


class Versions(server.APIRouter):
    """Route versions requests."""
    ExtensionManager = extensions.ExtensionManager

    def _setup_routes(self, mapper):
        self.resources['versions'] = create_resource()
        mapper.connect('versions', '/',
                       controller=self.resources['versions'],
                       action='all')
        mapper.redirect('', '/')


class VersionsController(wsgi.Controller):

    def __init__(self):
        super(VersionsController, self).__init__(None)

    @wsgi.response(300)
    def all(self, req):
        """Return all known versions."""
        builder = views_versions.get_view_builder(req)
        known_versions = copy.deepcopy(_KNOWN_VERSIONS)
        return builder.build_versions(known_versions)

    def index(self, req):
        builder = views_versions.get_view_builder(req)
        known_versions = copy.deepcopy(_KNOWN_VERSIONS)
        return builder.build_versions(known_versions)


def create_resource():
    return wsgi.Resource(VersionsController())
