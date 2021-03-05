# Copyright 2020 Soil, Inc.

import base64
import time
import calendar
from dateutil import tz
from datetime import datetime

from oslo_log import log as logging

from soil.openstack.instance import Instance
from soil.plugin.openstack import OpenstackPlugin


class ViewBuilder(object):
    """A class for openstack instance"""

    def __init__(self):
        super(ViewBuilder, self).__init__()

    def _instance_list(self, req, body):
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

        instances = source_plugin.nova.get_list_instance()['servers']

        return {"instances": instances}
