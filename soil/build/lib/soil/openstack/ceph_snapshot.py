# Copyright 2020 Soil, Inc.

import rbd
import rados
from oslo_log import log as logging

from soil.openstack.base import SourceBase
from soil.exception import RequestException
from soil.utils.log import get_request_id
from soil.i18n import _, _LI, _LW
import soil.conf


LOG = logging.getLogger(__name__)

CONF = soil.conf.CONF


class CephSnapshot(SourceBase):
    """A class for ceph snapshot"""

    def __init__(self, plugin, source_id, pool=None):
        super(CephSnapshot, self).__init__(plugin, source_id)
        self.pool = pool
        self.conf = plugin.ceph_conf_path # CONF.ceph.ceph_conf_path
        self.ceph_volume_id, self.ceph_snapshot_id = source_id.split('@')
        self.rbd = rbd.RBD()
        if not self.pool:
            pass
    
    @staticmethod
    def get_from_snapshot(snapshot):
        ceph_volume_id = str('volume-%s' % snapshot.obj.volume_id)
        ceph_image_id = str('snapshot-%s' % snapshot.id)
        ceph_snapshot_id = ceph_volume_id + '@' + ceph_image_id

        with rados.Rados(conffile=snapshot.plugin.ceph_conf_path) as cluster:
            for pool in cluster.list_pools():
                with cluster.open_ioctx(pool) as ioctx:
                    if ceph_volume_id in rbd.RBD().list(ioctx):
                        with rbd.Image(ioctx, ceph_volume_id) as image:
                            if ceph_image_id in map(lambda s: s['name'], image.list_snaps()):
                                return CephSnapshot(snapshot.plugin, ceph_snapshot_id, pool=pool)
                        break
        
        LOG.exception(_LW("The CephSnapshot %(ceph_snapshot_id)s could not be found"), 
                      {"h_snapshot_id": ceph_snapshot_id})
        raise RequestException(code=404, message='{"itemNotFound": {"messgae": "The CephSnapshot %s could not be found"}}' % ceph_snapshot_id)
    
    def delete(self):
        with rados.Rados(conffile=self.conf) as cluster:
            with cluster.open_ioctx(self.pool) as ioctx:
                self.rbd.remove(ioctx, self.source_id)
    
    def import_ceph_image(self, ceph_image):
        LOG.info(_LI('[%(request_id)s] Start sync ceph data %(source_id)s to %(ceph_image_source_id)s'), 
                 {"source_id": self.source_id, "ceph_image_source_id": ceph_image.source_id})
        
        with rados.Rados(conffile=self.conf) as src_cluster, rados.Rados(conffile=ceph_image.conf) as desc_cluster:
            with src_cluster.open_ioctx(self.pool) as src_ioctx, desc_cluster.open_ioctx(ceph_image.pool) as dest_ioctx:
                with rbd.Image(src_ioctx, self.ceph_volume_id, self.ceph_snapshot_id) as src_image, rbd.Image(dest_ioctx, ceph_image.source_id) as dest_image:
                    
                    src_size = src_image.size()
                    per_size = CONF.ceph.CEPH_CHUNK_SIZE

                    current_offset = 0
                    empty = '\0' * per_size
                    while True:
                        LOG.info(_LI('[%(request_id)s] %(ceph_image_source_id)s writing chunk at offset %(current_offset)s'), 
                                 {"request_id": get_request_id(), "ceph_image_source_id": ceph_image.source_id, "current_offset": current_offset})
                        
                        if current_offset + per_size < src_size:
                            rem = src_image.read(current_offset, per_size)
                            if rem != empty:
                                dest_image.write(rem, offset=current_offset)
                        else:
                            end_size = src_size - current_offset
                            empty = '\0' * end_size
                            rem = src_image.read(current_offset, end_size)
                            if rem != empty:
                                dest_image.write(rem, offset=current_offset)
                            break
                        current_offset += per_size
        
        LOG.info(_LI('[%(request_id)s] End sync ceph data %(source_id)s to %(ceph_image_source_id)s'), 
                 {"request_id": get_request_id(), "source_id": self.source_id, "ceph_image_source_id": ceph_image.source_id})
