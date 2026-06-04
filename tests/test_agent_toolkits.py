import pytest

from assistant_bot.agent_toolkits import build_conversation_read_tools
from assistant_bot.config import Config
from assistant_bot.database import AppDatabase
from assistant_bot.models import ConversationScope
from assistant_bot.stores import MemoryStore, TaskStore


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_conversation_read_tools_list_tasks(tmp_path) -> None:
    database = AppDatabase(str(tmp_path / "assistant.sqlite"))
    tasks = TaskStore(database.connection)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    task_id = tasks.add(scope=scope, title="제안서 초안 작성", priority="high", due_at="2026-06-10")
    tools = build_conversation_read_tools(
        config=make_config(tmp_path),
        memories=MemoryStore(database.connection, openai=FakeEmbeddingService()),
        tasks=tasks,
        scope=scope,
    )
    tool_by_name = {tool.name: tool for tool in tools}

    result = await tool_by_name["list_tasks"].run({"status": "open", "limit": 5})

    assert result["ok"] is True
    assert result["results"][0]["id"] == task_id
    assert result["results"][0]["title"] == "제안서 초안 작성"
    assert result["results"][0]["priority_label"] == "높음"
    assert all(tool.read_only for tool in tools)


def make_config(tmp_path) -> Config:
    return Config(
        discord_token="discord",
        discord_client_id=None,
        openai_api_key="openai",
        router_model="router",
        easy_model="easy",
        medium_model="medium",
        hard_model="hard",
        embedding_model="embedding",
        database_path=str(tmp_path / "assistant.sqlite"),
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


class FakeEmbeddingService:
    async def embedding(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]
