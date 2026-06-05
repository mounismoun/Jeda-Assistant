import pytest

from assistant_bot.agents.document_analysis import DocumentAnalysisAgent
from assistant_bot.config import Config
from assistant_bot.database import AppDatabase
from assistant_bot.models import ConversationScope
from assistant_bot.stores import AgentLogStore, MemoryStore, VisionOcrUsageStore


class FakeAttachment:
    def __init__(
        self,
        *,
        filename: str,
        data: bytes,
        size: int | None = None,
        content_type: str | None = None,
    ) -> None:
        self.filename = filename
        self._data = data
        self.size = len(data) if size is None else size
        self.content_type = content_type

    async def read(self) -> bytes:
        return self._data


class FakeOpenAI:
    def __init__(self) -> None:
        self.vision_requests: list[dict[str, object]] = []
        self.text_requests: list[dict[str, object]] = []

    async def embedding(self, text: str) -> list[float]:
        return [1.0, 0.0]

    async def vision_text_response(self, **kwargs) -> str:
        self.vision_requests.append(kwargs)
        return "이미지 OCR 결과: 계약 일정은 6월 10일입니다."

    async def text_response(self, **kwargs) -> str:
        self.text_requests.append(kwargs)
        return "분석 결과입니다. 참고: 문서 `1` · scan.png"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_document_analysis_agent_uses_fixed_vision_model_and_auto_detail(tmp_path) -> None:
    database = AppDatabase(str(tmp_path / "assistant.sqlite"))
    openai = FakeOpenAI()
    config = make_config(str(tmp_path / "assistant.sqlite"))
    scope = make_scope()
    agent = DocumentAnalysisAgent(
        config=config,
        openai=openai,  # type: ignore[arg-type]
        memories=MemoryStore(database.connection, openai),  # type: ignore[arg-type]
        usage=VisionOcrUsageStore(database.connection),
        logs=AgentLogStore(database.connection),
    )

    result = await agent.analyze(
        text="이 이미지 분석해줘",
        scope=scope,
        message_id="100",
        attachments=[
            FakeAttachment(
                filename="scan.png",
                data=b"fake-image-bytes",
                content_type="image/png",
            )  # type: ignore[list-item]
        ],
    )

    assert result.status == "success"
    assert result.facts["vision_ocr_model"] == "gpt-5.4-mini"
    assert result.facts["vision_detail"] == "auto"
    assert openai.vision_requests[0]["model"] == "gpt-5.4-mini"
    assert openai.vision_requests[0]["detail"] == "auto"
    assert VisionOcrUsageStore(database.connection).used_today(
        user_id=scope.user_id,
        usage_date="2026-06-05",
    ) == len(b"fake-image-bytes")


@pytest.mark.anyio
async def test_document_analysis_agent_rejects_vision_ocr_over_single_message_limit(tmp_path) -> None:
    database = AppDatabase(str(tmp_path / "assistant.sqlite"))
    openai = FakeOpenAI()
    config = make_config(str(tmp_path / "assistant.sqlite"))
    scope = make_scope()
    agent = DocumentAnalysisAgent(
        config=config,
        openai=openai,  # type: ignore[arg-type]
        memories=MemoryStore(database.connection, openai),  # type: ignore[arg-type]
        usage=VisionOcrUsageStore(database.connection),
        logs=AgentLogStore(database.connection),
    )

    result = await agent.analyze(
        text="이 이미지 분석해줘",
        scope=scope,
        message_id="100",
        attachments=[
            FakeAttachment(
                filename="huge.jpg",
                data=b"fake",
                size=config.vision_ocr_per_message_bytes + 1,
                content_type="image/jpeg",
            )  # type: ignore[list-item]
        ],
    )

    assert result.status == "unsupported"
    assert result.facts["reason"] == "single_message_limit_exceeded"
    assert openai.vision_requests == []


@pytest.mark.anyio
async def test_document_analysis_agent_does_not_charge_local_csv_analysis(tmp_path) -> None:
    database = AppDatabase(str(tmp_path / "assistant.sqlite"))
    openai = FakeOpenAI()
    config = make_config(str(tmp_path / "assistant.sqlite"))
    scope = make_scope()
    usage = VisionOcrUsageStore(database.connection)
    agent = DocumentAnalysisAgent(
        config=config,
        openai=openai,  # type: ignore[arg-type]
        memories=MemoryStore(database.connection, openai),  # type: ignore[arg-type]
        usage=usage,
        logs=AgentLogStore(database.connection),
    )

    result = await agent.analyze(
        text="이 표 요약해줘",
        scope=scope,
        message_id="100",
        attachments=[
            FakeAttachment(
                filename="table.csv",
                data="이름,금액\nA,100\n".encode(),
                content_type="text/csv",
            )  # type: ignore[list-item]
        ],
    )

    assert result.status == "success"
    assert openai.vision_requests == []
    assert usage.used_today(user_id=scope.user_id, usage_date="2026-06-05") == 0


def make_scope() -> ConversationScope:
    return ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )


def make_config(database_path: str) -> Config:
    return Config(
        discord_token="discord-token",
        discord_client_id="client-id",
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=database_path,
        max_attachment_bytes=20 * 1024 * 1024,
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
