# Copyright 2020 Soil, Inc.

import base64
import time
import calendar
from dateutil import tz
from datetime import datetime

from oslo_log import log as logging

from soil.openstack.network import Network
from soil.plugin.openstack import OpenstackPlugin


class ViewBuilder(object):
    """A class for openstack network"""

    def __init__(self):
        super(ViewBuilder, self).__init__()
    
    def _network_list(self, req, body):
        auth_url = body['auth_url']
        username = body['username']
        password = body['password']
        tenant_id = body['tenant_id']

        source_auth = {
            'cluster_name': 'source',
            'auth_url': auth_url,
            'username': username,
            'password': password,
            'tenant_id': tenant_id
        }

        source_plugin = OpenstackPlugin(**source_auth)

        networks = source_plugin.neutron.get_networks()['networks']

        return { "networks": networks }