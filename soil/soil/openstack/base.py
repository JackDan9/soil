# Copyright 2020 Soil, Inc.

from oslo_log import log as logging
from soil.i18n import _, _LI, _LE, _LW


LOG = logging.getLogger(__name__)


class DataBase(object):
    """A class for DataBase"""

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            LOG.error(_LW("'%(classname)s' object has no attribute '%(name)s'"),
                      {"classname": self.__class__.__name__, "name": name})
            raise AttributeError("'%(classname)s' object has no attribute '%(name)s'",
                                 {"classname": self.__class__.__name__, "name": name})


class SourceBase(object):
    """A class for Source Base"""

    def __init__(self, plugin, source_id):
        self.plugin = plugin
        self.source_id = source_id

    @classmethod
    def get_type(cls):
        return cls.__name__.lower()

    def get_source_id(self):
        return self.source_id

    def delete(self):
        pass

    def _check_failed_status(self, status):
        if status.upper() in ('ERROR', ):
            LOG.error(_LW("%(type)s %(source_id)s is ERROR"),
                      {"type": self.get_type(), "source_id": self.source_id})

            raise Exception("%(type)s %(source_id)s is ERROR",
                            {"type": self.get_type(), "source_id": self.source_id})
