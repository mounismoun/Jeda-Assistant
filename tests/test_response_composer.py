import pytest

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.response_composer import ResponseComposer


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_response_composer_uses_model_output() -> None:
    openai = FakeComposerOpenAI("자연스럽게 다시 쓴 답변")
    composer = ResponseComposer(config=make_config(), openai=openai)  # type: ignore[arg-type]

    answer = await composer.compose(
        user_text="현재 등록되어 있는 알림 목록",
        raw_response="현재 등록된 미발송 알림 1개입니다:\n- 알림 `1` · 2026-06-05 07:04 · 알림",
        scope=make_scope(),
        location_label="DM",
        conversation_context="",
    )

    assert answer == "자연스럽게 다시 쓴 답변"
    assert "실행 결과" in openai.requests[0]["input_text"]
    assert "2026-06-05 07:04" in openai.requests[0]["input_text"]


@pytest.mark.anyio
async def test_response_composer_falls_back_to_raw_response() -> None:
    composer = ResponseComposer(config=make_config(), openai=FailingComposerOpenAI())  # type: ignore[arg-type]

    answer = await composer.compose(
        user_text="지금 몇시야?",
        raw_response="현재 날짜와 시간은 2026-06-05 07:04:00 (Asia/Seoul)입니다.",
        scope=make_scope(),
        location_label="DM",
    )

    assert answer == "현재 날짜와 시간은 2026-06-05 07:04:00 (Asia/Seoul)입니다."


def make_scope() -> ConversationScope:
    return ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )


def make_config() -> Config:
    return Config(
        discord_token="discord-token",
        discord_client_id="client-id",
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=":memory:",
        max_attachment_bytes=1024,
        context_compression_chars=20000,
        retrieval_limit=8,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=1,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )


class FakeComposerOpenAI:
    def __init__(self, output: str) -> None:
        self.output = output
        self.requests: list[dict[str, object]] = []

    async def text_response(self, **kwargs) -> str:
        self.requests.append(kwargs)
        return self.output


class FailingComposerOpenAI:
    async def text_response(self, **kwargs) -> str:
        raise RuntimeError("composer unavailable")
