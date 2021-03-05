# Copyright 2020 Soil, Inc.

from soil.openstack.base import SourceBase
from soil.openstack.base import DataBase
from soil.openstack.common import Wait


class VolumeData(DataBase):
    """A class for openstack volume data"""

    def __init__(self, data):
        self.data = data['volume']

    @property
    def image_disk_format(self):
        return self.data.get('volume_image_metadata', {}).get('disk_format')

    @property
    def image_container_format(self):
        return self.data.get('volume_image_metadata', {}).get('container_format')


class VolumeDoingLock(object):
    """A class for openstack volume doing lock"""

    def __init__(self, volume):
        self.volume = volume

    def __enter__(self):
        self.volume.set_status('in-use')
        return self

    def __exit__(self, *exc_info):
        self.volume.set_status('available')


class Volume(SourceBase):
    """A class for openstack volume"""

    def __init__(self, plugin, source_id):
        super(Volume, self).__init__(plugin, source_id)
        self._volume_obj = None

    def doing_lock(self):
        return VolumeDoingLock(self)

    @staticmethod
    def get(plugin, source_id):
        volume = Volume(plugin, source_id)
        plugin.cinder.get_volume(source_id)
        return volume

    @staticmethod
    def create(plugin, volume_size, display_name, display_description, volume_type=None):
        response_data = plugin.cinder.create_volume(
            volume_size, display_name, display_description, volume_type=volume_type)
        return Volume(plugin, response_data['volume']['id'])

    @property
    def volume_obj(self):
        if self._volume_obj is not None:
            return self._volume_obj
        self._volume_obj = VolumeData(self.show())
        return self._volume_obj

    def is_created(self):
        volume_info = self.show()
        status = volume_info['volume']['status']
        if status in ('available', ):
            return True
        self._check_failed_status(status)
        return False

    def is_available(self):
        volume_info = self.show()
        status = volume_info['volume']['status']
        if status in ('available', ):
            return True
        self._check_failed_status(status)
        return False

    def is_inuse(self):
        volume_info = self.show()
        status = volume_info['volume']['status']
        if status in ('in-use', ):
            return True
        self._check_failed_status(status)
        return False

    def show(self):
        return self.plugin.cinder.get_volume(self.source_id)

    def delete(self):
        return self.plugin.cinder.delete_volume(self.source_id)

    def create_instance(self, name, flavor_id, volume_size, net_ids):
        from soil.openstack.instance import Instance

        response_data = self.plugin.nova.volumes_boot(
            name, flavor_id, 'volume', self.source_id, volume_size, net_ids)
        return Instance(self.plugin, response_data['server']['id'])

    def create_snapshot(self, until_done=False):
        from soil.openstack.snapshot import Snapshot

        response_data = self.plugin.cinder.create_snapshot_from_volume(
            self.source_id)
        snapshot = Snapshot(self.plugin, response_data['snapshot']['id'])

        if until_done:
            wait = Wait(snapshot.is_created)
            wait.wait(interval=2)

        return snapshot

    def create_another_env_image(self, another_plugin, disk_format=None):
        from soil.openstack.image import Image

        response_data = self.plugin.cinder.create_another_env_image(
            volume_id=self.source_id,
            image_name='soil-%s' % self.source_id,
            glance_ip=another_plugin.glance.port,
            glance_port=another_plugin.glance.port,
            glance_token=another_plugin.glance.token,
            # CONF.DEFAULT_CONTAINER_FORMAT
            container_format=self.volume_obj.image_container_format,
            # CONF.DEFAULT_DISK_FORMAT
            disk_format=disk_format or self.volume_obj.image_disk_format,
        )

        image_id = response_data['os-volume_upload_image']['image_id']
        return Image(another_plugin, image_id)

    def set_bootable(self, bootable):
        self.plugin.cinder.set_volume_bootable(self.source_id, bootable)

    def set_status(self, status='available'):
        self.plugin.cinder.set_volume_bootable(self.source_id, status)

    def set_status_available(self):
        self.set_status('available')

    def set_status_inuse(self):
        self.set_status('in-use')
