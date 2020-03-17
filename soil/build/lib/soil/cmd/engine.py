# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""Starter script for Soil Engine.

1. Configuration
Modify configuration in the file `/etc/soil/soil.conf`

2. Run
soil-engine --config-file /etc/soil/soil.conf

"""

import sys


import eventlet
from oslo_log import log as logging

import soil.conf
from soil import config
from soil import service 

CONF = soil.conf.CONF


def main():
    config.parse_args(sys.argv)
    logging.setup(CONF, 'soil')
    eventlet.monkey_patch()

    server = service.Service.create(binary='soil-engine')
    service.serve(server)
    service.wait()
