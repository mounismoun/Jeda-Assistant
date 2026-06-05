import pytest

from assistant_bot.bot import (
    AssistantBot,
    is_memory_capture_cancel,
    is_memory_deletion_confirmation,
    is_negative_confirmation,
    is_positive_confirmation,
)
from assistant_bot.config import Config
from assistant_bot.models import ConversationScope, RoutingResult
from assistant_bot.operation_result import OperationResult
from assistant_bot.stores import MemoryStore


class FakeDestination:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def send(self, message: str) -> None:
        self.messages.append(message)


class FakeOpenAI:
    def __init__(self) -> None:
        self.text_requests: list[dict[str, object]] = []

    async def embedding(self, text: str) -> list[float]:
        lowered = text.lower()
        return [1.0 if "점심" in lowered or "병원" in lowered else 0.0, 1.0]

    async def text_response(self, **kwargs) -> str:
        self.text_requests.append(kwargs)
        return "문서 핵심은 계약 일정과 비용 조건입니다.\n참고: 문서 `1` · contract.pdf"


class FakeRouter:
    async def route(self, **kwargs) -> RoutingResult:
        return RoutingResult("recall", 0.99, "첨부 문서 요약 요청")


class FakeAttachment:
    filename = "contract.txt"
    content_type = "text/plain"

    def __init__(self, data: str) -> None:
        self._data = data.encode()
        self.size = len(self._data)

    async def read(self) -> bytes:
        return self._data


class FakeMessage:
    id = 12345


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_confirmation_helpers() -> None:
    assert is_positive_confirmation("응, 전부 삭제해")
    assert is_positive_confirmation("응")
    assert is_positive_confirmation("yes confirm")
    assert is_negative_confirmation("아니 취소해")
    assert is_negative_confirmation("cancel")
    assert not is_positive_confirmation("그냥 목록 보여줘")
    assert not is_negative_confirmation("삭제해")


def test_memory_deletion_confirmation_requires_destructive_scope() -> None:
    assert is_memory_deletion_confirmation("응, 전부 삭제해")
    assert is_memory_deletion_confirmation("네, 모두 지워줘")
    assert is_memory_deletion_confirmation("yes delete all")
    assert not is_memory_deletion_confirmation("응")
    assert not is_memory_deletion_confirmation("ok")
    assert not is_memory_deletion_confirmation("삭제해")
    assert not is_memory_deletion_confirmation("메모 삭제해")
    assert not is_memory_deletion_confirmation("전부 보여줘")


def test_memory_capture_cancel_helpers() -> None:
    assert is_memory_capture_cancel("메모 그만해")
    assert is_memory_capture_cancel("메모 취소해")
    assert is_memory_capture_cancel("저장하지 마")
    assert not is_memory_capture_cancel("있다가 점심 뭐먹지")


@pytest.mark.anyio
async def test_assistant_bot_sends_due_reminders(tmp_path) -> None:
    config = Config(
        discord_token="discord-token",
        discord_client_id="client-id",
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=str(tmp_path / "assistant.sqlite"),
        max_attachment_bytes=1024,
        context_compression_chars=20000,
        retrieval_limit=8,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )
    bot = AssistantBot(config)
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="456",
        user_id="123",
        guild_id=None,
    )
    reminder_id = bot.reminders.add(scope=scope, text="제안서 초안 확인", remind_at="2000-01-01 09:00")
    destination = FakeDestination()

    async def fake_resolve(channel_id: str | None, user_id: str):
        assert channel_id is None
        assert user_id == "123"
        return destination

    bot.resolve_task_destination = fake_resolve  # type: ignore[method-assign]

    try:
        sent_count = await bot.send_due_reminders()

        assert sent_count == 1
        assert len(destination.messages) == 1
        assert not destination.messages[0].startswith("<@123>")
        assert f"알림 `{reminder_id}`" in destination.messages[0]
        assert bot.reminders.due_for_delivery(as_of="2999-01-01") == []
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_sends_guild_reminders_by_dm(tmp_path) -> None:
    config = Config(
        discord_token="discord-token",
        discord_client_id="client-id",
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=str(tmp_path / "assistant.sqlite"),
        max_attachment_bytes=1024,
        context_compression_chars=20000,
        retrieval_limit=8,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )
    bot = AssistantBot(config)
    scope = ConversationScope(
        conversation_id="channel:456:user:123",
        channel_id="456",
        user_id="123",
        guild_id="789",
    )
    bot.reminders.add(scope=scope, text="채널에서 요청한 알림", remind_at="2000-01-01 09:00")
    destination = FakeDestination()

    async def fake_resolve(channel_id: str | None, user_id: str):
        assert channel_id is None
        assert user_id == "123"
        return destination

    bot.resolve_task_destination = fake_resolve  # type: ignore[method-assign]

    try:
        sent_count = await bot.send_due_reminders()

        assert sent_count == 1
        assert destination.messages[0].startswith("알림입니다.")
        assert "<@123>" not in destination.messages[0]
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_saves_next_message_from_pending_memory_capture(tmp_path) -> None:
    config = Config(
        discord_token="discord-token",
        discord_client_id="client-id",
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=str(tmp_path / "assistant.sqlite"),
        max_attachment_bytes=1024,
        context_compression_chars=20000,
        retrieval_limit=8,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )
    bot = AssistantBot(config)
    bot.memories = MemoryStore(bot.database.connection, FakeOpenAI())  # type: ignore[assignment]
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )
    bot.pending_memory_captures.add(scope=scope, message_id="100")

    try:
        response = await bot.handle_pending_memory_capture(
            text="있다가 점심 뭐먹지",
            scope=scope,
            message_id="101",
        )

        assert response is not None
        assert response.status == "success"
        assert response.facts["text"] == "있다가 점심 뭐먹지"
        assert bot.pending_memory_captures.latest(scope=scope) is None
        assert bot.memories.get_memory_detail(scope=scope, memory_id=1).text == "있다가 점심 뭐먹지"
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_cancels_pending_memory_capture(tmp_path) -> None:
    config = Config(
        discord_token="discord-token",
        discord_client_id="client-id",
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=str(tmp_path / "assistant.sqlite"),
        max_attachment_bytes=1024,
        context_compression_chars=20000,
        retrieval_limit=8,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )
    bot = AssistantBot(config)
    bot.memories = MemoryStore(bot.database.connection, FakeOpenAI())  # type: ignore[assignment]
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )
    bot.pending_memory_captures.add(scope=scope, message_id="100")

    try:
        response = await bot.handle_pending_memory_capture(
            text="메모 그만해",
            scope=scope,
            message_id="101",
        )

        assert response is not None
        assert response.summary == "메모 대기 취소"
        assert bot.pending_memory_captures.latest(scope=scope) is None
        assert bot.memories.stats(scope=scope)["memories"] == 0
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_auto_saves_and_answers_attached_document_request(tmp_path) -> None:
    config = Config(
        discord_token="discord-token",
        discord_client_id="client-id",
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=str(tmp_path / "assistant.sqlite"),
        max_attachment_bytes=4096,
        context_compression_chars=20000,
        retrieval_limit=8,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )
    fake_openai = FakeOpenAI()
    bot = AssistantBot(config)
    bot.openai = fake_openai  # type: ignore[assignment]
    bot.memories = MemoryStore(bot.database.connection, fake_openai)  # type: ignore[arg-type]
    bot.router = FakeRouter()  # type: ignore[assignment]
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )

    try:
        response = await bot.handle_message(
            message=FakeMessage(),  # type: ignore[arg-type]
            text="이 문서 요약해봐",
            attachments=[FakeAttachment("계약 일정은 6월 10일이고 비용은 30만원입니다.")],  # type: ignore[list-item]
            scope=scope,
            author_name="moun",
            conversation_context="",
        )

        assert isinstance(response, OperationResult)
        assert response.intent == "recall"
        assert response.facts["document_ids"] == [1]
        assert response.fallback_text.startswith("문서 핵심은")
        assert bot.pending_attachments.unresolved_count(scope=scope) == 0
        assert bot.memories.stats(scope=scope)["documents"] == 1
        assert bot.memories.stats(scope=scope)["memories"] == 0
        assert "이 문서 요약해봐" not in bot.memories.get_document_detail(scope=scope, document_id=1).text
    finally:
        await bot.close()
