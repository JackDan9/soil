# Copyright 2020 Soil, Inc.

import uuid
import webob
import six
from six.moves import http_client

from soil.api.server import wsgi
from soil.api.utils.vmware.base import vCenterSmartConnect
from soil.api.views.vmware import vcenter as vcenter_view
from soil.api.v1.license.rsa_license import check_provider_nums
from soil.db import api as db_api


class vCenterController(wsgi.Controller):
    """The vCenter API controller for the Soil API"""

    _view_builder_class = vcenter_view.ViewBuilder

    def __init__(self):
        super(vCenterController, self).__init__()

    def index(self, req):
        return self._vcenter_get(req)
    
    def show(self, req, vcenter_id):
        return self._vcenter_get_by_uuid(req, vcenter_id)
