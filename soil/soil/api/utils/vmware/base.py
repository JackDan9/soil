# Copyright 2020 Soil, Inc.

import time

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from oslo_log import log as logging

from soil.api.utils.vmware.hybrid import HybridCloud
from soil.api.utils.vmware.common import parse_propspec
from soil.api.utils.vmware.serviceutil import build_full_traversal


LOG = logging.getLogger(__name__)


def _connect_failed(*args, **kwargs):
    _user, _pwd = args[3:5] if len(args) > 4 \
        else (kwargs.get('user', None), kwargs.get('pwd', None))
    LOG.error("Cloud not connect to the specified host using specified "
              "username(%s) and password(%s)" % (_user, _pwd))


class VMwareCloud(HybridCloud):
    """vmware cloud base class

    Initialize a connection to a vcenter or vsphere.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.si = None

    def connect(self):
        try:
            self.si = connect.SmartConnectNoSSL(*self.args, **self.kwargs)
        except Exception:
            try:
                self.si = connect.SmartConnect(*self.args, **self.kwargs)
            except Exception:
                pass
        finally:
            if self.si is None:
                _connect_failed(*self.args, **self.kwargs)

    def disconnect(self):
        if self.si:
            connect.Disconnect(self.si)
            self.si = None


class vCenterBase(VMwareCloud):
    def __init__(self, vcenter=None, *args, **kwargs):
        if vcenter is None:
            super(vCenterBase, self).__init__(*args, **kwargs)
        else:
            super(vCenterBase, self).__init__(
                host=vcenter.host,
                port=int(vcenter.port),
                user=vcenter.username,
                pwd=vcenter.password
            )

    def get_container_view(self, container, object_type=None, recursive=True):
        """Returns the container view of specified object type

        :param container: ManagedEntity object
        A reference to an instance of a Folder, Datacenter, ComputeResource,
        ResourcePool or HostSystem object.
        :param object_type: List
        An optional list of managed entity types.
        The server associates only objects of the specified type(s) with the view.
        If you specify an empty array, the server uses all types.
        :param recursive: Boolean
            When True, include only the immediate children of the container instance.
            When False, include additional objects by following paths beyond the immediate children.
        :return: Container view


        usage:
            # list all container instance under rootFolder by recursive
            view = self.get_container_view(si.content.rootFolder, [])

            # list only immediate children under rootFolder
            view = self.get_container_view(si.content.rootFolder, [], False)

            # list all container instance of ComputeResource under rootFolder by recursive
            view = self.get_container_view(si.content.rootFolder, [vim.ComputeResource]

            # list all container instance of ComputeResource and Network under rootFolder by recursive
            view = self.get_container_view(si.content.rootFolder, [vim.ComputeResource, vim.Network])

            # list all container instance under Datacenter by recursive
            datacenterFolder = si.content.rootFolder.childEntity[0]
            view = self.get_container_view(datacenterFolder, [])


        relations:
                        rootFolder
                            |
                            |
               |-------------------------|
               |                         |
          Datacenter1                Datacenter2
                                         |
                                         |
                        ---------------------------------------
                        |           |          |              |
                datastoreFolder  hostFolder  networkFolder  vmFolder
        """
        if self.si is None:
            return

        container = self.si.content.viewManager.CreateContainerView(
            container, object_type, recursive
        )
        view = container.view
        container.Destroy()
        return view

    def get_container_view_by_id(self, container, object_type=None, id=None, recursive=True):
        if self.si is None:
            return

        container = self.si.content.viewManager.CreateContainerView(
            container, object_type, recursive
        )
        children = container.view
        container.Destroy()
        for child in children:
            current = child._GetMoId()
            if (current == id):
                return child

    def create_filter_spec(self, objs, props):
        """Returns the filterSpec

        :param objs: the managed object sets at which the filter begins to collect properties
        :param props: the properties need to be query
        """
        objSpecs = []
        propSpecs = []
        traversal = build_full_traversal()
        for obj in objs:
            objSpec = vmodl.query.PropertyCollector.ObjectSpec(obj=obj,
                                                               selectSet=traversal)
            objSpecs.append(objSpec)
        for motype, proplist in props:
            # :param all: boolean
            # Specifies whether or not all properties of the object are read.
            # If this property is set to true, the 'pathSet' property is ignored.
            propSpec = vmodl.query.PropertyCollector.PropertySpec(all=False,
                                                                  type=motype,
                                                                  pathSet=proplist)
            propSpecs.append(propSpec)
        filterSpec = vmodl.query.PropertyCollector.FilterSpec(objectSet=objSpecs,
                                                              propSet=propSpecs)
        return filterSpec

    def collect_object_property(self, objs, props, maxObjects=None):
        """ Retrieve properties of objs using PropertyCollector managed object

        :param objs: The objects will be query
        :param props: The properties of objects need to be query
        :param maxObjects: The maximum number of ObjectContent data objects that should be
        returned in a single result from RetrievePropertiesEx
        """
        if self.si is None:
            return

        pc = self.si.content.propertyCollector
        filterSpec = self.create_filter_spec(objs, props)
        options = vmodl.query.PropertyCollector.RetrieveOptions(maxObjects=maxObjects)
        result = pc.RetrievePropertiesEx([filterSpec], options)

        # because the maximum number of objects retrieved by RetrievePropertiesEx and
        # ContinueRetrievePropertiesEx is limit to 100, so, we need to continue retrieve
        # properties using token
        def _continue(token=None):
            _result = pc.ContinueRetrievePropertiesEx(token)
            _token = _result.token
            _objects = _result.objects
            if _token is not None:
                _objects_ex = _continue(_token)
                _objects.extend(_objects_ex)
            return _objects

        if result is None:
            return {}

        token = result.token
        objects = result.objects
        if token is not None:
            _objects = _continue(token)
            objects.extend(_objects)

        return objects

    def get_obj(self, content, vimtype, name):
        """
        :param content:
        :param vimtype:
        :param name:
        :return:
        Get the vsphere object associated with a given text name
        """
        obj = None
        if self.si is None:
            return
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj

    def wait_for_task(self, task, actionName='job', hideResult=False):
        """
        Waits and provides updates on a vSphere task
        :param task:
        :param actionName:
        :param hideResult:
        :return:
        """

        while task.info.state not in [vim.TaskInfo.State.success,
                                      vim.TaskInfo.State.error]:
            time.sleep(2)

        if task.info.state == vim.TaskInfo.State.success:
            if task.info.result is not None and not hideResult:
                out = '%s completed successfully, result: %s' % (actionName, task.info.result)
                print(out)
            else:
                out = '%s completed successfully.' % actionName
                print(out)

        else:
            out = '%s did not complete successfully: %s' % (actionName, task.info.error)
            print(out)

        return task.info.result


class vCenterSmartConnect(vCenterBase):
    """Smart connect to vcenter

    reutrn a vcenter instance, instance contains some useful common method.
    the connection to vcenter will be destroied automate after operation.

    useage:
        smart_connect_to_vcenter = vCenterSmartConnect(vcenter)
        with smart_connect_to_vcenter as vCenter:
            si = vCenter.si
            ...
    """
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class vCenterPropertyCollector(vCenterBase):
    """collect designation properties of vcenter object

    using Managed-object 'ProertyCollector' to retrieve properties
    """
    def __init__(self, vcenter, object_type, properties):
        super(vCenterPropertyCollector, self).__init__(vcenter)
        self._object_type = object_type
        self._properties = properties

    def __enter__(self):
        self.connect()
        result = self._collect(self._object_type, self._properties)
        return result

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _collect(self, object_type, properties):
        si = self.si
        if si is None:
            return {}

        result = dict(content=si.content)
        container = si.content.rootFolder
        objs = self.get_container_view(container, object_type)
        props = parse_propspec(properties)
        try:
            objects = self.collect_object_property(objs, props)
        except vmodl.query.InvalidProperty:
            raise
        for obj in objects:
            key = obj.obj
            value = dict()
            for prop in obj.propSet:
                value.update({prop.name: prop.val})
            result.update({key: value})
        return result
