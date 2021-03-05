# Copyright 2020 Soil, Inc.

from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Boolean
from sqlalchemy import Column, DateTime, String, Integer, schema
from sqlalchemy.ext.declarative import declarative_base


BASE = declarative_base()
ARGS = {'mysql_charset': "utf8"}


class SoilDBBase(models.TimestampMixin,
                 models.ModelBase):

    deleted_at = Column(DateTime)
    deleted = Column(Boolean, default=False)
    metadata = None

    @staticmethod
    def delete_values():
        return {'deleted': True,
                'deleted_at': timeutils.utcnow()}

    def delete(self, session):
        """Delete this object."""
        updated_values = self.delete_values()
        self.update(updated_values)
        self.save(session=session)
        return updated_values


class VmwareLicense(BASE):
    """License table for vmware vcenter"""

    __tablename__ = 'vmware_license'

    id = Column(Integer, primary_key=True)
    license = Column(String(2048))
    expired = Column(Boolean, default=False)
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, default=timeutils.utcnow,
                        onupdate=timeutils.utcnow)


class OpenStackLicense(BASE):
    """License table for openstack"""

    __tablename__ = 'openstack_license'

    id = Column(Integer, primary_key=True)
    license = Column(String(2048))
    expired = Column(Boolean, default=False)
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, default=timeutils.utcnow,
                        onupdate=timeutils.utcnow)


class vCenter(BASE, SoilDBBase):
    """Auth table for vcenter"""

    __tablename__ = 'vcenter'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False)
    name = Column(String(255), unique=True)
    vcenter_type = Column(String(64))
    host = Column(String(64), unique=True)
    port = Column(String(32))
    username = Column(String(255))
    password = Column(String(255))
    status = Column(String(32))
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, default=timeutils.utcnow,
                        onupdate=timeutils.utcnow)


class vCenterLog(BASE, SoilDBBase):
    """Operation log list for vcenter"""

    __tablename__ = 'vcenter_log'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))  # provider name
    vcenter_type = Column(String(64))  # provider type
    hostname = Column(String(255))  # provider host
    action = Column(String(32))  # provider action
    status = Column(String(32))  # provider status
    resource = Column(String(64))  # resource name
    res_type = Column(String(64))  # resource type
    res_operator = Column(String(64))  # resource operator
    res_op_action = Column(String(64))  # resource operator action
    res_op_at = Column(DateTime, default=timeutils.utcnow,
                       onupdate=timeutils.utcnow)  # resource operate time
    created_at = Column(DateTime, default=timeutils.utcnow),
    updated_at = Column(DateTime, default=timeutils.utcnow)
