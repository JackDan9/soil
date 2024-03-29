# Copyright 2020 Soil, Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# Copyright 2012 Red Hat, Inc.
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
#    under the License

from oslo_config import cfg
from oslo_log import log as logging

import soil.conf
from soil import rpc
from soil import version
from soil.db.sqlalchemy import api as sqlalchemy_api

CONF = soil.conf.CONF
# logging.register_options(CONF)


def parse_args(argv, default_config_files=None, configure_db=True, init_rpc=True):
    CONF(argv[1:],
         project='soil',
         version=version.version_string(),
         default_config_files=default_config_files)

    if init_rpc:
        rpc.init(CONF)

    if configure_db:
        pass
        # sqlalchemy_api.configure(CONF)
