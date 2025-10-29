"""Time and timezone utilities for Drupal Aggregator."""
from datetime import datetime, timedelta
from typing import Optional
import pytz
from dateutil import parser as date_parser


def get_timezone(tz_name: str = "Europe/Athens") -> pytz.tzinfo.BaseTzInfo:
    """Get timezone object."""
    return pytz.timezone(tz_name)


def now_in_tz(tz_name: str = "Europe/Athens") -> datetime:
    """Get current time in specified timezone."""
    tz = get_timezone(tz_name)
    return datetime.now(tz)


def days_ago(days: int, tz_name: str = "Europe/Athens") -> datetime:
    """Get datetime N days ago in specified timezone."""
    tz = get_timezone(tz_name)
    return now_in_tz(tz_name) - timedelta(days=days)


def parse_date(date_string: str, tz_name: str = "Europe/Athens") -> Optional[datetime]:
    """Parse date string and localize to timezone."""
    try:
        dt = date_parser.parse(date_string)
        if dt.tzinfo is None:
            tz = get_timezone(tz_name)
            dt = tz.localize(dt)
        else:
            tz = get_timezone(tz_name)
            dt = dt.astimezone(tz)
        return dt
    except (ValueError, TypeError):
        return None


def is_within_timeframe(
    date_obj: datetime,
    since: datetime,
    tz_name: str = "Europe/Athens"
) -> bool:
    """Check if date is within timeframe."""
    if date_obj.tzinfo is None:
        tz = get_timezone(tz_name)
        date_obj = tz.localize(date_obj)
    return date_obj >= since


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """Format datetime object."""
    return dt.strftime(fmt)


def get_iso_timestamp(tz_name: str = "Europe/Athens") -> str:
    """Get current ISO formatted timestamp."""
    return now_in_tz(tz_name).isoformat()


def get_period_label(days: int) -> str:
    """
    Get human-readable period label based on number of days.

    Args:
        days: Number of days in the period

    Returns:
        Period label (e.g., "Daily", "Weekly", "Biweekly", "Monthly", "14-Day")

    Examples:
        >>> get_period_label(1)
        'Daily'
        >>> get_period_label(7)
        'Weekly'
        >>> get_period_label(14)
        'Biweekly'
        >>> get_period_label(10)
        '10-Day'
    """
    if days == 1:
        return "Daily"
    elif days == 7:
        return "Weekly"
    elif days == 14:
        return "Biweekly"
    elif days == 21:
        return "Triweekly"
    elif days == 28 or days == 30 or days == 31:
        return "Monthly"
    else:
        return f"{days}-Day"
