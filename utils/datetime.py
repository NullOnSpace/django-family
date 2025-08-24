from datetime import datetime, date, time
from typing import Tuple
from zoneinfo import ZoneInfo

from django.conf import settings


def get_local_date(dt: datetime) -> date:
    return dt.astimezone(tz=ZoneInfo(settings.TIME_ZONE)).date()


def get_range_of_date(dt: date) -> Tuple[datetime, datetime]:
    tz = ZoneInfo(settings.TIME_ZONE)
    return (
        datetime.combine(dt, time.min, tz),
        datetime.combine(dt, time.max, tz),
    )