import pytest

import assistant_bot.agents.document_analysis as document_analysis
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
    def __init__(self, *, vision_outputs: list[str] | None = None) -> None:
        self.vision_requests: list[dict[str, object]] = []
        self.text_requests: list[dict[str, object]] = []
        self.vision_outputs = list(vision_outputs or [])

    async def embedding(self, text: str) -> list[float]:
        return [1.0, 0.0]

    async def vision_text_response(self, **kwargs) -> str:
        self.vision_requests.append(kwargs)
        if self.vision_outputs:
            return self.vision_outputs.pop(0)
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


@pytest.mark.anyio
async def test_document_analysis_agent_skips_vision_for_text_only_pdf(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(document_analysis, "extract_bytes_text", lambda data, *, filename: "PDF 본문 텍스트")
    monkeypatch.setattr(document_analysis, "pdf_has_images", lambda data: False)
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
        text="이 문서 분석해줘",
        scope=scope,
        message_id="100",
        attachments=[
            FakeAttachment(
                filename="text.pdf",
                data=b"pdf-bytes",
                content_type="application/pdf",
            )  # type: ignore[list-item]
        ],
    )

    assert result.status == "success"
    assert openai.vision_requests == []
    assert usage.used_today(user_id=scope.user_id, usage_date="2026-06-05") == 0


@pytest.mark.anyio
async def test_document_analysis_agent_triages_decorative_pdf_images(
    tmp_path,
    monkeypatch,
) -> None:
    pdf_bytes = b"pdf-with-decorative-image"
    monkeypatch.setattr(document_analysis, "extract_bytes_text", lambda data, *, filename: "PDF 본문 텍스트")
    monkeypatch.setattr(document_analysis, "pdf_has_images", lambda data: True)
    monkeypatch.setattr(
        document_analysis,
        "render_pdf_pages_to_png",
        lambda data, *, filename: [(f"{filename}-page-1.png", b"page-image")],
    )
    database = AppDatabase(str(tmp_path / "assistant.sqlite"))
    openai = FakeOpenAI(
        vision_outputs=[
            '{"pages":[{"filename":"mixed.pdf-page-1.png","analyze":false,"reason":"장식 이미지"}]}'
        ]
    )
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
        text="이 문서 분석해줘",
        scope=scope,
        message_id="100",
        attachments=[
            FakeAttachment(
                filename="mixed.pdf",
                data=pdf_bytes,
                content_type="application/pdf",
            )  # type: ignore[list-item]
        ],
    )

    detail = MemoryStore(database.connection, openai).get_document_detail(scope=scope, document_id=1)  # type: ignore[arg-type]
    assert result.status == "success"
    assert len(openai.vision_requests) == 1
    assert openai.vision_requests[0]["detail"] == "auto"
    assert detail is not None
    assert "[PDF 중요 이미지 분석]" not in detail.text
    assert usage.used_today(user_id=scope.user_id, usage_date="2026-06-05") == len(pdf_bytes)


@pytest.mark.anyio
async def test_document_analysis_agent_adds_selected_pdf_visual_analysis(
    tmp_path,
    monkeypatch,
) -> None:
    pdf_bytes = b"pdf-with-important-chart"
    monkeypatch.setattr(document_analysis, "extract_bytes_text", lambda data, *, filename: "PDF 본문 텍스트")
    monkeypatch.setattr(document_analysis, "pdf_has_images", lambda data: True)
    monkeypatch.setattr(
        document_analysis,
        "render_pdf_pages_to_png",
        lambda data, *, filename: [(f"{filename}-page-1.png", b"chart-page")],
    )
    database = AppDatabase(str(tmp_path / "assistant.sqlite"))
    openai = FakeOpenAI(
        vision_outputs=[
            '{"pages":[{"filename":"chart.pdf-page-1.png","analyze":true,"reason":"핵심 차트"}]}',
            "차트 분석 결과: 매출이 2분기에 증가했습니다.",
        ]
    )
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
        text="차트까지 분석해줘",
        scope=scope,
        message_id="100",
        attachments=[
            FakeAttachment(
                filename="chart.pdf",
                data=pdf_bytes,
                content_type="application/pdf",
            )  # type: ignore[list-item]
        ],
    )

    detail = MemoryStore(database.connection, openai).get_document_detail(scope=scope, document_id=1)  # type: ignore[arg-type]
    assert result.status == "success"
    assert len(openai.vision_requests) == 2
    assert openai.vision_requests[0]["model"] == "gpt-5.4-mini"
    assert openai.vision_requests[1]["detail"] == "auto"
    assert detail is not None
    assert "[PDF 중요 이미지 분석]" in detail.text
    assert "매출이 2분기에 증가" in detail.text
    assert usage.used_today(user_id=scope.user_id, usage_date="2026-06-05") == len(pdf_bytes)


@pytest.mark.anyio
async def test_document_analysis_agent_skips_pdf_visuals_when_user_requests_text_only(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(document_analysis, "extract_bytes_text", lambda data, *, filename: "PDF 본문 텍스트")
    monkeypatch.setattr(document_analysis, "pdf_has_images", lambda data: True)
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
        text="텍스트만 요약해줘",
        scope=scope,
        message_id="100",
        attachments=[
            FakeAttachment(
                filename="mixed.pdf",
                data=b"pdf-with-image",
                content_type="application/pdf",
            )  # type: ignore[list-item]
        ],
    )

    assert result.status == "success"
    assert openai.vision_requests == []
    assert usage.used_today(user_id=scope.user_id, usage_date="2026-06-05") == 0


@pytest.mark.anyio
async def test_document_analysis_agent_rejects_mixed_pdf_vision_triage_over_limit(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(document_analysis, "extract_bytes_text", lambda data, *, filename: "PDF 본문 텍스트")
    monkeypatch.setattr(document_analysis, "pdf_has_images", lambda data: True)
    monkeypatch.setattr(
        document_analysis,
        "render_pdf_pages_to_png",
        lambda data, *, filename: [(f"{filename}-page-1.png", b"chart-page")],
    )
    database = AppDatabase(str(tmp_path / "assistant.sqlite"))
    openai = FakeOpenAI()
    config = make_config(
        str(tmp_path / "assistant.sqlite"),
        vision_ocr_per_message_bytes=10,
    )
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
        text="이 문서 분석해줘",
        scope=scope,
        message_id="100",
        attachments=[
            FakeAttachment(
                filename="mixed.pdf",
                data=b"pdf-with-image-over-limit",
                content_type="application/pdf",
            )  # type: ignore[list-item]
        ],
    )

    assert result.status == "unsupported"
    assert result.facts["reason"] == "single_message_limit_exceeded"
    assert openai.vision_requests == []
    assert usage.used_today(user_id=scope.user_id, usage_date="2026-06-05") == 0


def make_scope() -> ConversationScope:
    return ConversationScope(
        conversation_id="dm:123",
        channel_id="dm",
        user_id="123",
        guild_id=None,
    )


def make_config(
    database_path: str,
    *,
    vision_ocr_per_message_bytes: int = 10 * 1024 * 1024,
) -> Config:
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
        vision_ocr_per_message_bytes=vision_ocr_per_message_bytes,
    )
