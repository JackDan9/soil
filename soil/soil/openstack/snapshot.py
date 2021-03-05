# Copyright 2020 Soil, Inc.

from soil.openstack.base import DataBase
from soil.openstack.base import SourceBase


class SnapshotData(DataBase):
    """A class for openstack snapshot data"""

    def __init__(self, data):
        self.data = data['snapshot']


class Snapshot(SourceBase):
    """A class for openstack snapshot"""

    def __init__(self, plugin, source_id):
        super(Snapshot, self).__init__(plugin, source_id)
        self._snapshot_obj = None

    @property
    def snapshot_obj(self):
        if self._snapshot_obj is not None:
            return self._snapshot_obj

        self._snapshot_obj = SnapshotData(self.show())
        return self._snapshot_obj

    def show(self):
        return self.plugin.cinder.show_snapshot(self.source_id)

    def delete(self):
        self.plugin.cinder.delete_snapshot(self.source_id)

    def is_created(self):
        snapshot_info = self.show()
        status = snapshot_info['snapshot']['status']
        if status in ('available', ):
            return True

        self._check_failed_status(status)
        return False

    def is_delete(self):
        pass
