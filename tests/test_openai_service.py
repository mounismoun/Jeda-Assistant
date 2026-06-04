from __future__ import annotations

import pytest

from assistant_bot.config import Config
from assistant_bot.openai_service import OpenAIService
from assistant_bot.tool_calling import ToolSpec


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


@pytest.mark.anyio
async def test_tool_response_runs_function_call_and_returns_final_text() -> None:
    service = OpenAIService(make_config())
    fake_client = FakeOpenAIClient(
        responses=[
            FakeToolResponse(
                output=[
                    FakeFunctionCall(
                        name="lookup_note",
                        arguments='{"query":"운동"}',
                        call_id="call-1",
                    )
                ],
                output_text="",
            ),
            FakeToolResponse(output=[], output_text="운동 메모를 찾았어요."),
        ]
    )
    service.client = fake_client  # type: ignore[assignment]
    tool = ToolSpec(
        name="lookup_note",
        description="메모를 찾는다.",
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
        handler=lambda arguments: {"query": arguments["query"], "result": "저녁 운동"},
    )

    answer = await service.tool_response(
        model="gpt-test",
        instructions="테스트",
        input_text="운동 기억 찾아줘",
        tools=[tool],
    )

    assert answer == "운동 메모를 찾았어요."
    assert fake_client.responses.calls == 2
    second_input = fake_client.responses.requests[1]["input"]
    assert second_input[-1]["type"] == "function_call_output"
    assert second_input[-1]["call_id"] == "call-1"
    assert "저녁 운동" in second_input[-1]["output"]


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
    def __init__(
        self,
        *,
        text_failures: int = 0,
        embedding_failures: int = 0,
        responses: list[object] | None = None,
    ) -> None:
        self.responses = FakeResponses(text_failures, responses=responses)
        self.embeddings = FakeEmbeddings(embedding_failures)


class FakeResponses:
    def __init__(self, failures: int, *, responses: list[object] | None = None) -> None:
        self.failures = failures
        self.responses = responses or []
        self.requests: list[dict] = []
        self.calls = 0

    async def create(self, **kwargs):
        self.calls += 1
        self.requests.append(kwargs)
        if self.calls <= self.failures:
            raise RuntimeError("text failure")
        if self.responses:
            return self.responses.pop(0)
        return FakeTextResponse()


class FakeTextResponse:
    output_text = "OK"
    output = []


class FakeToolResponse:
    def __init__(self, *, output: list[object], output_text: str) -> None:
        self.output = output
        self.output_text = output_text


class FakeFunctionCall:
    type = "function_call"

    def __init__(self, *, name: str, arguments: str, call_id: str) -> None:
        self.name = name
        self.arguments = arguments
        self.call_id = call_id


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
