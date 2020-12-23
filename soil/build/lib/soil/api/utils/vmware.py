# Copyright 2020 Soil, Inc.

import time

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from oslo_log import log as logging

from soil.api.utils.hybrid import HybridCloud
from soil.api.utils.common import parse_propspec
from soil.api.utils.serviceutil import build_full_traversal

