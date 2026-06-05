from __future__ import annotations

import pytest

from assistant_bot.agents.weather import WeatherAgent
from assistant_bot.config import Config
from assistant_bot.database import AppDatabase
from assistant_bot.models import ConversationScope
from assistant_bot.operation_result import OperationResult
from assistant_bot.stores import AgentLogStore, WeatherCacheStore, WeatherLocationStore
from assistant_bot.weather_provider import (
    ForecastMoment,
    KmaWeatherProvider,
    WeatherLocation,
    WeatherLocationResolver,
    WeatherReport,
    latest_vilage_base_datetime,
)


class FakeOpenAI:
    async def text_response(self, **kwargs) -> str:
        return ""


class FakeWeatherProvider:
    def __init__(self, *, available: bool = True) -> None:
        self.available_value = available
        self.calls: list[WeatherLocation] = []

    def available(self) -> bool:
        return self.available_value

    def get_report(self, *, location: WeatherLocation, include_alerts: bool) -> WeatherReport:
        self.calls.append(location)
        return WeatherReport(
            location=location,
            base_date="20260605",
            base_time="0500",
            moments=(
                ForecastMoment(
                    date="20260605",
                    time="1200",
                    values={"SKY": "1", "PTY": "0", "TMP": "25", "POP": "20"},
                ),
            ),
            situation={"warning": "", "pre_warning": ""},
            land_forecast=(),
            cache_events=("forecast:not_found",),
        )


class FakeWebSearchAgent:
    def __init__(self) -> None:
        self.queries: list[str] = []

    async def search(self, *, text: str, scope: ConversationScope, execution_context=None) -> OperationResult:
        self.queries.append(text)
        return OperationResult(
            agent="web_search",
            intent="web_search",
            status="success",
            summary="검색 성공",
            fallback_text="미세먼지 검색 결과입니다.",
        )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_weather_agent_uses_kma_forecast_and_saves_recent_location() -> None:
    database = AppDatabase(":memory:")
    provider = FakeWeatherProvider()
    agent = WeatherAgent(
        config=make_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        locations=WeatherLocationResolver(resource_path="resources/kma_locations.csv"),
        location_store=WeatherLocationStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = make_scope()

    response = await agent.handle(text="서울 내일 날씨 알려줘", scope=scope)

    assert response.status == "success"
    assert response.facts["location"] == "서울"
    assert provider.calls[0].name == "서울"
    latest = WeatherLocationStore(database.connection).get_latest(user_id=scope.user_id)
    assert latest is not None
    assert latest["location_name"] == "서울"


@pytest.mark.anyio
async def test_weather_agent_reuses_recent_location_when_text_has_no_location() -> None:
    database = AppDatabase(":memory:")
    store = WeatherLocationStore(database.connection)
    store.save_latest(
        user_id="user-1",
        location_name="부산",
        nx=98,
        ny=76,
        land_reg_id="11H20201",
        weather_stn_id="159",
    )
    provider = FakeWeatherProvider()
    agent = WeatherAgent(
        config=make_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        locations=WeatherLocationResolver(resource_path="resources/kma_locations.csv"),
        location_store=store,
        logs=AgentLogStore(database.connection),
    )

    response = await agent.handle(text="내일 비 와?", scope=make_scope())

    assert response.status == "success"
    assert response.facts["used_recent_location"] is True
    assert provider.calls[0].name == "부산"


@pytest.mark.anyio
async def test_weather_agent_delegates_air_quality_to_web_search() -> None:
    database = AppDatabase(":memory:")
    web_search = FakeWebSearchAgent()
    agent = WeatherAgent(
        config=make_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        provider=FakeWeatherProvider(),  # type: ignore[arg-type]
        locations=WeatherLocationResolver(resource_path="resources/kma_locations.csv"),
        location_store=WeatherLocationStore(database.connection),
        logs=AgentLogStore(database.connection),
        web_search_agent=web_search,
    )

    response = await agent.handle(text="서울 미세먼지 어때?", scope=make_scope())

    assert response.status == "success"
    assert web_search.queries
    assert "미세먼지" in web_search.queries[0]


@pytest.mark.anyio
async def test_weather_agent_reports_missing_kma_key() -> None:
    database = AppDatabase(":memory:")
    agent = WeatherAgent(
        config=make_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        provider=FakeWeatherProvider(available=False),  # type: ignore[arg-type]
        locations=WeatherLocationResolver(resource_path="resources/kma_locations.csv"),
        location_store=WeatherLocationStore(database.connection),
        logs=AgentLogStore(database.connection),
    )

    response = await agent.handle(text="서울 날씨 알려줘", scope=make_scope())

    assert response.status == "failed"
    assert "KMA_API_AUTH_KEY" in response.fallback_text


def test_kma_weather_provider_cache_round_trip() -> None:
    database = AppDatabase(":memory:")
    cache = WeatherCacheStore(database.connection)
    provider = KmaWeatherProvider(
        auth_key="key",
        timeout_seconds=1,
        cache=cache,
        cache_ttl_minutes=20,
        timezone="Asia/Seoul",
    )
    cache.save(provider="kma", cache_key="sample", response={"ok": True}, ttl_minutes=20)

    status, payload = provider.cache.get(provider="kma", cache_key="sample")

    assert status == "hit"
    assert payload == {"ok": True}


def test_latest_vilage_base_datetime_uses_safe_previous_base_time() -> None:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    assert latest_vilage_base_datetime(datetime(2026, 6, 5, 5, 20, tzinfo=ZoneInfo("Asia/Seoul"))) == (
        "20260605",
        "0500",
    )
    assert latest_vilage_base_datetime(datetime(2026, 6, 5, 1, 50, tzinfo=ZoneInfo("Asia/Seoul"))) == (
        "20260604",
        "2300",
    )


def make_scope() -> ConversationScope:
    return ConversationScope(conversation_id="dm:user-1", channel_id="dm", user_id="user-1", guild_id=None)


def make_config() -> Config:
    return Config(
        discord_token="discord-token",
        discord_client_id=None,
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=":memory:",
        max_attachment_bytes=10,
        context_compression_chars=1000,
        retrieval_limit=5,
        openai_timeout_seconds=0,
        openai_max_retries=0,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=1,
        task_reminder_batch_size=10,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
        kma_api_auth_key="key",
    )
