# Copyright 2020 Soil, Inc.
# Utility functions for the vSphere API
# See com.vmware.apputils.vim25.ServiceUtil in the java API.

from pyVmomi import vim, vmodl


def build_full_traversal():
    """
    Builds a traversal spec that will recurse through all objects .. or at
    least I think it does. additions welcome.

    See com.vmware.apputils.vim25.ServiceUtil.buildFullTraversal in the java
    API. Extended bu Sebastian Tello's examples from pysphere to reach networks
    and datastores.
    """