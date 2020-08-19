# Copyright 2020 Soil, Inc.

from soil.openstack.base import SourceBase


class Network(SourceBase):
    """A class for openstack network"""

    def __init__(self, plugin, source_id):
        super(Network, self).__init__(plugin, source_id)
    
    @staticmethod
    def get(plugin, source_id):
        network = Network(plugin, source_id)
        plugin.neutron.get_network(source_id)
        return network
    
    @staticmethod
    def get_external(plugin):
        networks = plugin.neutron.get_networks()['networks']
        external_networks = filter(lambda n: n['router:external'], networks)
        return [Network(plugin, external_network['id']) for external_network in external_networks]

    def show(self):
        return self.plugin.neutron.get_network(self.source_id)
    
    def create_floating_ip(self, ip, port):
        from soil.openstack.floatingip import Floatingip

        response_data = self.plugin.neutron.create_floatingip(self.source_id, ip, port.source_id)
        return Floatingip(self.plugin, response_data['floatingip']['id'])
