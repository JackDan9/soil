# Copyright 2020 Soil, Inc.

from soil.exception import RequestException
from soil.utils.request import post_request, get_request, delete_request

SNAPSHOTS_URL = '/snapshots'
SNAPSHOTS_DETAIL_URL = '/snapshots/details'
SNAPSHOT_URL = '/snapshots/{snapshot_id}'

VOLUMES_URL = '/volumes'
VOLUMES_DETAIL_URL = '/volumes/details'
VOLUME_ACTION_URL = '/volume/{volume_id}/action'


TYPES_URL = '/types'


class CinderPlugin(object):
    """A class for openstack cinder plugin"""

    def __init__(self, host_url, openstack):
        self.host_url = host_url
        self.openstack = openstack
        self._snapshots_url = self.host_url + SNAPSHOTS_URL
        self._snapshots_detail_url = self.host_url + SNAPSHOTS_DETAIL_URL
        self._snapshot_url = self.host_url + SNAPSHOT_URL
        self._volumes_url = self.host_url + VOLUMES_URL
        self._volumes_detail_url = self.host_url + VOLUMES_DETAIL_URL
        self._volume_action_url = self.host_url + VOLUME_ACTION_URL
        self._types_url = self.host_url + TYPES_URL
    
    @property
    def openstack_user_token(self):
        return self.openstack.openstack_user_token
    
    def show_volumes(self):
        volumes_url = self._volumes_url
        return get_request(url=volumes_url, token=self.openstack_user_token)

    def show_volume(self, volume_id):
        volume_url = self._volumes_url.format(volume_id=volume_id)
        return get_request(url=volume_url, token=self.openstack_user_token)
    
    def create_volume(self, size, display_name=None, display_description=None, image_id=None, volume_type=None):
        data = {
            "volume": {
                "status": "creating",
                "availability_zone": None,
                "source_volid": None,
                "display_description": display_description,
                "snapshot_id": None,
                "user_id": None,
                "size": size,
                "display_name": display_name,
                "imageRef": image_id,
                "attach_status": "detached",
                "volume_type": volume_type,
                "project_id": None,
                "metadata": {}
            }
        }

        return post_request(self._volumes_url, data, self.openstack_user_token)
    
    def delete_volume(self, volume_id):
        volume_url = self._volumes_url.format(volume_id=volume_id)
        return delete_request(volume_url, self.openstack_user_token)
    
    def show_snapshots(self):
        snapshots_url = self._snapshots_url
        return get_request(snapshots_url, self.openstack_user_token)

    def show_snapshot(self, snapshot_id):
        snapshot_url = self._snapshot_url.format(snapshot_id=snapshot_id)
        return get_request(snapshot_url, self.openstack_user_token)
    
    def create_snapshot_from_volume(self, volume_id):
        data = {
            "snapshot": {
                "display_name": "hamal-volume-%s" % volume_id,
                "force": "True",
                "display_description": None,
                "volume_id": volume_id
            }
        }

        return post_request(self._snapshot_url, data, self.openstack_user_token)
    
    def delete_snapshot(self, snapshot_id):
        snapshot_url = self._snapshot_url.format(snapshot_id=snapshot_id)
        return delete_request(snapshot_url, self.openstack_user_token)
    
    def create_another_env_image(self, volume_id, image_name, glance_ip, glance_port, glance_token, container_format, disk_format):
        data = {
            "os-volume_upload_image": {
                "glance_ip": glance_ip,
                "glance_use_ssl": "0",
                "force": "True",
                "glance_version": "1",
                "container_format": container_format,
                "disk_format": disk_format,
                "image_name": image_name,
                "glance_token": glance_token,
                "glance_port": glance_port
            }
        }

        volume_url = self._volume_action_url.format(volume_id=volume_id)
        return post_request(volume_url, data, self.openstack_user_token)
    
    def set_volume_bootable(self, volume_id, bootable):
        data = {
            "os-set_bootable": {
                "bootable": bootable
            }
        }

        volume_url = self._volume_action_url.format(volume_id=volume_id)
        return post_request(volume_url, data, self.openstack_user_token, no_resp_content=True)
    
    def set_volume_status(self, volume_id, status):
        data = {
            "os-reset_status": {
                "status": status
            }
        }

        volume_url = self._volume_action_url(volume_id=volume_id)
        return post_request(volume_url, data, self.openstack_user_token, no_resp_content=True)
    
    def show_volume_types(self):
        return get_request(self._types_url, self.openstack_user_token)
