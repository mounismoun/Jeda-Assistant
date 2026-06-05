from __future__ import annotations

import csv
import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from assistant_bot.stores import WeatherCacheStore


@dataclass(frozen=True)
class WeatherLocation:
    name: str
    aliases: tuple[str, ...]
    nx: int
    ny: int
    land_reg_id: str | None = None
    weather_stn_id: str | None = None


@dataclass(frozen=True)
class ForecastMoment:
    date: str
    time: str
    values: dict[str, str]


@dataclass(frozen=True)
class WeatherReport:
    location: WeatherLocation
    base_date: str
    base_time: str
    moments: tuple[ForecastMoment, ...]
    situation: dict[str, str]
    land_forecast: tuple[dict[str, str], ...]
    cache_events: tuple[str, ...] = ()


class WeatherLocationResolver:
    def __init__(self, *, resource_path: str | Path) -> None:
        self.locations = load_weather_locations(resource_path)

    def resolve(self, text: str) -> WeatherLocation | None:
        normalized = normalize_location_text(text)
        best: tuple[int, WeatherLocation] | None = None
        for location in self.locations:
            names = (location.name, *location.aliases)
            for name in names:
                candidate = normalize_location_text(name)
                if not candidate or candidate not in normalized:
                    continue
                score = len(candidate)
                if best is None or score > best[0]:
                    best = (score, location)
        return best[1] if best else None

    def from_store_item(self, item: dict[str, object]) -> WeatherLocation:
        return WeatherLocation(
            name=str(item["location_name"]),
            aliases=(),
            nx=int(item["nx"]),
            ny=int(item["ny"]),
            land_reg_id=str(item["land_reg_id"]) if item.get("land_reg_id") else None,
            weather_stn_id=str(item["weather_stn_id"]) if item.get("weather_stn_id") else None,
        )


class KmaWeatherProvider:
    BASE_URL = "https://apihub.kma.go.kr/api/typ02/openApi"

    def __init__(
        self,
        *,
        auth_key: str | None,
        timeout_seconds: float,
        cache: WeatherCacheStore,
        cache_ttl_minutes: int,
        timezone: str,
    ) -> None:
        self.auth_key = auth_key
        self.timeout_seconds = timeout_seconds
        self.cache = cache
        self.cache_ttl_minutes = cache_ttl_minutes
        self.timezone = timezone

    def available(self) -> bool:
        return bool(self.auth_key)

    def get_report(self, *, location: WeatherLocation, include_alerts: bool) -> WeatherReport:
        if not self.auth_key:
            raise RuntimeError("KMA_API_AUTH_KEY 환경 변수가 필요합니다.")
        now = datetime.now(ZoneInfo(self.timezone))
        base_date, base_time = latest_vilage_base_datetime(now)
        forecast_payload, forecast_cache = self._request_with_cache(
            path="VilageFcstInfoService_2.0/getVilageFcst",
            params={
                "pageNo": "1",
                "numOfRows": "1000",
                "dataType": "JSON",
                "base_date": base_date,
                "base_time": base_time,
                "nx": str(location.nx),
                "ny": str(location.ny),
            },
        )
        items = extract_kma_items(forecast_payload)
        if not items:
            retry_date, retry_time = latest_vilage_base_datetime(now - timedelta(hours=3))
            forecast_payload, forecast_cache = self._request_with_cache(
                path="VilageFcstInfoService_2.0/getVilageFcst",
                params={
                    "pageNo": "1",
                    "numOfRows": "1000",
                    "dataType": "JSON",
                    "base_date": retry_date,
                    "base_time": retry_time,
                    "nx": str(location.nx),
                    "ny": str(location.ny),
                },
            )
            base_date, base_time = retry_date, retry_time
            items = extract_kma_items(forecast_payload)

        situation: dict[str, str] = {}
        land_forecast: tuple[dict[str, str], ...] = ()
        cache_events = [f"forecast:{forecast_cache}"]
        if include_alerts and location.weather_stn_id:
            situation_payload, situation_cache = self._request_with_cache(
                path="VilageFcstMsgService/getWthrSituation",
                params={
                    "pageNo": "1",
                    "numOfRows": "10",
                    "dataType": "JSON",
                    "stnId": location.weather_stn_id,
                },
            )
            situation = normalize_situation(extract_kma_first_item(situation_payload))
            cache_events.append(f"situation:{situation_cache}")
        if include_alerts and location.land_reg_id:
            land_payload, land_cache = self._request_with_cache(
                path="VilageFcstMsgService/getLandFcst",
                params={
                    "pageNo": "1",
                    "numOfRows": "10",
                    "dataType": "JSON",
                    "regId": location.land_reg_id,
                },
            )
            land_forecast = tuple(normalize_land_item(item) for item in extract_kma_items(land_payload)[:6])
            cache_events.append(f"land:{land_cache}")

        return WeatherReport(
            location=location,
            base_date=base_date,
            base_time=base_time,
            moments=tuple(group_forecast_items(items)[:12]),
            situation=situation,
            land_forecast=land_forecast,
            cache_events=tuple(cache_events),
        )

    def _request_with_cache(self, *, path: str, params: dict[str, str]) -> tuple[dict[str, object], str]:
        cache_key = path + "?" + urllib.parse.urlencode(sorted(params.items()))
        status, cached = self.cache.get(provider="kma", cache_key=cache_key)
        if cached is not None:
            return cached, status
        payload = self._request(path=path, params=params)
        self.cache.save(
            provider="kma",
            cache_key=cache_key,
            response=payload,
            ttl_minutes=self.cache_ttl_minutes,
        )
        return payload, status

    def _request(self, *, path: str, params: dict[str, str]) -> dict[str, object]:
        query = dict(params)
        query["authKey"] = self.auth_key or ""
        url = f"{self.BASE_URL}/{path}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            text = response.read().decode("utf-8", errors="replace")
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise RuntimeError("기상청 API 응답 형식이 올바르지 않습니다.")
        return payload


def load_weather_locations(resource_path: str | Path) -> list[WeatherLocation]:
    path = Path(resource_path)
    rows = read_location_rows(path) if path.exists() else []
    if not rows:
        rows = DEFAULT_LOCATION_ROWS
    return [location_from_row(row) for row in rows]


def read_location_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def location_from_row(row: dict[str, str]) -> WeatherLocation:
    aliases = tuple(alias.strip() for alias in str(row.get("alias", "")).split("|") if alias.strip())
    return WeatherLocation(
        name=str(row["name"]).strip(),
        aliases=aliases,
        nx=int(row["nx"]),
        ny=int(row["ny"]),
        land_reg_id=(str(row.get("land_reg_id") or "").strip() or None),
        weather_stn_id=(str(row.get("weather_stn_id") or "").strip() or None),
    )


def normalize_location_text(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"\s+", "", text)
    return re.sub(r"[^\w가-힣]", "", text)


def latest_vilage_base_datetime(now: datetime) -> tuple[str, str]:
    base_times = ("0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300")
    safe_now = now - timedelta(minutes=15)
    date = safe_now.date()
    hhmm = safe_now.strftime("%H%M")
    for base_time in reversed(base_times):
        if hhmm >= base_time:
            return date.strftime("%Y%m%d"), base_time
    previous = safe_now - timedelta(days=1)
    return previous.strftime("%Y%m%d"), "2300"


def extract_kma_items(payload: dict[str, object]) -> list[dict[str, str]]:
    try:
        items = payload["response"]["body"]["items"]["item"]  # type: ignore[index]
    except Exception:
        return []
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list):
        return []
    return [{str(key): str(value) for key, value in item.items()} for item in items if isinstance(item, dict)]


def extract_kma_first_item(payload: dict[str, object]) -> dict[str, str]:
    items = extract_kma_items(payload)
    return items[0] if items else {}


def group_forecast_items(items: list[dict[str, str]]) -> list[ForecastMoment]:
    grouped: dict[tuple[str, str], dict[str, str]] = {}
    for item in items:
        key = (item.get("fcstDate", ""), item.get("fcstTime", ""))
        if not key[0] or not key[1]:
            continue
        grouped.setdefault(key, {})[item.get("category", "")] = item.get("fcstValue", "")
    return [
        ForecastMoment(date=date, time=time, values=values)
        for (date, time), values in sorted(grouped.items(), key=lambda entry: entry[0])
    ]


def normalize_situation(item: dict[str, str]) -> dict[str, str]:
    return {
        "tmFc": item.get("tmFc", ""),
        "overview": item.get("wfSv1", ""),
        "warning": item.get("wn", ""),
        "pre_warning": item.get("wr", ""),
    }


def normalize_land_item(item: dict[str, str]) -> dict[str, str]:
    return {
        "announceTime": item.get("announceTime") or item.get("tmFc", ""),
        "numEf": item.get("numEf", ""),
        "weather": item.get("wf", ""),
        "temperature": item.get("ta", ""),
        "rain_probability": item.get("rnSt", ""),
        "rain_type": item.get("rnYn", ""),
    }


def default_location_row(
    name: str,
    alias: str,
    nx: int,
    ny: int,
    land_reg_id: str,
    weather_stn_id: str,
) -> dict[str, str]:
    return {
        "name": name,
        "alias": alias,
        "nx": str(nx),
        "ny": str(ny),
        "land_reg_id": land_reg_id,
        "weather_stn_id": weather_stn_id,
    }


DEFAULT_LOCATION_ROWS = [
    default_location_row("서울", "서울특별시|서울시", 60, 127, "11B10101", "109"),
    default_location_row("강남구", "서울강남|서울강남구|강남", 61, 126, "11B10101", "109"),
    default_location_row("인천", "인천광역시|인천시", 55, 124, "11B20201", "109"),
    default_location_row("수원", "수원시", 60, 121, "11B20601", "119"),
    default_location_row("춘천", "춘천시", 73, 134, "11D10301", "101"),
    default_location_row("강릉", "강릉시", 92, 131, "11D20501", "105"),
    default_location_row("대전", "대전광역시|대전시", 67, 100, "11C20401", "133"),
    default_location_row("세종", "세종시|세종특별자치시", 66, 103, "11C20404", "133"),
    default_location_row("청주", "청주시", 69, 106, "11C10301", "131"),
    default_location_row("광주", "광주광역시|광주시", 58, 74, "11F20501", "156"),
    default_location_row("전주", "전주시", 63, 89, "11F10201", "146"),
    default_location_row("목포", "목포시", 50, 67, "21F20801", "165"),
    default_location_row("대구", "대구광역시|대구시", 89, 90, "11H10701", "143"),
    default_location_row("부산", "부산광역시|부산시", 98, 76, "11H20201", "159"),
    default_location_row("울산", "울산광역시|울산시", 102, 84, "11H20101", "159"),
    default_location_row("창원", "창원시", 90, 77, "11H20301", "155"),
    default_location_row("제주", "제주시|제주도|제주특별자치도", 52, 38, "11G00201", "184"),
]
