# Copyright 2020 Soil, Inc.

import eventlet
from pyVmomi import vim

from soil.api.utils.common import sizeof_fmt
from soil.api.utils.vmware import vCenterPropertyCollector


class ViewBuilder(object):

    _collection_name = "vcenter"

    def __init__(self):
        super(ViewBuilder, self).__init__()

    def _detail(self, request, vcenter):
        if vcenter is None:
            return {"vcenter": {}}
        # summary = self._summary(vcenter)
        vcenter_ref = {
            "vcenter": {
                'id': vcenter.get('id'),
                'uuid': vcenter.get('uuid'),
                'name': vcenter.get('name'),
                'type': vcenter.get('type'),
                'host': vcenter.get('host'),
                'port': vcenter.get('port'),
                'status': vcenter.get('status'),
                'created_at': vcenter.get('created_at'),
                'updated_at': vcenter.get('updated_at'),
                # 'summary': summary
            }
        }
        return vcenter_ref

    def _list(self, request, vcenters):
        if not vcenters:
            return {"vcenters": []}

        vcenters_list = []

        # the pile acts as a collection of return values from the functions
        # if any exceptions are raised by the function they'll get raised here
        pile = eventlet.GreenPile(len(vcenters))
        for vcenter in vcenters:
            pile.spawn(self._detail, request, vcenter)

        for result in pile:
            try:
                vcenter = result['vcenter']
                vcenters_list.append(vcenter)
            except KeyError:
                pass

        return {"vcenters": vcenters_list}

    # backend private method

    def _summary(self, vcenter):
        summary_ref = {
            'version': '',
            'hostname': '',
            'numVms': 0,
            'numTemplates': 0,
            'numHosts': 0,
            'numEffectiveHosts': 0,
            'numCpus': 0,
            'totalCpuMhz': 0,
            'totalMemory': 0,
            'numCpuCores': 0,
            'numCpuThreads': 0,
            'effectiveCpuMhz': 0,
            'effectiveMemory': 0,
            'dataStore': 0
        }

        object_type = []
        properties = {
            'ComputeResource': ['summary'],
            'HostSystem': ['hardware.cpuInfo.numCpuPackages'],
            'Datastore': ['summary.capacity'],
            'VirtualMachine': ['config.template', 'guest'],
        }
        with vCenterPropertyCollector(vcenter, object_type, properties) as result:
            for key, value in result.items():
                if isinstance(key, str):
                    about = value.about
                    summary_ref['version'] = ' '.join(
                        [about.apiVersion, about.build])
                    continue

                if isinstance(key, vim.ComputeResource):
                    summary = value['summary']
                    summary_ref['numHosts'] += summary.numHosts
                    summary_ref['numEffectiveHosts'] += summary.numEffectiveHosts
                    summary_ref['totalCpuMhz'] += summary.totalCpu
                    summary_ref['totalMemory'] += summary.totalMemory
                    summary_ref['numCpuCores'] += summary.numCpuCores
                    summary_ref['numCpuThreads'] += summary.numCpuThreads
                    summary_ref['effectiveCpuMhz'] += summary.effectiveCpu
                    summary_ref['effectiveMemory'] += summary.effectiveMemory
                    continue

                if isinstance(key, vim.VirtualMachine):
                    template = value.get('config.template', False)
                    guest = value['guest']

                    if template:
                        summary_ref['numTemplates'] += 1
                    else:
                        summary_ref['numVms'] += 1

                    ip_address = [
                        net.ipAddress for net in guest.net if hasattr(net, 'ipAddress')]
                    for ip in ip_address:
                        if vcenter.host in ip:
                            summary_ref['hostname'] = guest.hostName

                    continue

                if isinstance(key, vim.HostSystem):
                    numCpuPackages = value['hardware.cpuInfo.numCpuPackages']
                    summary_ref['numCpus'] += numCpuPackages
                    continue

                if isinstance(key, vim.Datastore):
                    capacity = value['summary.capacity']
                    summary_ref['dataStore'] += capacity

        summary_ref['totalMemory'] = sizeof_fmt(summary_ref['totalMemory'])
        summary_ref['effectiveMemory'] = sizeof_fmt(
            summary_ref['effectiveMemory'])
        summary_ref['dataStore'] = sizeof_fmt(summary_ref['dataStore'])

        return summary_ref
