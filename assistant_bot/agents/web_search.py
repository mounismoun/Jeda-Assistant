from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass

from assistant_bot.config import Config
from assistant_bot.model_selector import choose_model
from assistant_bot.models import ConversationScope, ExecutionContext
from assistant_bot.openai_service import OpenAIService
from assistant_bot.operation_result import OperationResult
from assistant_bot.search_provider import NaverSearchProvider, SearchResult
from assistant_bot.stores import AgentLogStore, WebCacheStore
from assistant_bot.web_page_reader import PageContent, WebPageReader

from .common import URL_PATTERN, extract_urls, is_url_only_message, score_web_search_need


@dataclass(frozen=True)
class SearchQuery:
    query: str
    category: str
    purpose: str


@dataclass(frozen=True)
class SearchPlan:
    queries: tuple[SearchQuery, ...]
    reasoning: str


@dataclass(frozen=True)
class CachePolicy:
    mode: str
    reason: str


class WebSearchAgent:
    def __init__(
        self,
        *,
        config: Config,
        openai: OpenAIService,
        provider: NaverSearchProvider,
        page_reader: WebPageReader,
        cache: WebCacheStore,
        logs: AgentLogStore,
    ) -> None:
        self.config = config
        self.openai = openai
        self.provider = provider
        self.page_reader = page_reader
        self.cache = cache
        self.logs = logs

    async def search(
        self,
        *,
        text: str,
        scope: ConversationScope,
        execution_context: ExecutionContext | None = None,
    ) -> OperationResult:
        plan = await self.create_search_plan(text, execution_context=execution_context)
        cache_policy = decide_cache_policy(text)
        if not plan.queries:
            return OperationResult(
                agent="web_search",
                intent="web_search",
                status="needs_input",
                summary="검색어 누락",
                fallback_text="검색할 내용을 알려주세요. 예: `네이버에서 최신 AI 뉴스 찾아줘`",
            )

        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="web_search",
            intent="web_search",
            difficulty="medium",
            model=self.config.medium_model,
            reason=f"Naver Search API 검색 계획: {plan.reasoning}; cache={cache_policy.mode}:{cache_policy.reason}",
        )
        try:
            results, search_cache_events = await self.execute_search_plan(plan, cache_policy=cache_policy)
        except Exception as error:
            return OperationResult(
                agent="web_search",
                intent="web_search",
                status="failed",
                summary="Naver Search API 검색 실패",
                warnings=(str(error),),
                fallback_text=(
                    "웹검색에 실패했습니다. Naver Search API 설정이나 네트워크 상태를 확인해 주세요. "
                    f"오류: {error}"
                ),
            )

        if not results:
            query_text = ", ".join(query.query for query in plan.queries)
            return OperationResult(
                agent="web_search",
                intent="web_search",
                status="not_found",
                summary="검색 결과 없음",
                facts={"queries": query_text},
                fallback_text=f"`{query_text}` 검색 결과를 찾지 못했어요.",
            )

        pages, page_cache_events = await self.read_relevant_pages(
            text=text,
            plan=plan,
            results=results,
            cache_policy=cache_policy,
        )
        warnings: tuple[str, ...] = ()
        try:
            answer = await self.summarize(text=text, plan=plan, results=results, pages=pages)
            status = "success"
            summary = "Naver Search API 검색 결과 요약"
        except Exception as error:
            warnings = (f"LLM 요약 실패: {error}",)
            answer = fallback_search_answer(plan=plan, results=results, pages=pages)
            status = "partial_success"
            summary = "검색 결과 확보 후 LLM 요약 실패 fallback"
        return OperationResult(
            agent="web_search",
            intent="web_search",
            status=status,
            summary=summary,
            facts={
                "queries": [query.query for query in plan.queries],
                "categories": [query.category for query in plan.queries],
                "search_plan_reasoning": plan.reasoning,
                "context_used": bool(execution_context and execution_context.focused_context),
                "focused_context": execution_context.focused_context if execution_context else "",
                "result_count": len(results),
                "page_read_count": sum(1 for page in pages if page.success),
                "page_attempt_count": len(pages),
                "cache_policy": cache_policy.mode,
                "search_cache_events": search_cache_events,
                "page_cache_events": page_cache_events,
            },
            items=tuple(
                {
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet,
                    "category": result.category,
                    "published_at": result.published_at,
                }
                for result in results
            ),
            warnings=warnings,
            preserve_values=tuple(result.url for result in results if result.url),
            fallback_text=answer,
        )

    async def read_urls(
        self,
        *,
        text: str,
        scope: ConversationScope,
        execution_context: ExecutionContext | None = None,
    ) -> OperationResult:
        urls = extract_urls(text)[: self.config.web_search_read_top_n]
        if not urls:
            return OperationResult(
                agent="web_url",
                intent="web_url",
                status="needs_input",
                summary="URL 누락",
                fallback_text="읽을 웹 URL을 보내주세요. 예: `https://example.com/article 요약해줘`",
            )
        cache_policy = decide_cache_policy(text)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="web_url",
            intent="web_url",
            difficulty="medium",
            model=self.config.medium_model,
            reason=f"웹 URL 직접 읽기; cache={cache_policy.mode}:{cache_policy.reason}",
        )
        pages: list[PageContent] = []
        cache_events: list[str] = []
        direct_page_reads = await asyncio.gather(
            *(self.read_page_with_cache(url, cache_policy=cache_policy) for url in urls)
        )
        pages = [page for page, _ in direct_page_reads]
        cache_events = [event for _, event in direct_page_reads]

        related_plan: SearchPlan | None = None
        related_results: list[SearchResult] = []
        related_pages: list[PageContent] = []
        related_search_cache_events: list[str] = []
        related_page_cache_events: list[str] = []
        warnings: tuple[str, ...] = ()
        if should_search_related_content(text):
            related_query_text = strip_urls(text)
            try:
                related_plan = await self.create_search_plan(
                    related_query_text,
                    execution_context=execution_context,
                )
                if related_plan.queries:
                    related_results, related_search_cache_events = await self.execute_search_plan(
                        related_plan,
                        cache_policy=cache_policy,
                    )
                    related_pages, related_page_cache_events = await self.read_relevant_pages(
                        text=related_query_text,
                        plan=related_plan,
                        results=related_results,
                        cache_policy=cache_policy,
                    )
            except Exception as error:
                warnings = (f"관련 웹검색 실패: {error}",)

        successful_pages = [page for page in pages if page.success]
        if not successful_pages:
            errors = tuple(f"{page.final_url}: {page.error}" for page in pages if page.error)
            return OperationResult(
                agent="web_url",
                intent="web_url",
                status="failed",
                summary="URL 본문 확인 실패",
                facts={"urls": urls, "page_cache_events": cache_events, "cache_policy": cache_policy.mode},
                warnings=errors,
                preserve_values=tuple(urls),
                fallback_text="URL 본문을 읽지 못했습니다. 공개 HTML 페이지인지 확인해 주세요.",
            )

        try:
            answer = await self.summarize_urls(
                text=text,
                pages=pages,
                related_plan=related_plan,
                related_results=related_results,
                related_pages=related_pages,
            )
            status = "success"
            summary = "URL 본문 직접 확인 응답"
        except Exception as error:
            answer = fallback_url_answer(
                text=text,
                pages=pages,
                related_results=related_results,
                related_pages=related_pages,
            )
            status = "partial_success"
            summary = "URL 본문 확인 후 LLM 요약 실패 fallback"
            warnings = (*warnings, f"LLM 요약 실패: {error}")
        return OperationResult(
            agent="web_url",
            intent="web_url",
            status=status,
            summary=summary,
            facts={
                "urls": urls,
                "url_only": is_url_only_message(text),
                "page_read_count": len(successful_pages),
                "page_attempt_count": len(pages),
                "cache_policy": cache_policy.mode,
                "page_cache_events": cache_events,
                "related_search": related_plan is not None and bool(related_plan.queries),
                "related_queries": [query.query for query in related_plan.queries] if related_plan else [],
                "related_result_count": len(related_results),
                "related_page_read_count": sum(1 for page in related_pages if page.success),
                "related_search_cache_events": related_search_cache_events,
                "related_page_cache_events": related_page_cache_events,
            },
            warnings=warnings,
            preserve_values=tuple(urls),
            fallback_text=answer,
        )

    async def create_search_plan(
        self,
        text: str,
        *,
        execution_context: ExecutionContext | None = None,
    ) -> SearchPlan:
        fallback_query = extract_search_query(text)
        instructions = """
너는 Naver Search API 검색어를 설계하는 검색 계획자다.
사용자의 질문에 답하기 위해 필요한 정보만 검색한다.
단순 최신 정보 질문은 검색어 1개로 충분하다.
계산형 질문은 계산에 필요한 기준표, 공식 값, 비용/확률/규칙을 나눠 최대 4개 검색어로 만든다.
현재 요청이 대명사나 생략형 후속 질문이면 최근 대화 맥락에서 대상과 조건을 복원한다.
예: 최근 맥락이 "현재 대한민국 대통령은 이재명"이고 요청이 "임기가 언제까지지?"라면
"대한민국 대통령 이재명 임기 종료일"로 검색한다.
현재 요청에 명시된 대상이 있으면 최근 맥락보다 현재 요청을 우선한다.
맥락이 불충분하면 추측하지 말고 현재 요청 기준 검색어를 만든다.
사용자 문장을 그대로 길게 검색하지 말고 핵심 키워드 중심으로 재작성한다.
각 검색어 category는 webkr, news, blog, shop 중 하나다.
JSON만 반환한다. 형식:
{"queries":[{"query":"검색어","category":"webkr","purpose":"필요한 정보"}],"reasoning":"짧은 이유"}
"""
        context_text = execution_context.for_agent() if execution_context else ""
        route_text = ""
        if execution_context is not None:
            route_text = (
                f"라우터 판단 이유: {execution_context.route_reason}\n"
                f"검색 필요도: {execution_context.route_search_need_score} "
                f"({execution_context.route_search_decision})\n"
                f"검색 판단 이유: {execution_context.route_search_reason}"
            )
        try:
            output = await self.openai.text_response(
                model=self.config.router_model,
                instructions=instructions,
                input_text=(
                    f"최근 대화 맥락:\n{context_text or '(없음)'}\n\n"
                    f"{route_text or '라우터 판단 정보: (없음)'}\n\n"
                    f"사용자 요청:\n{text}"
                ),
                temperature=0,
            )
            return parse_search_plan(
                output,
                fallback_query=fallback_query,
                fallback_category=choose_search_category(text),
            )
        except Exception:
            if not fallback_query:
                return SearchPlan((), "검색어 추출 실패")
            return SearchPlan(
                (SearchQuery(fallback_query, choose_search_category(text), "fallback 검색어"),),
                "검색 계획 생성 실패 후 fallback",
            )

    async def execute_search_plan(
        self,
        plan: SearchPlan,
        *,
        cache_policy: CachePolicy,
    ) -> tuple[list[SearchResult], list[str]]:
        merged: list[SearchResult] = []
        seen_urls: set[str] = set()
        cache_events: list[str] = []
        for query in plan.queries:
            results, event = await self.search_with_cache(query, cache_policy=cache_policy)
            cache_events.append(event)
            for result in results:
                dedupe_key = result.url or f"{result.title}:{result.snippet}"
                if dedupe_key in seen_urls:
                    continue
                seen_urls.add(dedupe_key)
                merged.append(result)
        return merged, cache_events

    async def search_with_cache(
        self,
        query: SearchQuery,
        *,
        cache_policy: CachePolicy,
    ) -> tuple[list[SearchResult], str]:
        enabled = self.config.web_cache_enabled
        if cache_policy.mode == "allow_cache":
            reason, cached = self.cache.get_search_results(
                provider="naver",
                category=query.category,
                query=query.query,
                enabled=enabled,
            )
            if reason == "hit":
                return cached, f"search_cache_hit:{query.query}"
            results = await self.fetch_search_results(query)
            self.cache.save_search_results(
                provider="naver",
                category=query.category,
                query=query.query,
                results=results,
                ttl_minutes=self.config.web_search_cache_ttl_minutes,
            )
            return results, f"search_cache_miss:{reason}:{query.query}"
        if cache_policy.mode == "prefer_fresh":
            try:
                results = await self.fetch_search_results(query)
                self.cache.save_search_results(
                    provider="naver",
                    category=query.category,
                    query=query.query,
                    results=results,
                    ttl_minutes=self.config.web_search_cache_ttl_minutes,
                )
                return results, f"search_cache_refresh:{query.query}"
            except Exception:
                if not self.config.web_cache_fallback_on_error:
                    raise
                reason, cached = self.cache.get_search_results(
                    provider="naver",
                    category=query.category,
                    query=query.query,
                    enabled=enabled,
                )
                if reason == "hit":
                    return cached, f"search_cache_fallback_hit:{query.query}"
                raise
        results = await self.fetch_search_results(query)
        self.cache.save_search_results(
            provider="naver",
            category=query.category,
            query=query.query,
            results=results,
            ttl_minutes=self.config.web_search_cache_ttl_minutes,
        )
        return results, f"search_cache_bypass:{query.query}"

    async def fetch_search_results(self, query: SearchQuery) -> list[SearchResult]:
        return await asyncio.to_thread(
            self.provider.search,
            query=query.query,
            category=query.category,
            display=self.config.web_search_max_results,
        )

    async def read_relevant_pages(
        self,
        *,
        text: str,
        plan: SearchPlan,
        results: list[SearchResult],
        cache_policy: CachePolicy,
    ) -> tuple[list[PageContent], list[str]]:
        indexes = await self.select_results_to_read(text=text, plan=plan, results=results)
        urls: list[str] = []
        for index in indexes[: self.config.web_search_read_top_n]:
            if index < 0 or index >= len(results):
                continue
            url = results[index].url
            if not url:
                continue
            urls.append(url)
        page_reads = await asyncio.gather(
            *(self.read_page_with_cache(url, cache_policy=cache_policy) for url in urls)
        )
        pages = [page for page, _ in page_reads]
        cache_events = [event for _, event in page_reads]
        return pages, cache_events

    async def read_page_with_cache(self, url: str, *, cache_policy: CachePolicy) -> tuple[PageContent, str]:
        enabled = self.config.web_cache_enabled
        if cache_policy.mode == "allow_cache":
            reason, cached = self.cache.get_page(url=url, enabled=enabled)
            if reason == "hit" and cached is not None:
                return cached, f"page_cache_hit:{url}"
            page = await self.read_page_with_timeout(url)
            self.cache.save_page(url=url, page=page, ttl_minutes=self.config.web_page_cache_ttl_minutes)
            return page, f"page_cache_miss:{reason}:{url}"
        if cache_policy.mode == "prefer_fresh":
            page = await self.read_page_with_timeout(url)
            if page.success or not self.config.web_cache_fallback_on_error:
                self.cache.save_page(url=url, page=page, ttl_minutes=self.config.web_page_cache_ttl_minutes)
                return page, f"page_cache_refresh:{url}"
            reason, cached = self.cache.get_page(url=url, enabled=enabled)
            if reason == "hit" and cached is not None:
                return cached, f"page_cache_fallback_hit:{url}"
            self.cache.save_page(url=url, page=page, ttl_minutes=self.config.web_page_cache_ttl_minutes)
            return page, f"page_cache_refresh_failed:{reason}:{url}"
        page = await self.read_page_with_timeout(url)
        self.cache.save_page(url=url, page=page, ttl_minutes=self.config.web_page_cache_ttl_minutes)
        return page, f"page_cache_bypass:{url}"

    async def read_page_with_timeout(self, url: str) -> PageContent:
        timeout = max(0.05, float(self.config.web_page_timeout_seconds))
        try:
            return await asyncio.wait_for(asyncio.to_thread(self.page_reader.read, url), timeout=timeout)
        except TimeoutError:
            return PageContent(
                url=url,
                final_url=url,
                title="",
                text="",
                success=False,
                error=f"본문 읽기 시간 초과({timeout:.1f}초)",
            )

    async def select_results_to_read(
        self,
        *,
        text: str,
        plan: SearchPlan,
        results: list[SearchResult],
    ) -> list[int]:
        max_count = max(1, min(self.config.web_search_read_top_n, len(results)))
        result_lines = []
        for index, result in enumerate(results, start=1):
            date_text = f" 날짜={result.published_at}" if result.published_at else ""
            result_lines.append(f"{index}. 제목={result.title}\nURL={result.url}\n요약={result.snippet}{date_text}")
        instructions = f"""
너는 웹검색 결과 중 본문을 읽을 링크를 고르는 선별기다.
사용자 요청에 직접 답하는 데 필요한 결과만 고른다.
최대 {max_count}개까지 고른다.
관련성이 낮거나 중복인 결과는 제외한다.
공식 문서, 원문, 최신 자료, 사용자가 언급한 기준표와 직접 맞는 결과를 우선한다.
JSON만 반환한다. 형식: {{"indexes":[1,2],"reason":"짧은 이유"}}
"""
        try:
            output = await self.openai.text_response(
                model=self.config.router_model,
                instructions=instructions,
                input_text=(
                    f"사용자 요청:\n{text}\n\n검색 계획:\n{format_search_plan(plan)}\n\n"
                    "검색 결과:\n" + "\n\n".join(result_lines)
                ),
                temperature=0,
            )
            match = re.search(r"\{.*\}", output, flags=re.DOTALL)
            data = json.loads(match.group(0) if match else output)
            indexes = [int(value) - 1 for value in data.get("indexes", [])]
        except Exception:
            indexes = list(range(max_count))
        unique = []
        for index in indexes:
            if 0 <= index < len(results) and index not in unique:
                unique.append(index)
        return unique[:max_count] or list(range(max_count))

    async def summarize(
        self,
        *,
        text: str,
        plan: SearchPlan,
        results: list[SearchResult],
        pages: list[PageContent],
    ) -> str:
        choice = choose_model(
            self.config,
            text,
            context_chars=sum(len(result.snippet) for result in results) + sum(len(page.text) for page in pages),
            result_count=len(results),
        )
        result_lines = []
        for index, result in enumerate(results, start=1):
            date_text = f" · 날짜: {result.published_at}" if result.published_at else ""
            result_lines.append(
                f"{index}. 제목: {result.title}\n"
                f"   URL: {result.url}\n"
                f"   요약: {result.snippet}{date_text}"
            )
        page_lines = []
        for index, page in enumerate(pages, start=1):
            if page.success:
                page_lines.append(
                    f"{index}. URL: {page.final_url}\n"
                    f"   제목: {page.title or '(없음)'}\n"
                    f"   본문 확인 내용:\n{page.text}"
                )
            else:
                page_lines.append(f"{index}. URL: {page.final_url}\n   본문 확인 실패: {page.error}")
        instructions = """
너는 Naver Search API 검색 결과와 선별 링크 본문을 함께 사용하는 웹검색 에이전트다.
본문 확인 내용이 있으면 snippet보다 본문 확인 내용을 우선 근거로 답한다.
본문 확인에 실패한 링크는 검색 snippet 자료로만 사용한다.
제공된 자료에 없는 내용은 추측하지 않는다.
최신/현재 정보는 검색 결과 기준이라고 명시한다.
답변 끝에는 출처 URL과 본문 확인 여부를 포함한다.
"""
        return await self.openai.text_response(
            model=choice.model,
            instructions=instructions,
            input_text=(
                f"사용자 요청:\n{text}\n\n"
                f"검색 계획:\n{format_search_plan(plan)}\n\n"
                "Naver Search API 결과:\n"
                f"{chr(10).join(result_lines)}\n\n"
                "선별 링크 본문 확인 결과:\n"
                f"{chr(10).join(page_lines) if page_lines else '(본문 확인 대상 없음)'}"
            ),
            temperature=0.2,
        )

    async def summarize_urls(
        self,
        *,
        text: str,
        pages: list[PageContent],
        related_plan: SearchPlan | None = None,
        related_results: list[SearchResult] | None = None,
        related_pages: list[PageContent] | None = None,
    ) -> str:
        url_only = is_url_only_message(text)
        related_results = related_results or []
        related_pages = related_pages or []
        choice = choose_model(
            self.config,
            text,
            context_chars=(
                sum(len(page.text) for page in pages)
                + sum(len(result.snippet) for result in related_results)
                + sum(len(page.text) for page in related_pages)
            ),
            result_count=len(pages) + len(related_results),
        )
        request_text = "URL만 전달됨. 짧게 요약하고 추가 요청사항이 있는지 물어본다." if url_only else strip_urls(text)
        page_lines = []
        for index, page in enumerate(pages, start=1):
            if page.success:
                page_lines.append(
                    f"{index}. URL: {page.final_url}\n"
                    f"   제목: {page.title or '(없음)'}\n"
                    f"   본문:\n{page.text}"
                )
            else:
                page_lines.append(f"{index}. URL: {page.final_url}\n   본문 확인 실패: {page.error}")
        related_result_lines = []
        for index, result in enumerate(related_results, start=1):
            date_text = f" · 날짜: {result.published_at}" if result.published_at else ""
            related_result_lines.append(
                f"{index}. 제목: {result.title}\n"
                f"   URL: {result.url}\n"
                f"   요약: {result.snippet}{date_text}"
            )
        related_page_lines = []
        for index, page in enumerate(related_pages, start=1):
            if page.success:
                related_page_lines.append(
                    f"{index}. URL: {page.final_url}\n"
                    f"   제목: {page.title or '(없음)'}\n"
                    f"   본문:\n{page.text}"
                )
            else:
                related_page_lines.append(f"{index}. URL: {page.final_url}\n   본문 확인 실패: {page.error}")
        instructions = """
너는 사용자가 보낸 웹 URL 본문을 직접 읽고 답하는 에이전트다.
검색 결과나 추측이 아니라 제공된 URL 본문만 근거로 사용한다.
사용자가 URL과 함께 관련 내용 검색을 요청했다면 URL 본문과 관련 검색 자료를 구분해서 함께 사용한다.
사용자가 URL만 보냈다면 3~5문장으로 짧게 요약하고, 어떤 작업을 원하는지 물어본다.
사용자가 별도 요청을 함께 보냈다면 그 요청에 맞춰 답한다.
본문 확인에 실패한 URL은 실패했다고 말한다.
답변 끝에는 확인한 URL을 출처로 포함한다.
"""
        return await self.openai.text_response(
            model=choice.model,
            instructions=instructions,
            input_text=(
                f"사용자 요청:\n{request_text or '(URL만 전달됨)'}\n\n"
                f"URL만 전달됨 여부: {url_only}\n\n"
                "URL 본문 확인 결과:\n"
                f"{chr(10).join(page_lines)}\n\n"
                "관련 검색 계획:\n"
                f"{format_search_plan(related_plan) if related_plan else '(관련 검색 없음)'}\n\n"
                "관련 Naver Search API 결과:\n"
                f"{chr(10).join(related_result_lines) if related_result_lines else '(관련 검색 결과 없음)'}\n\n"
                "관련 검색 링크 본문 확인 결과:\n"
                f"{chr(10).join(related_page_lines) if related_page_lines else '(관련 검색 본문 없음)'}"
            ),
            temperature=0.2,
        )


def choose_search_category(text: str) -> str:
    normalized = text.casefold()
    if any(marker in normalized for marker in ["뉴스", "속보", "news"]):
        return "news"
    if any(marker in normalized for marker in ["블로그", "후기", "리뷰", "blog", "review"]):
        return "blog"
    if any(marker in normalized for marker in ["가격", "상품", "쇼핑", "최저가", "구매", "shop"]):
        return "shop"
    return "webkr"


def decide_cache_policy(text: str) -> CachePolicy:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    bypass_markers = [
        "캐시 쓰지 말고",
        "캐시쓰지말고",
        "캐시 없이",
        "cache 없이",
        "다시 검색",
        "다시 읽",
        "새로 검색",
        "새로 읽",
        "최신으로 다시",
        "캐시 없이 읽",
        "fresh",
        "bypass cache",
    ]
    if any(marker in normalized or marker in compact for marker in bypass_markers):
        return CachePolicy("bypass_cache", "사용자가 새 조회를 명시")
    fresh_markers = [
        "최신",
        "오늘 기준",
        "방금",
        "실시간",
        "현재 가격",
        "환율",
        "주가",
        "뉴스",
        "속보",
        "latest",
        "today",
        "current price",
    ]
    if any(marker in normalized or marker in compact for marker in fresh_markers):
        return CachePolicy("prefer_fresh", "최신성 높은 요청")
    return CachePolicy("allow_cache", "TTL 내 캐시 사용 가능")


def parse_search_plan(output: str, *, fallback_query: str, fallback_category: str) -> SearchPlan:
    match = re.search(r"\{.*\}", output, flags=re.DOTALL)
    data = json.loads(match.group(0) if match else output)
    raw_queries = data.get("queries", [])
    queries: list[SearchQuery] = []
    if isinstance(raw_queries, list):
        for raw_query in raw_queries:
            if not isinstance(raw_query, dict):
                continue
            query = str(raw_query.get("query", "")).strip()
            if not query:
                continue
            category = normalize_search_category(str(raw_query.get("category", fallback_category)))
            purpose = str(raw_query.get("purpose", "")).strip() or "검색 정보"
            queries.append(SearchQuery(query=query, category=category, purpose=purpose))
    if not queries and fallback_query:
        queries.append(SearchQuery(fallback_query, normalize_search_category(fallback_category), "fallback 검색어"))
    deduped: list[SearchQuery] = []
    seen: set[tuple[str, str]] = set()
    for query in queries:
        key = (query.query.casefold(), query.category)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(query)
    return SearchPlan(tuple(deduped[:4]), str(data.get("reasoning", "검색 계획 생성")).strip())


def normalize_search_category(category: str) -> str:
    category = category.strip().lower()
    if category in NaverSearchProvider.SUPPORTED_CATEGORIES:
        return category
    return "webkr"


def format_search_plan(plan: SearchPlan) -> str:
    lines = [f"계획 이유: {plan.reasoning}"]
    for index, query in enumerate(plan.queries, start=1):
        lines.append(f"{index}. query={query.query} category={query.category} purpose={query.purpose}")
    return "\n".join(lines)


def fallback_search_answer(*, plan: SearchPlan, results: list[SearchResult], pages: list[PageContent]) -> str:
    lines = [
        "검색과 본문 확인은 수행했지만, 최종 요약 모델 호출이 시간 초과되었습니다.",
        "",
        "검색 계획:",
    ]
    for query in plan.queries:
        lines.append(f"- {query.query} ({query.purpose})")
    successful_pages = [page for page in pages if page.success]
    if successful_pages:
        lines.extend(["", "본문 확인된 링크:"])
        for page in successful_pages[:5]:
            excerpt = page.text[:300].strip()
            lines.append(f"- {page.title or page.final_url}: {page.final_url}")
            if excerpt:
                lines.append(f"  확인 내용 일부: {excerpt}")
    lines.extend(["", "검색 결과 출처:"])
    for result in results[:5]:
        lines.append(f"- {result.title}: {result.url}")
    lines.append("")
    lines.append("다시 요청하면 같은 검색 자료를 바탕으로 요약을 재시도할 수 있습니다.")
    return "\n".join(lines)


def fallback_url_answer(
    *,
    text: str,
    pages: list[PageContent],
    related_results: list[SearchResult] | None = None,
    related_pages: list[PageContent] | None = None,
) -> str:
    url_only = is_url_only_message(text)
    related_results = related_results or []
    related_pages = related_pages or []
    successful_pages = [page for page in pages if page.success]
    lines = ["URL 본문은 확인했지만, 최종 요약 모델 호출이 실패했습니다.", ""]
    if successful_pages:
        lines.append("확인한 내용 요약:")
        for page in successful_pages[:5]:
            excerpt = page.text[:300].strip()
            lines.append(f"- {page.title or page.final_url}: {excerpt}")
    failed_pages = [page for page in pages if not page.success]
    if failed_pages:
        lines.extend(["", "본문 확인 실패:"])
        for page in failed_pages:
            lines.append(f"- {page.final_url}: {page.error}")
    if related_results:
        lines.extend(["", "관련 검색 결과:"])
        for result in related_results[:5]:
            lines.append(f"- {result.title}: {result.url}")
    successful_related_pages = [page for page in related_pages if page.success]
    if successful_related_pages:
        lines.extend(["", "관련 검색 본문 확인:"])
        for page in successful_related_pages[:5]:
            lines.append(f"- {page.title or page.final_url}: {page.final_url}")
    lines.extend(["", "출처:"])
    for page in pages[:5]:
        lines.append(f"- {page.final_url}")
    if url_only:
        lines.append("")
        lines.append("원하는 작업이 있으면 요약, 핵심 정리, 사실 확인, 번역처럼 요청해 주세요.")
    return "\n".join(lines)


def extract_search_query(text: str) -> str:
    cleaned = text.strip()
    for marker in [
        "네이버에서",
        "네이버 검색",
        "웹에서",
        "웹 검색",
        "웹검색",
        "인터넷에서",
        "인터넷 검색",
        "검색해서",
        "검색해줘",
        "검색해",
        "찾아줘",
        "찾아",
        "알려줘",
        "확인해줘",
        "확인해",
    ]:
        cleaned = cleaned.replace(marker, " ")
    return " ".join(cleaned.split()).strip(" :：,.")


def strip_urls(text: str) -> str:
    return URL_PATTERN.sub("", text).strip()


def should_search_related_content(text: str) -> bool:
    if is_url_only_message(text):
        return False
    request_text = strip_urls(text)
    if not request_text:
        return False
    need = score_web_search_need(request_text)
    return need.decision == "required"
