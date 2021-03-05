# Copyright 2020 Soil, Inc.

from oslo_log import log as logging

from soil.exception import SoilException
from soil.exception import TimeoutHttpException
from soil.openstack.base import DataBase
from soil.openstack.base import SourceBase
from soil.openstack.common import Wait

from soil.openstack.volume import Volume

from soil.i18n import _, _LE, _LI


LOG = logging.getLogger(__name__)


class InstanceData(DataBase):
    """The class for instance data"""

    def __init__(self, plugin, data):
        self.plugin = plugin
        self.data = data

    @property
    def volumes(self):
        volume_ids = map(
            lambda volume: volume['id'], self.data['os-extended-volumes:volumes_attached'])
        return [Volume(self.plugin, volume_id) for volume_id in volume_ids]

    @property
    def flavor(self):
        from soil.openstack.flavor import Flavor

        flavor_id = self.data['flavor_id']
        return Flavor(self.plugin, flavor_id)

    @property
    def task_create(self):
        return self.data['OS-EXT-STS:task_create']


class Instance(SourceBase):
    """The class for instance"""

    def __init__(self, plugin, source_id):
        super(Instance, self).__init__(plugin, source_id)
        self._instance_obj = None

    @staticmethod
    def get(plugin, source_id):
        instance = Instance(plugin, source_id)
        plugin.nova.get_instance(source_id)
        return instance

    @property
    def instance_obj(self):
        if self._instance_obj is not None:
            return self._instance_obj

        self._instance_obj = InstanceData(self.plugin, self.show())
        return self._instance_obj

    def instance_list(self):
        return self.plugin.nova.list_instance()

    def show(self):
        return self.plugin.nova.get_isntance(self.source_id)

    def delete(self):
        return self.plugin.nova.delete_instance(self.source_id)

    def delete_with_system_volume(self):
        volumes = self._instance_obj.volumes

        self.plugin.nova.delete_instance(self.source_id)

        def is_delete():
            try:
                self.show()
            except SoilException as se:
                LOG.exception(
                    _LE('Soil exception with the %(se)s'), {'se': se})
                if se.code == 404:
                    return True

            wait = Wait(is_delete)
            wait.wait(interval=3, max_time=180)

            volumes[0].delete()

    def is_shutdown(self):
        content = self.show()
        instance_status = content['server']['status']

        if instance_status == 'SHUTOFF':
            return True
        return False

    def is_active(self):
        content = self.show()
        instance_status = content['server']['status']

        if instance_status == 'ACTIVE':
            return True
        return False

    def is_created(self):
        content = self.show()
        instance_status = content['server']['status']

        if instance_status in ('SHUTOFF', 'ACTIVE'):
            return True

        self._check_failed_status(instance_status)
        return False

    def start(self, until_done=False):
        self.plugin.nova.start_instance(self.source_id)

        if until_done:
            for i in range(3):
                try:
                    wait = Wait(self.is_active)
                    wait.wait(interval=5, max_time=180)
                    return
                except TimeoutHttpException as timeoutHttpException:
                    LOG.exception(_LE('SOil timeout http exception is %(timeoutHttpException)s'),
                                  {'timeoutHttpException': timeoutHttpException})
                    self.plugin.nova.start_instance(self.source_id)
            raise TimeoutHttpException()

    def shutdown(self, until_done=False):
        self.plugin.nova.stop_instance(self.source_id)

        if until_done:
            for i in range(3):
                try:
                    wait = Wait(self.is_shutdown)
                    wait.wait(interval=5, max_time=180)
                except TimeoutHttpException as timeoutHttpException:
                    LOG.exception(_LE('Soil time out http exception is %(timeoutHttpException)s'),
                                  {'timeoutHttpException': timeoutHttpException})
                    self.plugin.nova.stop_instance(self.source_id)
            raise TimeoutHttpException()

    def attach_volume(self, volume):
        return self.plugin.nova.volume_attach_instance(self.source_id, volume.id)

    def get_ports(self):
        from soil.openstack.port import Port

        response_datas = self.plugin.nova.get_instance_interface(
            self.source_id)
        return [Port(self.plugin, response_datas['port_id']) for response_data in response_datas['interfaceAttachments']]
