# Copyright 2020 Soil, Inc.

from soil.exception import RequestException
from soil.openstack.base import SourceBase


class Image(SourceBase):
    """A class for openstack image"""

    def __init__(self, plugin, source_id):
        super(Image, self).__init__(plugin, source_id)

    def is_created(self):
        image_info = self.show()
        status = image_info['image']['status']
        if status in ('ACTIVE', ):
            return True
        self._check_failed_status(status)
        return False

    def is_delete(self):
        try:
            image_info = self.show()
            status = image_info['image']['status'].upper()
            if status in ('DELETED', 'DELETING'):
                return True
            self._check_failed_status(status)
        except RequestException as re:
            if re.code == 404:
                return True
        return False

    def show(self):
        return self.plugin.nova.get_image(self.source_id)

    def delete(self):
        if self.is_delete():
            return True
        return self.plugin.nova.delete_image(self.source_id)

    def create_instance(self, name, flavor_id, volume_size, net_ids):
        from soil.openstack.instance import Instance

        response_data = self.plugin.nova.volumes_boot(
            name, flavor_id, 'image', self.source_id, volume_size, net_ids)
        return Instance(self.plugin, response_data['server']['id'])

    def create_volume(self, volume_size, display_name, display_description, volume_type=None):
        from soil.openstack.volume import Volume

        response_data = self.plugin.cinder.create_volume(
            volume_size, display_name, display_description, self.source_id, volume_type)
        return Volume(self.plugin, response_data['volume']['id'])
