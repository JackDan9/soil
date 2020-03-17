# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
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

"""Implementation of SQLAlchemy backend."""

from oslo_db.sqlalchemy import enginefacade
from oslo_log import log as logging
from oslo_utils import importutils

import soil.conf

profiler_sqlalchemy = importutils.try_import('osprofiler.sqlalchemy')

CONF = soil.conf.CONF


LOG = logging.getLogger(__name__)

main_context_manager = enginefacade.transaction_context()
# api_context_manager = enginefacade.transaction_context()


def _get_db_conf(conf_group, connection=None):
    kw = dict(conf_group.items())
    if connection is not None:
        kw['connection'] = connection
    return kw 


def configure(conf):
    main_context_manager.configure(**_get_db_conf(conf.database))
    # api_context_manager.configure(**_get_db_conf(conf.api_database))

    if profiler_sqlalchemy and CONF.profiler.enabled and CONF.profiler.trace_sqlalchemy:

        main_context_manager.append_on_engine_create(
            lambda eng: profiler_sqlalchemy.add_tracing(sa, eng, "db"))
        # api_context_manager.append_on_engine_create(
            # lambda eng: profiler_sqlalchemy.add_tracing(sa, eng, "db"))
        
    