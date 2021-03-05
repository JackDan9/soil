# Copyright 2020 Soil, Inc.

from dateutil import tz
from datetime import datetime, timedelta

from oslo_log import log as logging
from soil.exception import SoilException
from soil.i18n import _, _LI


LOG = logging.getLogger(__name__)


def transfer_datetime(utc_datetime):
    """Change the source datetiem to the localtime"""

    from_datetime_zone = tz.gettz('UTC')
    to_datetime_zone = tz.gettz('CST')

    utc_datetime = datetime.strptime(utc_datetime, "%Y-%m-%dT%H:%M:%SZ")

    utc = utc_datetime.replace(tzinfo=from_datetime_zone)

    cst_datetime_zone = utc.astimezone(to_datetime_zone)

    cst_datetime = datetime.strftime(cst_datetime_zone, "%Y-%m-%d %H:%M:%S")

    LOG.info(_LI("Localtime %(utc_datetime)s to update destination time %(cst_datetime)s"),
             {"utc_datetime": utc_datetime, "cst_datetime": cst_datetime})

    return cst_datetime
