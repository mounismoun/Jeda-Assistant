from __future__ import annotations

import pytest

from assistant_bot.config import Config
from assistant_bot.openai_service import OpenAIService


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_text_response_retries_transient_failure() -> None:
    service = OpenAIService(make_config())
    fake_client = FakeOpenAIClient(text_failures=1)
    service.client = fake_client  # type: ignore[assignment]

    output = await service.text_response(
        model="gpt-test",
        instructions="테스트",
        input_text="입력",
    )

    assert output == "OK"
    assert fake_client.responses.calls == 2


@pytest.mark.anyio
async def test_embedding_retries_transient_failure() -> None:
    service = OpenAIService(make_config())
    fake_client = FakeOpenAIClient(embedding_failures=1)
    service.client = fake_client  # type: ignore[assignment]

    embedding = await service.embedding("입력")

    assert embedding == [0.1, 0.2, 0.3]
    assert fake_client.embeddings.calls == 2


@pytest.mark.anyio
async def test_text_response_raises_after_retry_budget() -> None:
    service = OpenAIService(make_config(openai_max_retries=1))
    fake_client = FakeOpenAIClient(text_failures=3)
    service.client = fake_client  # type: ignore[assignment]

    with pytest.raises(RuntimeError, match="text failure"):
        await service.text_response(
            model="gpt-test",
            instructions="테스트",
            input_text="입력",
        )

    assert fake_client.responses.calls == 2


def make_config(openai_max_retries: int = 2) -> Config:
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
        openai_max_retries=openai_max_retries,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )


class FakeOpenAIClient:
    def __init__(self, *, text_failures: int = 0, embedding_failures: int = 0) -> None:
        self.responses = FakeResponses(text_failures)
        self.embeddings = FakeEmbeddings(embedding_failures)


class FakeResponses:
    def __init__(self, failures: int) -> None:
        self.failures = failures
        self.calls = 0

    async def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("text failure")
        return FakeTextResponse()


class FakeTextResponse:
    output_text = "OK"


class FakeEmbeddings:
    def __init__(self, failures: int) -> None:
        self.failures = failures
        self.calls = 0

    async def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("embedding failure")
        return FakeEmbeddingResponse()


class FakeEmbeddingResponse:
    data = [type("EmbeddingData", (), {"embedding": [0.1, 0.2, 0.3]})()]
