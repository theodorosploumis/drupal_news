from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple

import pytz
from dateutil import parser


@dataclass(frozen=True)
class TimeWindow:
    start: datetime
    end: datetime

    def contains(self, dt: datetime) -> bool:
        return self.start <= dt <= self.end


def get_time_window(days: int, timezone_name: str) -> TimeWindow:
    tz = pytz.timezone(timezone_name)
    end = datetime.now(tz)
    start = end - timedelta(days=days)
    return TimeWindow(start=start, end=end)


def parse_datetime(value: str, timezone_name: str) -> datetime:
    tz = pytz.timezone(timezone_name)
    dt = parser.parse(value)
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    return dt.astimezone(tz)


def window_contains_string_date(value: str, timezone_name: str, days: int) -> bool:
    window = get_time_window(days, timezone_name)
    dt = parse_datetime(value, timezone_name)
    return window.contains(dt)
