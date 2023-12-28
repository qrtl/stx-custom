# Copyright 2022 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime

import pytz

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


def convert_datetime_tz(date_time, tz_from, tz_to):
    if isinstance(date_time, str):
        date_time = datetime.strptime(date_time, DATETIME_FORMAT)
    if isinstance(tz_from, str):
        tz_from = pytz.timezone(tz_from)
    if isinstance(tz_to, str):
        tz_to = pytz.timezone(tz_to)
    return tz_from.localize(date_time).astimezone(tz_to).replace(tzinfo=None)


def convert_datetime_to_utc(date_time, tz_from=None):
    if tz_from is None:
        tz_from = date_time.tzinfo
    if not tz_from:
        return date_time
    return convert_datetime_tz(date_time, tz_from, "UTC")


def convert_datetime_from_utc(date_time, tz_to=None):
    if tz_to is None:
        tz_to = date_time.tzinfo
    if not tz_to:
        return date_time
    return convert_datetime_tz(date_time, "UTC", tz_to)
