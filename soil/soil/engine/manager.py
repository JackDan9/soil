# Copyright 2019 Open Source Community, Inc.

import os

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import periodic_task


CONF = cfg.CONF
LOG = logging.getLogger(__name__)

engine_opts = [
    cfg.StrOpt('host',
               help='The host name which engine run on'),
    cfg.IntOpt('check_interval',
               default=-1,
               help='The interval time to check hosts. Set '
                    '-1 to skip periodical task by default.'),
]


CONF.register_opts(engine_opts)
_PID = os.getpid()


class EngineManager(periodic_task.PeriodicTasks):

    def __init__(self, host=None, service_name='soil-engine'):
        if not host:
            host = CONF.host
        self.host = host
        self.service_name = service_name
        super(EngineManager, self).__init__(CONF)

    def periodic_tasks(self, context, raise_on_error=False):
        """Tasks to be run at a periodic interval."""
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    def init_host(self):
        """Hook to do additional manager initialization.

        when one requests the service be started.  This is called before any
        service record is created. Child classes should override this method.
        """
        pass

    def cleanup_host(self):
        """Hook to do cleanup work when the service shuts down.

        Child classes should override this method.
        """
        pass

    # NOTE(gcb) This is just an example showing usage of periodic task.
    @periodic_task.periodic_task(spacing=CONF.check_interval)
    def log_pid(self, context):
        """periodical task for logging pid of the current process"""
        LOG.info('Run soil-engine with pid:%s on host:%s' % (_PID, self.host))
