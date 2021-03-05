# Copyright 2020 Soil, Inc.

from soil.exception import HttpException
from soil.openstack.base import SourceBase


class VolumeType(SourceBase):
    """A class for openstack volume type"""

    def __init__(self, plugin, source_id):
        super(VolumeType, self).__init__(plugin, source_id)
        self._volume_type_obj = None

    @staticmethod
    def list_names(plugin):
        volume_types = plugin.cinder.get_volume_types()
        return map(lambda t: t['name'], volume_types['volume_types'])

    @staticmethod
    def check_volume_type(plugin, volume_type):
        if volume_type not in VolumeType.list_names(plugin):
            raise HttpException(
                404, 'volume_type "%s" not found' % volume_type)
