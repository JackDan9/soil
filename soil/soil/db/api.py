# Copyright 2020 Soil, Inc.
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

"""Defines interface for DB access.

Functions in this module are imported into the nova.db namespace. Call these
functions from nova.db namespace, not the nova.db.api namespace.

All functions in this module return objects that implement a dictionary-like
interface. Currently, many of these objects are sqlalchemy objects that
implement a dictionary interface. However, a future goal is to have all of
these objects be simple dictionaries.

"""
import threading

from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db import options
from oslo_db.sqlalchemy import session as db_session
from oslo_db import concurrency
from oslo_log import log as logging

from soil.db import models
from soil.db.models import BASE
import soil.conf
from soil.db import constants

CONF = soil.conf.CONF

# NOTE(cdent): These constants are re-defined in this module to preserve
# existing references to them.
# MAX_INT = constants.MAX_INT
# SQL_SP_FLOAT_MAX = constants.SQL_SP_FLOAT_MAX

# _BACKEND_MAPPING = {'sqlalchemy': 'soil.db.sqlalchemy.api'}

# IMPL = concurrency.TpoolDbapiWrapper(CONF, backend_mapping=_BACKEND_MAPPING)

LOG = logging.getLogger(__name__)


options.set_defaults(CONF, connection='mysql+pymysql://root:secret@localhost/soil')


_LOCK = threading.Lock()
_FACADE = None


def _create_facade_lazily():
    global _LOCK
    with _LOCK:
        global _FACADE
        if _FACADE is None:
            _FACADE = db_session.EngineFacade(
                CONF.database.connection,
                **dict(CONF.database)
            )
        return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def dispose_engine():
    get_engine().dispose()


def is_user_context(context):
    """Indicates if the request context is a normal user."""
    if not context:
        return False
    if context.is_admin:
        return False
    if not context.user_id or not context.project_id:
        return False
    return True


def register_models():
    # NOTE()
    engine = get_engine()
    BASE.metadata.create_all(engine)


def unregister_models():
    engine = get_engine()
    BASE.metadata.drop_all(engine)


def model_query(context, model, *args, **kwargs):
    """Query helper that accounts for context's `read_deleted` field.

    :param context: context to query under
    :param session: if present, the session to use
    :param read_deleted: if present, overrides context's read_deleted field.
    """
    session = kwargs.get('session') or get_session()
    read_deleted = kwargs.get('read_deleted') or context.read_deleted

    query = session.query(model, *args)

    if read_deleted == 'no':
        query = query.filter_by(deleted=False)
    elif read_deleted == 'yes':
        pass  # omit the filter to include deleted and active
    elif read_deleted == 'only':
        query = query.filter_by(deleted=True)
    elif read_deleted == 'int_no':
        query = query.filter_by(deleted=0)
    else:
        raise Exception(
            _("Unrecognized read_deleted value '%s'") % read_deleted)

    return query


###################


def vcenter_get_by_uuid(uuid):
    session = get_session()
    query = session.query(models.vCenter)
    vcenter = query.filter_by(uuid=uuid).first()
    return vcenter


def vcenter_get_all():
    session = get_session()
    vcenters = session.query(models.vCenter).all()
    return vcenters


def vcenter_create(uuid, name, vcenter_type, host, port, username, password, status):
    session = get_session()
    vcenter_models = models.vCenter(uuid=uuid,
                                    name=name,
                                    vcenter_type=vcenter_type,
                                    host=host,
                                    port=port,
                                    username=username,
                                    password=password,
                                    status=status)
    try:
        with session.begin():
            session.add(vcenter_models)
    except db_exc.DBDuplicateEntry:
        raise
    except Exception:
        raise
    return vcenter_models


def vcenter_update_by_uuid(uuid, **kwargs):
    session = get_session()
    with session.begin():
        query = session.query(models.vCenter)
        vcenter = query.filter_by(uuid=uuid).first()
        vcenter.name = kwargs['name']
        vcenter.vcenter_type = kwargs['vcenter_type']
        vcenter.host = kwargs['host']
        vcenter.port = kwargs['port']
        vcenter.username = kwargs['username']
        vcenter.password = kwargs['password']
        vcenter.status = kwargs['status']
    return vcenter


def vcenter_delete_by_uuid(uuid):
    session = get_session()
    with session.begin():
        vcenter = session.query(models.vCenter).filter_by(uuid=uuid)
        if vcenter is not None:
            vcenter.delete()


###################


def vcenter_log_get(limit=10):
    session = get_session()
    query = session.query(models.vCenterLog)
    log = query.limit(limit).all()
    return log


def vcenter_log_get_all():
    session = get_session()
    log = session.query(models.vCenterLog).all()
    return log


def vcenter_log_create(**kw):
    session = get_session()
    log_models = models.vCenterLog(name=kw.get('name'),
                                   vcenter_type=kw.get('vcenter_type'),
                                   hostname=kw.get('hostname'),
                                   action=kw.get('action'),
                                   status=kw.get('status'),
                                   resource=kw.get('resource'),
                                   res_type=kw.get('res_type'),
                                   res_operator=kw.get('res_operator'),
                                   res_op_action=kw.get('res_op_action'))
    try:
        with session.begin():
            session.add(log_models)
    except Exception:
        raise
    return log_models


##################


def license_get():
    session = get_session()
    query = session.query(models.VmwareLicense)
    license = query.all()
    try:
        return license[0]
    except IndexError:
        return license


def license_create(**kw):
    session = get_session()
    license_models = models.VmwareLicense(license=kw.get('license'))
    try:
        with session.begin():
            session.add(license_models)
    except Exception:
        raise
    return license_models


def license_update(**kw):
    session = get_session()
    with session.begin():
        query = session.query(models.VmwareLicense)
        license = query.all()[0]
        license.license = kw.get('license')
        license.expired = kw.get('expired')
    return license
