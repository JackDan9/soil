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

"""
This is the single point of entry to generate the sample configuration
file for Soil. It collects all the necessary info from the other modules
in this package. It is assumed that:
* every other module in this package has a 'list_opts' function which
  return a dict where
  * the keys are strings which are the group names
  * the value of each key is a list of config options for that group
* the soil.conf package doesn't have further packages with config options
* this module is only used in the context of sample file generation
"""

import copy
import itertools

from soil.api.middleware import auth
from soil.api import extensions
from soil.engine import manager
from soil.wsgi import server
from soil import service


def list_opts():
    """Entry point for oslo-config-generator."""
    return [('DEFAULT', itertools.chain(
        copy.deepcopy(auth.auth_opts),
        copy.deepcopy(extensions.extension_opts),
        copy.deepcopy(manager.engine_opts),
        copy.deepcopy(server.wsgi_opts),
        copy.deepcopy(service.service_opts)))]
