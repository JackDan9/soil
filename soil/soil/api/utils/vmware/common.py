import six
from pyVmomi import vim

from soil.api.utils.vmware.exception import vCenterPropertyNotExist


def sizeof_fmt(num):
    """
    Returns the human readable version if a file size
    Unified conversion of units to GB
    """
    if isinstance(num, (six.integer_types, float)):
        convert_to_GB = 1024.0 * 1024.0 * 1024.0
        num /= convert_to_GB
        return "%3.1f%s" % (num, 'GB')


def parse_propspec(propspec):
    """Parses property specifications

    :param propspec: the property specifications need to be parses,
        '{'VirtualMachine': ['name']}' for example
    :return: a sequence of 2-tuples. each containing a managed object type
    and a list of properties applicable to that type

    useage:
        propspec = {
            'VirtualMachine': ['name'],
            'Datastore': ['name']
        }
        properties = parse_propspec(propspec)
    """
    props = []
    for objtype, objprops in propspec.items():
        motype = getattr(vim, objtype, None)
        if motype is None:
            raise vCenterPropertyNotExist(motype)
        props.append((motype, objprops))
    return props
