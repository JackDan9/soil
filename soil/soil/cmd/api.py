# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Starter script for Soil API.

Starts the VMware and Openstack APIs in separate greenthreads.

"""

import sys


import eventlet
from oslo_config import cfg
from oslo_log import log as logging
from oslo_reports import opts as gmr_opts

# Need to register global_opts
from soil import config
from soil import service

CONF = cfg.CONF
logging.register_options(CONF)


def main():
    gmr_opts.set_defaults(CONF)
    config.parse_args(sys.argv)
    logging.setup(CONF, 'soil')
    eventlet.monkey_patch()

    launcher = service.process_launcher()
    server = service.WSGIService('soil-api')
    launcher.launch_service(server, workers=server.workers or 1)
    launcher.wait()
