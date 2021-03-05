# Copyright 2020 Soil, Inc.
# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# Copyright 2013 Red Hat, Inc.
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
  CLI interface for soil management.
"""

from __future__ import print_function

import sys

import eventlet
from oslo_config import cfg
from oslo_log import log as logging

from soil import config
from soil import service

CONF = cfg.CONF


def main():
    config.parse_args(sys.argv)
    logging.setup(CONF, 'soil')
    eventlet.monkey_patch()

    server = service.Service.create(binary='soil-engine')
    service.serve(server)
    service.wait()
