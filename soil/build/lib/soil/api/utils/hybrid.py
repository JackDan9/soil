# Copyright 2020 Soil, Inc.

import six
from abc import ABCMeta
from abc import abstractmethod


@six.add_metaclass(ABCMeta)
class HybridCloud(object):
    """Abstract class for hybrid cloud
    
    All cloud platform should provide connect and disconnect to it, VMware, aliyun, eg.
    """
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
