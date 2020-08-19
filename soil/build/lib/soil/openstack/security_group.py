# Copyright 2020 Soil, Inc.

from soil.openstack.base import DataBase
from soil.openstack.base import SourceBase


class SecurityGroupData(DataBase):
    """A class for openstack security group data"""

    def __init__(self, data):
        self.data = data['security_group']


class SecurityGroup(SourceBase):
    """A class for openstack security group"""

    def __init__(self, plugin, source_id):
        super(SecurityGroup, self).__init__(plugin, source_id)
        self._security_group_obj = None
    
    @property
    def security_group_obj(self):
        if self._security_group_obj is not None:
            return self._security_group_obj
        self._security_group_obj = SecurityGroupData(self.show())
        return self._security_group_obj
    
    @staticmethod
    def get(plugin, source_id):
        security_group = SecurityGroup(plugin, source_id)
        plugin.neutron.get_security_group(source_id)
        return security_group
    
    @staticmethod
    def create(plugin, name):
        response_data = plugin.neutron.create_security_group(name)
        return SecurityGroup(plugin, response_data['security_group']['id'])
    
    def show(self):
        return self.plugin.neutron.get_security_group(self.source_id)
    
    def delete(self):
        return self.plugin.neutron.delete_security_group(self.source_id)
    
    def delete_all_rules(self):
        security_group_rules = self.show()['security_group']['security_group_rules']
        for security_group_rule in security_group_rules:
            self.plugin.neutron.delete_security_group_rule(security_group_rule['id'])
    
    def create_rule(self, other_rule):
        self.plugin.neutron.create_security_group_rule(
            security_group_id = self.source_id,
            direction=other_rule['direction'],
            ethertype=other_rule['ethertype'],
            port_range_max=other_rule['port_range_max'],
            port_range_min=other_rule['port_range_min'],
            protocol=other_rule['protocol'],
            remote_group_id=other_rule['remote_group_id'],
            remote_group_prefix=other_rule['remote_ip_prefix']
        )
