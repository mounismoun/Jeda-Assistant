import asyncio

import pytest

from assistant_bot.agents import DocumentAnalysisAgent
from assistant_bot.bot import (
    AssistantBot,
    asks_to_delete_document_scope,
    is_memory_capture_cancel,
    is_memory_deletion_confirmation,
    is_negative_confirmation,
    is_positive_confirmation,
    processing_status_message,
)
from assistant_bot.config import Config
from assistant_bot.models import ConversationScope, RoutingResult
from assistant_bot.operation_result import OperationResult
from assistant_bot.stores import MemoryStore, VisionOcrUsageStore


class FakeDestination:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def send(self, message: str) -> None:
        self.messages.append(message)


class FakeOpenAI:
    def __init__(self) -> None:
        self.text_requests: list[dict[str, object]] = []
        self.vision_requests: list[dict[str, object]] = []

    async def embedding(self, text: str) -> list[float]:
        lowered = text.lower()
        return [1.0 if "점심" in lowered or "병원" in lowered else 0.0, 1.0]

    async def text_response(self, **kwargs) -> str:
        self.text_requests.append(kwargs)
        return "문서 핵심은 계약 일정과 비용 조건입니다.\n참고: 문서 `1` · contract.pdf"

    async def vision_text_response(self, **kwargs) -> str:
        self.vision_requests.append(kwargs)
        return "이미지에는 책상 위 노트북이 보입니다. 화면에는 일정표 텍스트가 있습니다."


class FakeRouter:
    async def route(self, **kwargs) -> RoutingResult:
        return RoutingResult("recall", 0.99, "첨부 문서 요약 요청")


class FakeDeleteRouter:
    async def route(self, **kwargs) -> RoutingResult:
        return RoutingResult("delete_memory", 0.99, "ID 기반 기억 삭제 요청")


def test_processing_status_message_varies_by_count() -> None:
    first = processing_status_message(1)
    second = processing_status_message(2)
    long_running = processing_status_message(8)

    assert first != second
    assert "정확히 확인" in first
    assert "필요한 자료" in second
    assert "약 2분" in long_running


@pytest.mark.anyio
async def test_processing_updates_edit_existing_message(monkeypatch) -> None:
    source_message = FakeProgressSourceMessage()
    stop_event = asyncio.Event()
    calls = 0

    async def fake_wait_for(awaitable, timeout):
        nonlocal calls
        awaitable.close()
        calls += 1
        if calls <= 2:
            raise TimeoutError
        stop_event.set()
        return None

    monkeypatch.setattr(asyncio, "wait_for", fake_wait_for)

    await AssistantBot.send_processing_updates(object(), source_message, stop_event)  # type: ignore[arg-type]

    assert source_message.reply_count == 1
    assert source_message.progress_message.edits[0] != source_message.progress_message.initial_content
    assert source_message.progress_message.edits[-1] == "답변 준비가 끝났습니다."


class FakeAttachment:
    def __init__(
        self,
        data: str,
        *,
        filename: str = "contract.txt",
        content_type: str = "text/plain",
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        self._data = data.encode()
        self.size = len(self._data)

    async def read(self) -> bytes:
        return self._data


class FakeMessage:
    id = 12345


class FakeProgressMessage:
    def __init__(self, content: str) -> None:
        self.initial_content = content
        self.edits: list[str] = []

    async def edit(self, *, content: str) -> None:
        self.edits.append(content)


class FakeProgressSourceMessage:
    def __init__(self) -> None:
        self.reply_count = 0
        self.progress_message = FakeProgressMessage("")

    async def reply(self, content: str, **kwargs: object) -> FakeProgressMessage:
        self.reply_count += 1
        self.progress_message = FakeProgressMessage(content)
        return self.progress_message


class FakeOriginalMessage:
    def __init__(self, *, message_id: int, attachments: list[FakeAttachment]) -> None:
        self.id = message_id
        self.attachments = attachments


class FakeChannel:
    def __init__(self, original_message: FakeOriginalMessage) -> None:
        self.original_message = original_message
        self.fetched_ids: list[int] = []

    async def fetch_message(self, message_id: int) -> FakeOriginalMessage:
        self.fetched_ids.append(message_id)
        return self.original_message


class FakeInteractionResponse:
    def __init__(self) -> None:
        self.deferred = False
        self.edited_messages: list[dict[str, object]] = []
        self.sent_messages: list[dict[str, object]] = []

    def is_done(self) -> bool:
        return self.deferred or bool(self.edited_messages or self.sent_messages)

    async def defer(self) -> None:
        self.deferred = True

    async def edit_message(self, **kwargs: object) -> None:
        self.edited_messages.append(kwargs)

    async def send_message(self, content: str, **kwargs: object) -> None:
        self.sent_messages.append({"content": content, **kwargs})


class FakeInteractionMessage:
    def __init__(self) -> None:
        self.edits: list[dict[str, object]] = []

    async def edit(self, **kwargs: object) -> None:
        self.edits.append(kwargs)


class FakeInteractionFollowup:
    def __init__(self) -> None:
        self.sent_messages: list[dict[str, object]] = []

    async def send(self, content: str, **kwargs: object) -> None:
        self.sent_messages.append({"content": content, **kwargs})


class FakeInteraction:
    def __init__(self, user_id: str, *, channel: FakeChannel | None = None) -> None:
        self.user = type("User", (), {"id": int(user_id)})()
        self.response = FakeInteractionResponse()
        self.message = FakeInteractionMessage()
        self.followup = FakeInteractionFollowup()
        self.channel = channel


class FakeResponseComposer:
    async def compose(self, **kwargs: object) -> str:
        raw_response = kwargs["raw_response"]
        return str(raw_response)


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
    assert asks_to_delete_document_scope("파일 관련 기억 전부 삭제해")
    assert not is_memory_deletion_confirmation("응")
    assert not is_memory_deletion_confirmation("ok")
    assert not is_memory_deletion_confirmation("삭제해")
    assert not is_memory_deletion_confirmation("메모 삭제해")
    assert not is_memory_deletion_confirmation("전부 보여줘")
    assert not is_memory_deletion_confirmation("메모 한개 제외하고 모두 삭제해")
    assert not is_memory_deletion_confirmation("파일만 전부 삭제해")
    assert not asks_to_delete_document_scope("메모 관련 기억 전부 삭제해")


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
    bot.vision_ocr_usage = VisionOcrUsageStore(bot.database.connection)
    bot.document_analysis_agent = DocumentAnalysisAgent(
        config=config,
        openai=fake_openai,  # type: ignore[arg-type]
        memories=bot.memories,
        usage=bot.vision_ocr_usage,
        logs=bot.logs,
    )
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
        assert response.intent == "analyze_document"
        assert response.facts["document_ids"] == [1]
        assert response.fallback_text.startswith("문서 핵심은")
        assert bot.pending_attachments.unresolved_count(scope=scope) == 0
        assert bot.memories.stats(scope=scope)["documents"] == 1
        assert bot.memories.stats(scope=scope)["memories"] == 0
        assert "이 문서 요약해봐" not in bot.memories.get_document_detail(scope=scope, document_id=1).text
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_attaches_buttons_to_pending_attachment_confirmation(tmp_path) -> None:
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
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )
    bot.pending_attachments.add(scope=scope, message_id="100", filenames=["note.pdf"])
    result = OperationResult(
        agent="bot",
        intent="remember",
        status="confirm_required",
        summary="첨부 파일 기억 저장 확인 대기",
        fallback_text="저장할까요?",
    )

    try:
        view = bot.confirmation_view_for(result, scope)

        assert view is not None
        assert bot.confirmation_action_for(result, scope) == "save_attachment"
        assert [child.label for child in view.children] == ["승인", "거부"]
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_attaches_buttons_to_memory_delete_confirmation(tmp_path) -> None:
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
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )
    bot.pending_memory_deletions.add(
        scope=scope,
        message_id="100",
        memory_count=1,
        document_count=0,
    )
    result = OperationResult(
        agent="memory",
        intent="delete_memory",
        status="confirm_required",
        summary="사용자 기준 저장 기억 전체 삭제 확인 필요",
        fallback_text="삭제할까요?",
    )

    try:
        view = bot.confirmation_view_for(result, scope)

        assert view is not None
        assert bot.confirmation_action_for(result, scope) == "delete_all_memories"
        assert [child.label for child in view.children] == ["승인", "거부"]
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_confirmation_button_defers_before_editing_original_message(tmp_path) -> None:
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
    bot.response_composer = FakeResponseComposer()  # type: ignore[assignment]
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )
    interaction = FakeInteraction(user_id="123")

    try:
        await bot.handle_confirmation_button(
            interaction,  # type: ignore[arg-type]
            scope=scope,
            action="unknown",
            approved=True,
        )

        assert interaction.response.deferred is True
        assert interaction.response.edited_messages == []
        assert interaction.message.edits
        assert interaction.message.edits[-1]["view"] is None
        assert "처리할 수 있는 작업" in str(interaction.message.edits[-1]["content"])
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_confirmation_button_approves_pending_image_with_document_analysis(tmp_path) -> None:
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
    fake_openai = FakeOpenAI()
    bot = AssistantBot(config)
    bot.openai = fake_openai  # type: ignore[assignment]
    bot.memories = MemoryStore(bot.database.connection, fake_openai)  # type: ignore[arg-type]
    bot.vision_ocr_usage = VisionOcrUsageStore(bot.database.connection)
    bot.document_analysis_agent = DocumentAnalysisAgent(
        config=config,
        openai=fake_openai,  # type: ignore[arg-type]
        memories=bot.memories,
        usage=bot.vision_ocr_usage,
        logs=bot.logs,
    )
    bot.response_composer = FakeResponseComposer()  # type: ignore[assignment]
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )
    bot.pending_attachments.add(scope=scope, message_id="100", filenames=["IMG_7700.jpg"])
    original_message = FakeOriginalMessage(
        message_id=100,
        attachments=[
            FakeAttachment(
                "fake image bytes",
                filename="IMG_7700.jpg",
                content_type="image/jpeg",
            )
        ],
    )
    interaction = FakeInteraction(user_id="123", channel=FakeChannel(original_message))

    try:
        await bot.handle_confirmation_button(
            interaction,  # type: ignore[arg-type]
            scope=scope,
            action="save_attachment",
            approved=True,
        )

        assert bot.pending_attachments.unresolved_count(scope=scope) == 0
        assert bot.memories.stats(scope=scope)["documents"] == 1
        assert fake_openai.vision_requests
        assert fake_openai.vision_requests[-1]["model"] == "gpt-5.4-mini"
        assert fake_openai.vision_requests[-1]["detail"] == "auto"
        assert "이미지에는 책상" in bot.memories.get_document_detail(scope=scope, document_id=1).text
        assert interaction.message.edits
        assert "이미지 파일이라서 비전 OCR이 필요" not in str(interaction.message.edits[-1]["content"])
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_confirms_memory_and_document_id_deletion_before_delete(tmp_path) -> None:
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
    bot = AssistantBot(config)
    bot.memories = MemoryStore(bot.database.connection, FakeOpenAI())  # type: ignore[assignment]
    bot.router = FakeDeleteRouter()  # type: ignore[assignment]
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )

    try:
        memory_id = await bot.memories.save_text_memory(
            scope=scope,
            text="삭제 확인 테스트 메모",
            source_message_id="m1",
        )
        document_id, _ = await bot.memories.save_document(
            scope=scope,
            filename="delete-test.txt",
            content_type="text/plain",
            text="삭제 확인 테스트 문서",
            source_message_id="d1",
        )

        response = await bot.handle_message(
            message=FakeMessage(),  # type: ignore[arg-type]
            text=f"메모 {memory_id} 삭제해, 문서 {document_id} 삭제해",
            attachments=[],
            scope=scope,
            author_name="moun",
            conversation_context="",
        )

        assert isinstance(response, OperationResult)
        assert response.status == "confirm_required"
        assert response.facts["memory_ids"] == [memory_id]
        assert response.facts["document_ids"] == [document_id]
        assert bot.memories.get_memory_detail(scope=scope, memory_id=memory_id) is not None
        assert bot.memories.get_document_detail(scope=scope, document_id=document_id) is not None
        pending = bot.pending_memory_deletions.latest(scope=scope)
        assert pending is not None
        assert pending.mode == "targets"

        confirmed = bot.handle_pending_memory_deletion_confirmation(text="응", scope=scope)

        assert confirmed is not None
        assert confirmed.status == "success"
        assert confirmed.facts["deleted_count"] == 2
        assert bot.memories.get_memory_detail(scope=scope, memory_id=memory_id) is None
        assert bot.memories.get_document_detail(scope=scope, document_id=document_id) is None
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_file_related_delete_targets_documents_only(tmp_path) -> None:
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
    bot = AssistantBot(config)
    bot.memories = MemoryStore(bot.database.connection, FakeOpenAI())  # type: ignore[assignment]
    bot.router = FakeDeleteRouter()  # type: ignore[assignment]
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )

    try:
        memory_id = await bot.memories.save_text_memory(
            scope=scope,
            text="삭제되면 안 되는 텍스트 메모",
            source_message_id="m1",
        )
        document_id_1, _ = await bot.memories.save_document(
            scope=scope,
            filename="file-a.pdf",
            content_type="application/pdf",
            text="삭제할 문서 A",
            source_message_id="d1",
        )
        document_id_2, _ = await bot.memories.save_document(
            scope=scope,
            filename="file-b.jpg",
            content_type="image/jpeg",
            text="삭제할 문서 B",
            source_message_id="d2",
        )

        response = await bot.handle_message(
            message=FakeMessage(),  # type: ignore[arg-type]
            text="파일 관련 기억 전부 삭제해",
            attachments=[],
            scope=scope,
            author_name="moun",
            conversation_context="",
        )

        assert isinstance(response, OperationResult)
        assert response.status == "confirm_required"
        assert response.facts["memory_ids"] == []
        assert response.facts["document_ids"] == [document_id_2, document_id_1]
        pending = bot.pending_memory_deletions.latest(scope=scope)
        assert pending is not None
        assert pending.mode == "targets"
        assert pending.memory_ids == []
        assert pending.document_ids == [document_id_2, document_id_1]

        confirmed = bot.handle_pending_memory_deletion_confirmation(text="응", scope=scope)

        assert confirmed is not None
        assert confirmed.status == "success"
        assert bot.memories.get_memory_detail(scope=scope, memory_id=memory_id) is not None
        assert bot.memories.get_document_detail(scope=scope, document_id=document_id_1) is None
        assert bot.memories.get_document_detail(scope=scope, document_id=document_id_2) is None
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_cancels_pending_delete_when_confirmation_changes_scope(tmp_path) -> None:
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
    bot = AssistantBot(config)
    bot.memories = MemoryStore(bot.database.connection, FakeOpenAI())  # type: ignore[assignment]
    scope = ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )

    try:
        memory_id = await bot.memories.save_text_memory(
            scope=scope,
            text="삭제되면 안 되는 텍스트 메모",
            source_message_id="m1",
        )
        document_id, _ = await bot.memories.save_document(
            scope=scope,
            filename="file-a.pdf",
            content_type="application/pdf",
            text="삭제되면 안 되는 문서",
            source_message_id="d1",
        )
        pending_result = bot.request_memory_deletion_confirmation(message_id="100", scope=scope)

        assert pending_result.status == "confirm_required"
        changed = bot.handle_pending_memory_deletion_confirmation(
            text="메모 한개 제외하고 모두 삭제해",
            scope=scope,
        )

        assert changed is not None
        assert changed.status == "success"
        assert "취소" in changed.fallback_text
        assert bot.pending_memory_deletions.latest(scope=scope) is None
        assert bot.memories.get_memory_detail(scope=scope, memory_id=memory_id) is not None
        assert bot.memories.get_document_detail(scope=scope, document_id=document_id) is not None
    finally:
        await bot.close()
