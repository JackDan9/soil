# Copyright 2020 Soil, Inc.

import time

from oslo_log import log as logging

from soil.exception import TimeoutHttpException
from soil.db.sqlalchemy import api as db_api
from soil.i18n import _, _LI, _LW, _LE


LOG = logging.getLogger(__name__)


class Wait(object):
    """A class for wait"""

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def wait(self, interval=5, exc=TimeoutHttpException(), max_time=300, func_exc_max_times=3):
        start_time = time.time()
        func_exc_times = 0

        while True:
            try:
                if self.func(*self.args, **self.kwargs):
                    db_api.db_session()
                    return True
            except Exception as ex:
                LOG.exception(_LE('Soil Exception %(ex)s'), 
                              {'ex': ex})
                
                if func_exc_times >= func_exc_max_times:
                    raise ex
                
                func_exc_times = func_exc_times + 1
            
            if time.time() - start_time > max_time:
                db_api.dispose_engine()
                
                LOG.exception(_LE('Soil exc exception %(exc)s'), 
                              {"exc": exc})
                
                raise exc
            
            time.sleep(5)
