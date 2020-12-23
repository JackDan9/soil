class VMwareEx(Exception):
    pass


class vCenterNotConnect(VMwareEx):
    pass


class vCenterPropertyNotExist(VMwareEx):
    def __init__(self, object_type):
        self.message = ("referenced type %s in property specification "
                        "does not exist, \nconsult the managed object type "
                        "reference in the vSphere API documentation" % 
                        object_type)
    
    def __str__(self):
        return self.message
