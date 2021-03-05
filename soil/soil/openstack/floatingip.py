# Copyright 2020 Soil, Inc.

from soil.openstack.base import SourceBase


class Floatingip(SourceBase):
    """A class for openstack network floatingip"""

    def __init__(self, plugin, source_id):
        super(Floatingip, self).__init__(plugin, source_id)

    def delete(self):
        self.plugin.neutron.delete_floatingip(self.source_id)
