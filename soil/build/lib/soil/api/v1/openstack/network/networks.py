# Copyright 2020 Soil, Inc.

from soil.api.server import wsgi
from soil.api.views.openstack.network import networks as networks_view


class NetworksController(wsgi.Controller):
    """A class for openstack network controller"""

    _view_builder_class = networks_view.ViewBuilder

    def __init__(self):
        super(NetworksController, self).__init__()
    
    def create(self, req, body):
        return self._get_networks_on_openstack(req, body)
    
    # backend resources operation
    def _get_networks_on_openstack(self, req, body):
        return self._view_builder._network_list(req, body)