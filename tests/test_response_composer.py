import pytest

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.operation_result import OperationResult
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
    assert "친근한 존댓말" in openai.requests[0]["instructions"]


@pytest.mark.anyio
async def test_response_composer_prefers_structured_operation_result() -> None:
    openai = FakeComposerOpenAI("알림 등록해뒀어요. 오늘 오전 7시 4분에 DM으로 알려드릴게요.")
    composer = ResponseComposer(config=make_config(), openai=openai)  # type: ignore[arg-type]

    answer = await composer.compose(
        user_text="1분 뒤 알림 보내줘",
        raw_response=OperationResult(
            agent="reminder",
            intent="manage_reminder",
            status="success",
            summary="사용자 알림 등록 완료",
            facts={
                "reminder_id": 1,
                "remind_at": "2026-06-05 07:04",
                "human_remind_at": "오늘 오전 7시 4분",
                "delivery": "DM",
            },
            fallback_text="알림 `1`로 등록했어요. `2026-06-05 07:04`에 DM으로 알려드릴게요.",
        ),
        scope=make_scope(),
        location_label="DM",
        conversation_context="assistant: 알림 `1`로 등록했어요.",
    )

    assert answer == "알림 등록해뒀어요. 오늘 오전 7시 4분에 DM으로 알려드릴게요."
    request = openai.requests[0]
    assert "구조화된 실행 결과" in request["input_text"]
    assert '"agent": "reminder"' in request["input_text"]
    assert "fallback_text나 기존 문장을 그대로 복사하지 않는다" in request["instructions"]


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
