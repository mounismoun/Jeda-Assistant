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


def current_time_context(timezone_name: str | None = None) -> str:
    timezone = resolve_timezone(timezone_name)
    now = datetime.now(timezone)
    return f"{now.strftime('%Y-%m-%d %H:%M:%S')} ({timezone.key})"


def human_current_time_context(timezone_name: str | None = None) -> str:
    timezone = resolve_timezone(timezone_name)
    now = datetime.now(timezone)
    return f"{humanize_datetime(now, timezone_name)} ({timezone.key})"


def humanize_datetime_text(value: str, timezone_name: str | None = None) -> str:
    text = value.strip()
    for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, pattern)
        except ValueError:
            continue
        timezone = resolve_timezone(timezone_name)
        return humanize_datetime(parsed.replace(tzinfo=timezone), timezone_name)
    return value


def humanize_datetime(value: datetime, timezone_name: str | None = None) -> str:
    timezone = resolve_timezone(timezone_name)
    dt = value.astimezone(timezone) if value.tzinfo else value.replace(tzinfo=timezone)
    today = datetime.now(timezone).date()
    date = dt.date()
    if date == today:
        date_label = "오늘"
    elif (date - today).days == 1:
        date_label = "내일"
    elif (date - today).days == -1:
        date_label = "어제"
    else:
        date_label = dt.strftime("%Y년 %m월 %d일")

    hour = dt.hour
    minute = dt.minute
    period = "오전" if hour < 12 else "오후"
    display_hour = hour % 12 or 12
    if minute == 0:
        time_label = f"{period} {display_hour}시"
    else:
        time_label = f"{period} {display_hour}시 {minute}분"
    return f"{date_label} {time_label}"
