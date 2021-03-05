# Copyright 2020 Soil, Inc.

import rbd
import rados

from soil.openstack.base import SourceBase
from soil.exception import RequestException


class CephImage(SourceBase):
    """A class for ceph image"""

    def __init__(self, plugin, source_id, pool=None, size=None):
        super(CephImage, self).__init__(plugin, source_id)
        self.conf = plugin.ceph_conf_path  # CONF.ceph_conf_path
        self.pool = pool
        self.size = size
        if not self.pool or not self.size:
            pass

    @staticmethod
    def get_from_volume(volume):
        image_id = str('volume-%s' % volume.id)

        with rados.Rados(conffile=volume.plugin.ceph_conf_path) as cluster:
            for pool in cluster.list_pools():
                with cluster.open_ioctx(pool) as ioctx:
                    if image_id in rbd.RBD().list(ioctx):
                        with rbd.Image(ioctx, image_id) as image:
                            return CephImage(volume.plugin, image_id, pool=pool, size=image.size())

        raise RequestException(code=404, message="")

    def delete(self):
        with rados.Rados(conffile=self.conf) as cluster:
            with cluster.open_ioctx(self.pool) as ioctx:
                rbd.RBD().remove(ioctx, self.source_id)

    def create_empty(self):
        with rados.Rados(conffile=self.conf) as cluster:
            with cluster.open_ioctx(self.pool) as ioctx:
                rbd.RBD().create(ioctx, self.source_id, size=self.size)
