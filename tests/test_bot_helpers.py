import pytest

from assistant_bot.bot import (
    AssistantBot,
    is_memory_deletion_confirmation,
    is_negative_confirmation,
    is_positive_confirmation,
)
from assistant_bot.config import Config
from assistant_bot.models import ConversationScope


class FakeDestination:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def send(self, message: str) -> None:
        self.messages.append(message)


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


@pytest.mark.anyio
async def test_assistant_bot_sends_due_task_reminders(tmp_path) -> None:
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
    task_id = bot.tasks.add(scope=scope, title="제안서 초안 작성", due_at="2000-01-01")
    destination = FakeDestination()

    async def fake_resolve(channel_id: str | None, user_id: str):
        assert channel_id is None
        assert user_id == "123"
        return destination

    bot.resolve_task_destination = fake_resolve  # type: ignore[method-assign]

    try:
        sent_count = await bot.send_due_task_reminders()

        assert sent_count == 1
        assert len(destination.messages) == 1
        assert not destination.messages[0].startswith("<@123>")
        assert f"할 일 `{task_id}`" in destination.messages[0]
        assert bot.tasks.due_for_reminder(today="2999-01-01") == []
    finally:
        await bot.close()


@pytest.mark.anyio
async def test_assistant_bot_sends_guild_task_reminders_by_dm(tmp_path) -> None:
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
    bot.tasks.add(scope=scope, title="채널에서 받은 할 일", due_at="2000-01-01")
    destination = FakeDestination()

    async def fake_resolve(channel_id: str | None, user_id: str):
        assert channel_id is None
        assert user_id == "123"
        return destination

    bot.resolve_task_destination = fake_resolve  # type: ignore[method-assign]

    try:
        sent_count = await bot.send_due_task_reminders()

        assert sent_count == 1
        assert destination.messages[0].startswith("할 일 리마인더입니다.")
        assert "<@123>" not in destination.messages[0]
    finally:
        await bot.close()
