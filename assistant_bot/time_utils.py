from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Seoul"


def resolve_timezone(timezone_name: str | None) -> ZoneInfo:
    try:
        return ZoneInfo((timezone_name or DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def now_in_timezone(timezone_name: str | None = None) -> datetime:
    return datetime.now(resolve_timezone(timezone_name))


def today_string(timezone_name: str | None = None) -> str:
    return now_in_timezone(timezone_name).strftime("%Y-%m-%d")
