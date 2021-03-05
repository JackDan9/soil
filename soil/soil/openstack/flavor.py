# Copyright 2020 Soil, Inc.

from oslo_log import log as logging

from soil.exception import SoilException
from soil.exception import RequestException
from soil.openstack.base import DataBase
from soil.openstack.base import SourceBase
from soil.i18n import _, _LW, _LE


LOG = logging.getLogger(__name__)


class FlavorData(DataBase):
    """A class for flavor data"""

    def __init__(self, data):
        self.data = data['flavor']

    @property
    def vcpus(self):
        return self.data['vcpus']

    @property
    def disk(self):
        return self.data['disk']

    @property
    def name(self):
        return self.data['name']

    @property
    def rxtx_factor(self):
        return self.data['rxtx_factor']

    @property
    def ram(self):
        return self.data['ram']

    @property
    def swap(self):
        return self.data['swap'] or 0

    @property
    def is_public(self):
        return self.data['OS-FLV-EXT-DATA:is_public']

    @property
    def ephemeral(self):
        return self.data['OS-FLV-EXT-DATA:ephemeral']


class Flavor(SourceBase):
    """A class for openstack flavor"""

    def __init__(self, plugin, source_id):
        super(Flavor, self).__init__(plugin, source_id)
        self._flavor_obj = None

    @staticmethod
    def get(plugin, source_id=None, flavor_name=None):
        if source_id is not None:
            flavor = Flavor(plugin, source_id)
            plugin.nova.get_flavor(source_id)
            return flavor

        if flavor_name is not None:
            flavors = plugin.nova.list_flavor()
            for flavor in flavors['flavors']:
                if flavor['name'] == flavor_name:
                    return Flavor(plugin, flavor['id'])

        LOG.exception(_LE('{"itemNotFound": {"message": "The flavor %(flavor_name)s could not be found.", "code": 404}}'),
                      {"flavor_name": flavor_name})
        raise RequestException(
            code=404, message='{"itemNotFound": {"message": "The flavor %s could not be found.", "code": 404}}' % flavor_name)

    @property
    def flavor_obj(self):
        if self._flavor_obj:
            return self._flavor_obj
        self._flavor_obj = FlavorData(self.show())
        return self._flavor_obj

    def show(self):
        return self.plugin.nova.get_flavor(self.source_id)

    def flavor_list(self):
        return self.plugin.nova.list_flavor()

    def delete(self):
        return self.plugin.nova.delete_flavor(self.source_id)

    def create_another_env_flavor(self, another_plugin):
        flavor_name = 'plugin-%s-%s' % (self.flavor_obj.name, self.source_id)
        try:
            response_data = another_plugin.nova.create_flavor(
                vcpus=self.flavor_obj.vcpus,
                disk=self.flavor_obj.disk,
                name=flavor_name,
                is_public=self.flavor_obj.is_public,
                rxtx_factor=self.flavor_obj.rxtx_factor,
                ephemeral=self.flavor_obj.ephemeral,
                ram=self.flavor_obj.ram,
                swap=self.flavor_obj.swap
            )
            return Flavor(another_plugin, response_data['flavor']['id'])
        except RequestException as re:
            if re.code != 409:
                raise re

            return Flavor.get(another_plugin, flavor_name=flavor_name)
