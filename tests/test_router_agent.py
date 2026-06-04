import pytest

from assistant_bot.agents import RouterAgent
from assistant_bot.config import Config
from assistant_bot.models import ConversationScope


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_router_agent_prefers_model_route_over_heuristic() -> None:
    openai = FakeRouterOpenAI('{"intent":"help","confidence":0.93,"reason":"리마인더 기능 문의"}')
    router = RouterAgent(
        config=make_config(),
        openai=openai,  # type: ignore[arg-type]
        logs=FakeLogs(),  # type: ignore[arg-type]
        allowed_intents={"help", "manage_task", "chat"},
    )

    route = await router.route(
        text="리마인드 기능은 없나?",
        has_attachments=False,
        scope=make_scope(),
        conversation_context="user: 봇이 뭘 할 수 있는지 물어봄",
    )

    assert route.intent == "help"
    assert "최근 대화 맥락" in openai.requests[0]["input_text"]
    assert "현재 코드로 제공되지 않는 기능" in openai.requests[0]["instructions"]
    assert "Discord 음성 통화" in openai.requests[0]["instructions"]


@pytest.mark.anyio
async def test_router_agent_accepts_unsupported_for_unavailable_actions() -> None:
    openai = FakeRouterOpenAI('{"intent":"unsupported","confidence":0.97,"reason":"음성 통화는 지원하지 않음"}')
    router = RouterAgent(
        config=make_config(),
        openai=openai,  # type: ignore[arg-type]
        logs=FakeLogs(),  # type: ignore[arg-type]
        allowed_intents={"help", "manage_task", "chat", "unsupported"},
    )

    route = await router.route(
        text="음성 통화 걸어줘",
        has_attachments=False,
        scope=make_scope(),
    )

    assert route.intent == "unsupported"


@pytest.mark.anyio
async def test_router_agent_falls_back_to_heuristic_when_model_fails() -> None:
    router = RouterAgent(
        config=make_config(),
        openai=FailingRouterOpenAI(),  # type: ignore[arg-type]
        logs=FakeLogs(),  # type: ignore[arg-type]
        allowed_intents={"help", "manage_task", "chat"},
    )

    route = await router.route(
        text="30분 뒤 물 마시라고 알려줘",
        has_attachments=False,
        scope=make_scope(),
    )

    assert route.intent == "manage_task"


def make_scope() -> ConversationScope:
    return ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )


def make_config() -> Config:
    return Config(
        discord_token="discord",
        discord_client_id=None,
        openai_api_key="openai",
        router_model="router",
        easy_model="easy",
        medium_model="medium",
        hard_model="hard",
        embedding_model="embedding",
        database_path=":memory:",
        max_attachment_bytes=1024,
        context_compression_chars=1000,
        retrieval_limit=4,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )


class FakeRouterOpenAI:
    def __init__(self, output: str) -> None:
        self.output = output
        self.requests: list[dict[str, object]] = []

    async def text_response(self, **kwargs) -> str:
        self.requests.append(kwargs)
        return self.output


class FailingRouterOpenAI:
    async def text_response(self, **kwargs) -> str:
        raise RuntimeError("router unavailable")


class FakeLogs:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def add(self, **kwargs) -> None:
        self.rows.append(kwargs)
