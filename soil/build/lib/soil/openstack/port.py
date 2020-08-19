# Copyright 2020 Soil, Inc.

from soil.openstack.base import SourceBase

class Port(SourceBase):
    """A class for openstack port"""

    def __init__(self, plugin, source_id):
        super(Port, self).__init__(plugin, source_id)
    
    def get_security_groups(self):
        from soil.openstack.security_group import SecurityGroup
        response_data = self.plugin.neutron.get_port(self.source_id)
        return [SecurityGroup(self.plugin, security_group_id) for security_group_id in response_data['port']['security_groups']]

    def update_security_groups(self, security_groups):
        security_group_ids = [security_group for security_group in security_groups]
        self.plugin.neutron.update_port(self.source_id, security_group_ids)
