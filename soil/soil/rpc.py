# Copyright 2020 Soil, Inc.
# Copyright 2013 Red Hat, Inc.
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

import six

from oslo_config import cfg
import oslo_messaging as messaging
from oslo_messaging.rpc import dispatcher
from oslo_serialization import jsonutils

import soil.conf
import soil.exception
import soil.context
from soil.i18n import _, _LI, _LW, _LI


__all__ = [
    'init',
    'cleanup',
    'set_defaults',
    'add_extra_exmods',
    'clear_extra_exmods',
    'get_allowed_exmods',
    'RequestContextSerializer',
    'get_client',
    'get_server',
    'get_notifier',
]


CONF = soil.conf.CONF

TRANSPORT = None
NOTIFICATION_TRANSPORT = None
NOTIFIER = None

ALLOWED_EXMODS = [
    soil.exception.__name__,
]
EXTRA_EXMODS = []


def init(conf):
    global TRANSPORT, NOTIFICATION_TRANSPORT, NOTIFIER
    exmods = get_allowed_exmods()
    TRANSPORT = create_transport(get_transport_url())
    NOTIFICATION_TRANSPORT = messaging.get_notification_transport(
        conf, allowed_remote_exmods=exmods)
    serializer = RequestContextSerializer(JsonPayloadSerializer())
    NOTIFIER = messaging.Notifier(
        NOTIFICATION_TRANSPORT,
        serializer=serializer)


def cleanup():
    global TRANSPORT, NOTIFICATION_TRANSPORT, NOTIFIER
    assert TRANSPORT is not None
    assert NOTIFICATION_TRANSPORT is not None
    assert NOTIFIER is not None
    TRANSPORT.cleanup()
    NOTIFICATION_TRANSPORT.cleanup()
    TRANSPORT = NOTIFICATION_TRANSPORT = NOTIFIER = None


def set_defaults(control_exchange):
    messaging.set_transport_defaults(control_exchange)


def add_extra_exmods(*args):
    EXTRA_EXMODS.extend(args)


def clear_extra_exmods():
    del EXTRA_EXMODS[:]


def get_allowed_exmods():
    return ALLOWED_EXMODS + EXTRA_EXMODS


class JsonPayloadSerializer(messaging.NoOpSerializer):
    @staticmethod
    def fallback(obj):
        """Serializer fallback

        This method is used to serialize an object which jsonutils.to_primitive
        does not otherwise know how to handle.

        This is mostly only needed in tests because of the use of the soil
        CreatingSeializer fixture which keeps some non-serializable fields
        on the RequestContext, like db_connection.
        """
        if isinstance(obj, soil.context.RequestContext):
            # This matches RequestContextSerializer.serialize_context()
            return obj.to_dict()
        return six.text_type(obj)

    def serialize_entity(self, context, entity):
        return jsonutils.to_primitive(entity, convert_instances=True)


class RequestContextSerializer(messaging.Serializer):

    def __init__(self, base):
        self._base = base

    def serialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.serialize_entity(context, entity)

    def deserialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.deserialize_entity(context, entity)

    def serialize_context(self, context):
        return context

    def deserialize_context(self, context):
        return context


def get_transport_url(url_str=None):
    return messaging.TransportURL.parse(CONF, url_str)


def get_client(target, version_cap=None, serializer=None):
    assert TRANSPORT is not None

    serializer = RequestContextSerializer(serializer)

    return messaging.RPCClient(TRANSPORT,
                               target,
                               version_cap=version_cap,
                               serializer=serializer)


def get_server(target, endpoints, serializer=None):
    assert TRANSPORT is not None

    serializer = RequestContextSerializer(serializer)
    access_policy = dispatcher.DefaultRPCAccessPolicy
    return messaging.get_rpc_server(TRANSPORT,
                                    target,
                                    endpoints,
                                    executor='eventlet',
                                    serializer=serializer,
                                    access_policy=access_policy)


def get_notifier(service, host=None, publisher_id=None):
    assert NOTIFIER is not None
    if not publisher_id:
        publisher_id = "%s.%s" % (service, host or CONF.host)
    return NOTIFIER.prepare(publisher_id=publisher_id)


def get_versioned_notifier(publisher_id):
    assert NOTIFIER is not None
    return NOTIFIER.prepare(publisher_id=publisher_id)


def create_transport(url):
    exmods = get_allowed_exmods()
    return messaging.get_rpc_transport(CONF,
                                       url=url,
                                       allowed_remote_exmods=exmods)
