# Copyright 2020 Soil, Inc.
# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Piston Cloud Computing, Inc.
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
"""
SQLAlchemy models for nova data.
"""

from oslo_config import cfg
from oslo_log import log as logging
from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy import String
from sqlalchemy import Text

LOG = logging.getLogger(__name__)


CONF = cfg.CONF

BASE = declarative_base()


def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')


class SoilBase(models.TimestampMixin,
               models.ModelBase):

    metadata = None

    def __copy__(self):
        """Implement a safe copy.copy().

        SQLAlchemy-mapped objects travel with an object
        called an InstanceState, which is pegged to that object
        specifically and tracks everything about that object.  It's
        critical within all attribute operations, including gets
        and deferred loading. This object definitely cannot be
        shared among two instances, and must be handled.

        The copy routine here makes use of session.merge() which
        already essentially implements a "copy" style of operation,
        which produces a new instance with a new InstanceState and copies
        all the data along mapped attributes without using any SQL.

        The mode we are using here has the caveat that the given object
        must be "clean", e.g. that it has no database-loaded state
        that has been updated and not flushed.   This is a good thing,
        as creating a copy of an object including non-flushed, pending
        database state is probably not a good idea; neither represents
        what the actual row looks like, and only one should be flushed.

        """
        session = orm.session()

        copy = session.merge(self, load=False)
        session.expunge(copy)
        return copy

# class License(BASE, SoilBase, models.SoftDeleteMixin):
