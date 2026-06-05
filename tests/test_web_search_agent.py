from __future__ import annotations

import json
import time
from dataclasses import replace

import pytest

from assistant_bot.agents.web_search import (
    WebSearchAgent,
    choose_search_category,
    decide_cache_policy,
    extract_search_query,
    parse_search_plan,
)
from assistant_bot.config import Config
from assistant_bot.database import AppDatabase
from assistant_bot.models import ConversationScope, ExecutionContext
from assistant_bot.search_provider import SearchResult, clean_naver_text, normalize_naver_item
from assistant_bot.stores import AgentLogStore, WebCacheStore
from assistant_bot.web_page_reader import PageContent


class FakeOpenAI:
    async def text_response(self, **kwargs) -> str:
        if is_search_plan_prompt(kwargs["input_text"]):
            return (
                '{"queries":[{"query":"최신 AI 뉴스","category":"news",'
                '"purpose":"최신 뉴스 확인"}],"reasoning":"단일 최신 뉴스 검색"}'
            )
        if "검색 결과:" in kwargs["input_text"]:
            return '{"indexes":[1],"reason":"가장 관련 있음"}'
        assert "Naver Search API 결과" in kwargs["input_text"]
        assert "본문 확인 내용" in kwargs["input_text"]
        return "검색 결과 요약입니다.\n출처: https://example.com"


class SelectingManyOpenAI:
    async def text_response(self, **kwargs) -> str:
        if is_search_plan_prompt(kwargs["input_text"]):
            return (
                '{"queries":[{"query":"최신 AI 뉴스","category":"news",'
                '"purpose":"최신 뉴스 확인"}],"reasoning":"단일 검색"}'
            )
        if "검색 결과:" in kwargs["input_text"]:
            return '{"indexes":[1,2,3,4,5,6],"reason":"상위 관련 결과"}'
        return "본문 확인 기반 요약입니다."


class MultiQueryOpenAI:
    async def text_response(self, **kwargs) -> str:
        if is_search_plan_prompt(kwargs["input_text"]):
            return json.dumps(
                {
                    "queries": [
                        {
                            "query": "메이플스토리 스타포스 확률공개표 200제",
                            "category": "webkr",
                            "purpose": "성공/파괴 확률 확인",
                        },
                        {
                            "query": "메이플스토리 스타포스 200제 강화 비용 12성 22성",
                            "category": "webkr",
                            "purpose": "성급별 메소 비용 확인",
                        },
                    ],
                    "reasoning": "기댓값 계산에 확률표와 비용표가 모두 필요",
                },
                ensure_ascii=False,
            )
        if "검색 결과:" in kwargs["input_text"]:
            return '{"indexes":[1,2],"reason":"계산에 필요한 표"}'
        return "확률표와 비용표를 기준으로 계산했습니다."


class SummarizeFailingOpenAI(FakeOpenAI):
    async def text_response(self, **kwargs) -> str:
        if is_search_plan_prompt(kwargs["input_text"]):
            return (
                '{"queries":[{"query":"최신 AI 뉴스","category":"news",'
                '"purpose":"최신 뉴스 확인"}],"reasoning":"단일 최신 뉴스 검색"}'
            )
        if "검색 결과:" in kwargs["input_text"]:
            return '{"indexes":[1],"reason":"가장 관련 있음"}'
        raise TimeoutError("summary timeout")


class UrlOpenAI:
    def __init__(self) -> None:
        self.requests: list[str] = []

    async def text_response(self, **kwargs) -> str:
        self.requests.append(kwargs["input_text"])
        assert "URL 본문 확인 결과" in kwargs["input_text"]
        if "URL만 전달됨 여부: True" in kwargs["input_text"]:
            return "짧은 URL 요약입니다. 추가로 어떤 작업을 원하시나요?\n출처: https://example.com/article"
        return "요청에 맞춰 URL 본문을 분석했습니다.\n출처: https://example.com/article"


class RelatedUrlOpenAI:
    async def text_response(self, **kwargs) -> str:
        input_text = kwargs["input_text"]
        if is_search_plan_prompt(input_text):
            return json.dumps(
                {
                    "queries": [
                        {
                            "query": "관련 검색",
                            "category": "webkr",
                            "purpose": "URL 관련 외부 자료 확인",
                        }
                    ],
                    "reasoning": "사용자가 관련 내용 검색을 요청",
                },
                ensure_ascii=False,
            )
        if "검색 결과:" in input_text:
            return '{"indexes":[1],"reason":"관련 결과"}'
        assert "URL 본문 확인 결과" in input_text
        assert "관련 Naver Search API 결과" in input_text
        assert "관련 검색 링크 본문 확인 결과" in input_text
        return "URL 본문과 관련 검색 자료를 함께 반영했습니다.\n출처: https://example.com/article"


class ContextAwareSearchPlanOpenAI:
    def __init__(self) -> None:
        self.plan_input = ""

    async def text_response(self, **kwargs) -> str:
        self.plan_input = kwargs["input_text"]
        assert "최근 대화 맥락:" in self.plan_input
        assert "대한민국 대통령은 이재명" in self.plan_input
        if is_search_plan_prompt(self.plan_input):
            return json.dumps(
                {
                    "queries": [
                        {
                            "query": "대한민국 대통령 이재명 임기 종료일",
                            "category": "webkr",
                            "purpose": "직전 대통령 질문의 후속 질문에서 임기 종료일 확인",
                        }
                    ],
                    "reasoning": "최근 대화 맥락에서 대한민국 대통령 이재명에 대한 후속 질문으로 해석",
                },
                ensure_ascii=False,
            )
        return "요약"


def is_search_plan_prompt(input_text: str) -> bool:
    return (
        "사용자 요청:" in input_text
        and "검색 결과:" not in input_text
        and "검색 계획:" not in input_text
        and "Naver Search API 결과" not in input_text
    )


class FakeProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def search(self, **kwargs) -> list[SearchResult]:
        self.calls.append(kwargs)
        return [
            SearchResult(
                title="OpenAI 최신 소식",
                url="https://example.com",
                snippet="AI 뉴스 요약",
                category=str(kwargs["category"]),
                published_at="2026-06-05",
            )
        ]


class ManyResultsProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def search(self, **kwargs) -> list[SearchResult]:
        self.calls.append(kwargs)
        return [
            SearchResult(
                title=f"결과 {index}",
                url=f"https://example.com/{index}",
                snippet=f"요약 {index}",
                category=str(kwargs["category"]),
            )
            for index in range(10)
        ]


class QueryEchoProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def search(self, **kwargs) -> list[SearchResult]:
        self.calls.append(kwargs)
        index = len(self.calls)
        return [
            SearchResult(
                title=f"검색 {index}",
                url=f"https://example.com/search-{index}",
                snippet=str(kwargs["query"]),
                category=str(kwargs["category"]),
            )
        ]


class FailOnSecondProvider(QueryEchoProvider):
    def search(self, **kwargs) -> list[SearchResult]:
        if len(self.calls) >= 2:
            raise RuntimeError("provider unavailable")
        return super().search(**kwargs)


class FailingProvider:
    def search(self, **kwargs) -> list[SearchResult]:
        raise RuntimeError("naver failure")


class FakePageReader:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def read(self, url: str) -> PageContent:
        self.calls.append(url)
        return PageContent(
            url=url,
            final_url=url,
            title="본문 제목",
            text="검색 결과 snippet보다 자세한 본문 내용",
            success=True,
        )


class FailOnSecondPageReader(FakePageReader):
    def read(self, url: str) -> PageContent:
        if len(self.calls) >= 2:
            return PageContent(url=url, final_url=url, title="", text="", success=False, error="page unavailable")
        return super().read(url)


class SlowPageReader(FakePageReader):
    def read(self, url: str) -> PageContent:
        self.calls.append(url)
        time.sleep(0.2)
        return PageContent(
            url=url,
            final_url=url,
            title="늦은 본문",
            text="늦게 도착한 본문",
            success=True,
        )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_naver_result_normalization_strips_html_and_shop_fields() -> None:
    result = normalize_naver_item(
        {
            "title": "<b>상품</b>",
            "link": "https://example.com/item",
            "description": "&quot;좋은&quot; 상품",
            "lprice": "12000",
            "mallName": "<b>몰</b>",
        },
        category="shop",
    )

    assert result.title == "상품"
    assert result.url == "https://example.com/item"
    assert "12000원" in result.snippet
    assert clean_naver_text("<b>최신</b> &amp; 뉴스") == "최신 & 뉴스"


def test_search_category_and_query_extraction() -> None:
    assert choose_search_category("최신 뉴스 찾아줘") == "news"
    assert choose_search_category("블로그 후기 검색해줘") == "blog"
    assert choose_search_category("쇼핑 최저가 검색해줘") == "shop"
    assert choose_search_category("공식 문서 찾아줘") == "webkr"
    assert extract_search_query("네이버에서 최신 AI 뉴스 찾아줘") == "최신 AI 뉴스"


def test_parse_search_plan_normalizes_and_limits_queries() -> None:
    plan = parse_search_plan(
        json.dumps(
            {
                "queries": [
                    {"query": f"검색어 {index}", "category": "bad", "purpose": "목적"}
                    for index in range(6)
                ],
                "reasoning": "여러 검색 필요",
            },
            ensure_ascii=False,
        ),
        fallback_query="fallback",
        fallback_category="news",
    )

    assert len(plan.queries) == 4
    assert plan.queries[0].category == "webkr"


def test_cache_policy_decisions() -> None:
    assert decide_cache_policy("공식 문서 설치 방법 알려줘").mode == "allow_cache"
    assert decide_cache_policy("오늘 기준 환율 알려줘").mode == "prefer_fresh"
    assert decide_cache_policy("캐시 쓰지 말고 다시 검색해줘").mode == "bypass_cache"


@pytest.mark.anyio
async def test_web_search_plan_uses_execution_context_for_follow_up_question() -> None:
    database = AppDatabase(":memory:")
    openai = ContextAwareSearchPlanOpenAI()
    agent = WebSearchAgent(
        config=make_config(),
        openai=openai,  # type: ignore[arg-type]
        provider=FakeProvider(),  # type: ignore[arg-type]
        page_reader=FakePageReader(),  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    execution_context = ExecutionContext(
        focused_context="user: 지금 한국 대통령 누구야\nassistant: 검색 결과 기준 현재 대한민국 대통령은 이재명입니다.",
        route_reason="직전 대통령 질문의 후속 질문",
        route_search_need_score=70,
        route_search_decision="required",
        route_search_reason="현재 공직자 임기 확인",
    )

    plan = await agent.create_search_plan("임기가 언제까지지?", execution_context=execution_context)

    assert plan.queries[0].query == "대한민국 대통령 이재명 임기 종료일"
    assert "직전 대통령 질문의 후속 질문" in openai.plan_input


@pytest.mark.anyio
async def test_web_search_agent_summarizes_naver_results() -> None:
    database = AppDatabase(":memory:")
    provider = FakeProvider()
    agent = WebSearchAgent(
        config=make_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        page_reader=FakePageReader(),  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    result = await agent.search(text="네이버에서 최신 AI 뉴스 찾아줘", scope=scope)

    assert result.status == "success"
    assert result.intent == "web_search"
    assert result.facts["categories"] == ["news"]
    assert result.facts["page_read_count"] == 1
    assert "https://example.com" in result.fallback_text
    assert provider.calls[0]["category"] == "news"
    assert provider.calls[0]["display"] == 10


@pytest.mark.anyio
async def test_web_search_agent_reads_at_most_five_selected_pages() -> None:
    database = AppDatabase(":memory:")
    provider = ManyResultsProvider()
    page_reader = FakePageReader()
    agent = WebSearchAgent(
        config=make_config(),
        openai=SelectingManyOpenAI(),  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        page_reader=page_reader,  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    result = await agent.search(text="네이버에서 최신 AI 뉴스 찾아줘", scope=scope)

    assert result.status == "success"
    assert provider.calls[0]["display"] == 10
    assert len(page_reader.calls) == 5
    assert result.facts["page_attempt_count"] == 5


@pytest.mark.anyio
async def test_web_search_agent_uses_llm_multi_query_plan_for_calculation_request() -> None:
    database = AppDatabase(":memory:")
    provider = QueryEchoProvider()
    page_reader = FakePageReader()
    agent = WebSearchAgent(
        config=make_config(),
        openai=MultiQueryOpenAI(),  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        page_reader=page_reader,  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    result = await agent.search(
        text="메이플스토리 확률공개표 참고해서 200제 스타포스 12성에서 22성 기댓값 메소 알려줘",
        scope=scope,
    )

    assert result.status == "success"
    assert len(provider.calls) == 2
    assert provider.calls[0]["query"] == "메이플스토리 스타포스 확률공개표 200제"
    assert provider.calls[1]["query"] == "메이플스토리 스타포스 200제 강화 비용 12성 22성"
    assert result.facts["queries"] == [
        "메이플스토리 스타포스 확률공개표 200제",
        "메이플스토리 스타포스 200제 강화 비용 12성 22성",
    ]
    assert len(page_reader.calls) == 2


@pytest.mark.anyio
async def test_web_search_agent_reuses_search_and_page_cache_for_allow_cache() -> None:
    database = AppDatabase(":memory:")
    provider = QueryEchoProvider()
    page_reader = FakePageReader()
    agent = WebSearchAgent(
        config=make_config(),
        openai=MultiQueryOpenAI(),  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        page_reader=page_reader,  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    first = await agent.search(text="200제 스타포스 12성에서 22성 기댓값 메소 알려줘", scope=scope)
    second = await agent.search(text="200제 스타포스 12성에서 22성 기댓값 메소 알려줘", scope=scope)

    assert first.status == "success"
    assert second.status == "success"
    assert len(provider.calls) == 2
    assert len(page_reader.calls) == 2
    assert second.facts["cache_policy"] == "allow_cache"
    assert all(str(event).startswith("search_cache_hit:") for event in second.facts["search_cache_events"])
    assert all(str(event).startswith("page_cache_hit:") for event in second.facts["page_cache_events"])


@pytest.mark.anyio
async def test_web_search_agent_prefers_fresh_but_falls_back_to_cache_on_errors() -> None:
    database = AppDatabase(":memory:")
    provider = FailOnSecondProvider()
    page_reader = FailOnSecondPageReader()
    agent = WebSearchAgent(
        config=make_config(),
        openai=MultiQueryOpenAI(),  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        page_reader=page_reader,  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    first = await agent.search(text="최신 200제 스타포스 12성에서 22성 기댓값 메소 알려줘", scope=scope)
    second = await agent.search(text="최신 200제 스타포스 12성에서 22성 기댓값 메소 알려줘", scope=scope)

    assert first.status == "success"
    assert second.status == "success"
    assert second.facts["cache_policy"] == "prefer_fresh"
    assert "search_cache_fallback_hit:" in str(second.facts["search_cache_events"])
    assert "page_cache_fallback_hit:" in str(second.facts["page_cache_events"])


@pytest.mark.anyio
async def test_web_search_agent_reads_url_directly_and_summarizes_url_only_message() -> None:
    database = AppDatabase(":memory:")
    openai = UrlOpenAI()
    page_reader = FakePageReader()
    agent = WebSearchAgent(
        config=make_config(),
        openai=openai,  # type: ignore[arg-type]
        provider=FakeProvider(),  # type: ignore[arg-type]
        page_reader=page_reader,  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    result = await agent.read_urls(text="https://example.com/article", scope=scope)

    assert result.status == "success"
    assert result.intent == "web_url"
    assert result.facts["url_only"] is True
    assert result.facts["page_cache_events"] == ["page_cache_miss:not_found:https://example.com/article"]
    assert len(page_reader.calls) == 1
    assert "추가로 어떤 작업" in result.fallback_text


@pytest.mark.anyio
async def test_web_search_agent_reuses_page_cache_for_repeated_direct_url() -> None:
    database = AppDatabase(":memory:")
    openai = UrlOpenAI()
    page_reader = FakePageReader()
    agent = WebSearchAgent(
        config=make_config(),
        openai=openai,  # type: ignore[arg-type]
        provider=FakeProvider(),  # type: ignore[arg-type]
        page_reader=page_reader,  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    first = await agent.read_urls(text="이 링크 요약해줘 https://example.com/article", scope=scope)
    second = await agent.read_urls(text="이 링크 요약해줘 https://example.com/article", scope=scope)

    assert first.status == "success"
    assert second.status == "success"
    assert len(page_reader.calls) == 1
    assert second.facts["page_cache_events"] == ["page_cache_hit:https://example.com/article"]
    assert "사용자 요청:\n이 링크 요약해줘" in openai.requests[0]


@pytest.mark.anyio
async def test_web_search_agent_times_out_slow_direct_url_page_read() -> None:
    database = AppDatabase(":memory:")
    page_reader = SlowPageReader()
    agent = WebSearchAgent(
        config=replace(make_config(), web_page_timeout_seconds=0.05),
        openai=UrlOpenAI(),  # type: ignore[arg-type]
        provider=FakeProvider(),  # type: ignore[arg-type]
        page_reader=page_reader,  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)
    started = time.monotonic()

    result = await agent.read_urls(text="https://example.com/slow", scope=scope)

    assert time.monotonic() - started < 0.15
    assert result.status == "failed"
    assert result.warnings == ("https://example.com/slow: 본문 읽기 시간 초과(0.1초)",)
    assert page_reader.calls == ["https://example.com/slow"]


@pytest.mark.anyio
async def test_web_search_agent_searches_related_content_when_url_request_asks_for_search() -> None:
    database = AppDatabase(":memory:")
    provider = QueryEchoProvider()
    page_reader = FakePageReader()
    agent = WebSearchAgent(
        config=make_config(),
        openai=RelatedUrlOpenAI(),  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        page_reader=page_reader,  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    result = await agent.read_urls(
        text="이 URL 내용과 관련 내용도 검색해줘 https://example.com/article",
        scope=scope,
    )

    assert result.status == "success"
    assert result.facts["related_search"] is True
    assert result.facts["related_queries"] == ["관련 검색"]
    assert result.facts["related_result_count"] == 1
    assert provider.calls[0]["query"] == "관련 검색"
    assert page_reader.calls == ["https://example.com/article", "https://example.com/search-1"]
    assert "함께 반영" in result.fallback_text


@pytest.mark.anyio
async def test_web_search_agent_reports_provider_failure() -> None:
    database = AppDatabase(":memory:")
    agent = WebSearchAgent(
        config=make_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        provider=FailingProvider(),  # type: ignore[arg-type]
        page_reader=FakePageReader(),  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    result = await agent.search(text="웹에서 최신 AI 뉴스 찾아줘", scope=scope)

    assert result.status == "failed"
    assert "Naver Search API 설정" in result.fallback_text


@pytest.mark.anyio
async def test_web_search_agent_falls_back_when_summary_model_times_out() -> None:
    database = AppDatabase(":memory:")
    agent = WebSearchAgent(
        config=make_config(),
        openai=SummarizeFailingOpenAI(),  # type: ignore[arg-type]
        provider=FakeProvider(),  # type: ignore[arg-type]
        page_reader=FakePageReader(),  # type: ignore[arg-type]
        cache=WebCacheStore(database.connection),
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(conversation_id="dm:1", channel_id="dm", user_id="1", guild_id=None)

    result = await agent.search(text="네이버에서 최신 AI 뉴스 찾아줘", scope=scope)

    assert result.status == "partial_success"
    assert result.warnings
    assert "최종 요약 모델 호출이 시간 초과" in result.fallback_text
    assert "https://example.com" in result.fallback_text


def make_config() -> Config:
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
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )
