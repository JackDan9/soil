# Copyright 2020 Soil, Inc.

import copy

from soil.api import extensions
from soil.api import server
from soil.api.server import wsgi
from soil.api.views import versions as views_versions

_KNOWN_VERSIONS = {
    "v1.0": {
        "id": "v1.0",
        "status": "SUPPORTED",
        "version": "1.0.0",
        "updated": "2020-01-09T20:20:00Z",
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
