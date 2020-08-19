# Copyright 2015 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# This package got introduced during the Mitaka cycle in 2015 to
# have a central place where the config options of Nova can be maintained.
# For more background see the blueprint "centralize-config-options"

from oslo_config import cfg

from soil.conf import api
from soil.conf import database
from soil.conf import destination_cluster
from soil.conf import rsa_license
from soil.conf import rpc
from soil.conf import source_cluster

CONF = cfg.CONF


# api.register_opts(CONF)
# database.register_opts(CONF)
destination_cluster.register_opts(CONF)
rsa_license.register_opts(CONF)
rpc.register_opts(CONF)
source_cluster.register_opts(CONF)
