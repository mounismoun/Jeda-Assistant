"""Responses 호출, 출처 보존과 Jeda의 역할별 모델 설정."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

import aiohttp
import tiktoken
from dotenv import load_dotenv
from openai import AsyncOpenAI


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    database: str = "./data/jeda.sqlite"
    router: str = "gpt-6-luna"
    everyday: str = "gpt-6-luna"
    vision: str = "gpt-6.1-terra"
    reasoning: str = "gpt-6.2-sol"
    max_bytes: int = 10 * 1024 * 1024
    daily_search: int = 50
    timeout: float = 60

    @classmethod
    def load(cls):
        load_dotenv()
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY를 설정하세요.")
        cfg = cls(
            key,
            os.getenv("JEDA_DATABASE_PATH", cls.database),
            os.getenv("JEDA_ROUTER_MODEL", cls.router),
            os.getenv("JEDA_CHAT_MODEL", cls.everyday),
            os.getenv("JEDA_VISION_MODEL", cls.vision),
            os.getenv("JEDA_REASONING_MODEL", cls.reasoning),
            int(os.getenv("MAX_ATTACHMENT_BYTES", cls.max_bytes)),
            int(os.getenv("WEB_SEARCH_DAILY_LIMIT_PER_USER", cls.daily_search)),
            float(os.getenv("JEDA_TIMEOUT_SECONDS", cls.timeout)),
        )
        if cfg.max_bytes <= 0 or cfg.timeout <= 0 or cfg.daily_search < 0:
            raise ValueError("파일 크기·대기시간은 양수, 검색 한도는 0 이상이어야 합니다.")
        return cfg


def encode(value):
    return tiktoken.get_encoding("o200k_base").encode(value, disallowed_special=())


def tokens(value):
    return len(encode(value))


def chunks(value, budget):
    # 문자열 경계에서 나누어 한글과 이모지의 UTF-8 시퀀스를 보존한다.
    start = 0
    while start < len(value):
        window = value[start : start + budget * 8]
        if tokens(window) <= budget:
            yield window
            start += len(window)
            continue
        lo, hi = 1, len(window)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if tokens(window[:mid]) <= budget:
                lo = mid
            else:
                hi = mid - 1
        yield window[:lo]
        start += lo


def object_schema(fields):
    return {"type": "object", "properties": fields, "required": list(fields), "additionalProperties": False}


def safe_url(value):
    return isinstance(value, str) and urlsplit(value).scheme in {"https", "http"} and bool(urlsplit(value).netloc)


def cited_urls(text):
    return {url.rstrip(".,;/") for url in re.findall(r"https?://[^\s<>)\]]+", text)}


class CitationMismatch(ValueError):
    def __init__(self, cited):
        super().__init__("답변의 링크를 검색 출처와 대조할 수 없습니다.")
        self.cited = sorted(cited)


def source_page(url):
    # Tracking parameters and in-page anchors are not separate source documents.
    parts = urlsplit(url)
    query = "&".join(p for p in parts.query.split("&") if not p.lower().startswith("utm_"))
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), query, ""))


def extract_web(response, required_urls=(), *, allow_weather=False):
    calls = [
        item
        for item in response.get("output", [])
        if item.get("type") == "web_search_call" and item.get("status") == "completed"
    ]
    if not calls:
        raise ValueError("실제 웹 검색이 완료되지 않았습니다.")
    opened = {call.get("action", {}).get("url") for call in calls if call.get("action", {}).get("type") == "open_page"}
    opened_pages = {source_page(url) for url in opened if safe_url(url)}
    missing = [url for url in required_urls if source_page(url) not in opened_pages]
    if missing:
        raise ValueError("지정 URL의 직접 열람을 확인할 수 없습니다: " + ", ".join(missing))
    weather_feed = allow_weather and any(
        source == "oai-weather" or isinstance(source, dict) and "oai-weather" in source.values()
        for call in calls
        for source in ((call.get("action") or {}).get("sources") or [])
    )
    parts, sources = [], []
    for item in response.get("output", []):
        for part in item.get("content", []):
            if part.get("type") != "output_text":
                continue
            body = part["text"]
            annotations = sorted(part.get("annotations", []), key=lambda a: a.get("end_index", 0), reverse=True)
            for note in annotations:
                url = note.get("url")
                if note.get("type") == "url_citation" and safe_url(url):
                    pos = min(max(note.get("end_index", len(body)), 0), len(body))
                    start = max(0, min(note.get("start_index", pos), pos))
                    if not any(source_page(link) == source_page(url) for link in cited_urls(body[start:pos])):
                        body = body[:pos] + f" [출처](<{url}>)" + body[pos:]
                    sources.append(url)
            parts.append(body)
    cited = set(sources)
    cited_pages = {source_page(url) for url in sources}
    if any(source_page(url) not in cited_pages for url in required_urls):
        raise ValueError("지정 페이지의 내용을 뒷받침하는 직접 인용을 확인하지 못했습니다.")
    if not parts or not sources and not weather_feed:
        raise ValueError("웹 검색 결과에서 인용 가능한 근거를 확인하지 못했습니다.")
    answer = "\n".join(parts)
    verified = set(cited)
    for call in calls:
        for source in (call.get("action") or {}).get("sources") or []:
            if isinstance(source, dict) and safe_url(source.get("url")):
                verified.add(source["url"])
    pages = {source_page(url): url for url in sorted(verified)}

    def verified_link(match):
        raw = match[0]
        link = raw.rstrip(".,;")
        if link in verified:
            return raw
        target = pages.get(source_page(link))
        if target is None:
            raise CitationMismatch(cited)
        return target + raw[len(link) :]

    answer = re.sub(r"https?://[^\s<>)\]]+", verified_link, answer)
    # The search model can append a domain citation immediately after its own Markdown link.
    answer = re.sub(
        r"(\[[^\]\n]+\]\(<?(https?://[^\s<>()]+)>?\))\s+\(\[[^\]\n]+\]\(<?\2>?\)\)",
        r"\1",
        answer,
    )
    paragraphs = []
    linked = set()
    for paragraph in answer.split("\n\n"):
        links = {source_page(url) + "#" + urlsplit(url).fragment for url in cited_urls(paragraph)}
        only_link = re.fullmatch(
            r"(?:공식 원문|원문|출처|Source)?[ :：]*\[[^\]\n]+\]\(<?https?://[^\s<>()]+>?\)", paragraph.strip(), re.I
        )
        if not (only_link and links and links <= linked):
            paragraphs.append(paragraph)
        linked.update(links)
    answer = "\n\n".join(paragraphs)
    if weather_feed:
        answer += "\n출처 · OpenAI 실시간 날씨 피드 (oai-weather)"
    return {
        "text": answer,
        "urls": list(dict.fromkeys(sorted(sources, key=answer.find))),
        "feeds": ["oai-weather"] if weather_feed else [],
    }


class Models:
    def __init__(self, settings: Settings):
        self.config = settings
        self.client = AsyncOpenAI(api_key=settings.api_key, timeout=settings.timeout, max_retries=0)

    async def text(self, model, effort, instructions, data, *, limit=2000, schema=None, timeout=None):
        params = dict(
            model=model,
            reasoning={"effort": effort},
            instructions=instructions,
            input=data,
            max_output_tokens=limit,
            store=False,
        )
        if schema:
            params["text"] = {"format": {"type": "json_schema", "name": "decision", "strict": True, "schema": schema}}
        started = time.monotonic()
        result = await self.client.responses.create(**params, timeout=timeout or self.config.timeout)
        usage = result.usage
        logging.getLogger(__name__).info(
            "Responses model=%s effort=%s input=%s output=%s seconds=%.2f",
            model,
            effort,
            getattr(usage, "input_tokens", None),
            getattr(usage, "output_tokens", None),
            time.monotonic() - started,
        )
        if result.status != "completed" or not result.output_text.strip():
            reason = getattr(result.incomplete_details, "reason", None) or result.status
            raise ValueError(
                f"완성된 모델 응답을 받지 못했습니다 ({reason}, 출력 {getattr(usage, 'output_tokens', 0)}토큰)."
            )
        return json.loads(result.output_text) if schema else result.output_text

    async def discover(self, model, effort, instructions, data):
        response = await self.client.responses.create(
            model=model,
            instructions=instructions,
            input=data,
            store=False,
            reasoning={"effort": effort},
            tools=[{"type": "web_search", "external_web_access": True}],
            tool_choice="required",
            max_tool_calls=4,
            max_output_tokens=4000,
            include=["web_search_call.action.sources"],
        )
        if response.status != "completed":
            raise ValueError("웹 검색이 완료되지 않았습니다.")
        return response.model_dump()

    async def search(self, model, effort, instructions, data, urls=(), *, weather=False):
        async def query(prompt, payload):
            response = await self.discover(model, effort, prompt, payload)
            return extract_web(response, urls, allow_weather=weather)

        try:
            return await query(instructions, data)
        except CitationMismatch as mismatch:
            # Discard the previous prose and independently verify the sources once.
            logging.getLogger(__name__).info("재검색: 검색 출처와 본문 URL 불일치")
            return await query(
                instructions + " 이전 답안에 대조되지 않는 링크가 있었다. 출처 후보를 다시 열어 확인하고 "
                "결론만 간결히 쓰며 근거는 웹 도구의 인용 주석으로 제공한다. URL을 직접 작성하지 않는다.",
                json.dumps({"request": data, "source_candidates": mismatch.cited}, ensure_ascii=False),
            )

    async def compose(self, model, effort, instructions, data, corrections: asyncio.Queue, *, limit, timeout):
        """변경 번호는 API가 실제로 이어 쓴 후속 응답에만 부여한다."""
        headers = {"Authorization": "Bearer " + self.config.api_key}
        async with asyncio.timeout(timeout), aiohttp.ClientSession(headers=headers) as session:
            async with session.ws_connect("wss://api.openai.com/v1/responses", max_msg_size=16 * 1024 * 1024) as ws:
                await ws.send_json(
                    {
                        "type": "response.create",
                        "model": model,
                        "reasoning": {"effort": effort},
                        "instructions": instructions,
                        "input": data,
                        "store": False,
                        "max_output_tokens": limit,
                    }
                )
                parent, pending, applied = None, None, None
                read = asyncio.create_task(ws.receive_json())
                update = None
                try:
                    while True:
                        if parent and pending is None and update is None:
                            update = asyncio.create_task(corrections.get())
                        ready, _ = await asyncio.wait(
                            [read, update] if update else [read], return_when=asyncio.FIRST_COMPLETED
                        )
                        if update in ready:
                            pending, instruction = update.result()
                            update = None
                            await ws.send_json(
                                {"type": "response.steer", "previous_response_id": parent, "input": instruction}
                            )
                        if read not in ready:
                            continue
                        event = read.result()
                        name = event.get("type")
                        if name in {
                            "response.created",
                            "response.steer.accepted",
                            "response.completed",
                            "response.incomplete",
                            "response.steer.failed",
                            "error",
                        }:
                            logging.getLogger(__name__).info(
                                "Responses WS event=%s response=%s", name, (event.get("response") or {}).get("id")
                            )
                        result = event.get("response", {})
                        if name == "response.created":
                            if parent is not None and pending is not None and result["id"] != parent:
                                applied, pending = pending, None
                            parent = result["id"]
                        elif name == "response.completed" and pending is None and result["id"] == parent:
                            answer = "\n".join(
                                p["text"]
                                for item in result["output"]
                                for p in item.get("content", [])
                                if p["type"] == "output_text"
                            )
                            if not answer.strip():
                                raise ValueError("응답 본문을 확인하지 못했습니다.")
                            return answer, applied
                        elif name in {"error", "response.failed", "response.steer.failed"}:
                            raise ValueError("생성 연결을 다시 시작해야 합니다.")
                        elif (
                            name == "response.incomplete"
                            and (result.get("incomplete_details") or {}).get("reason") != "steered"
                        ):
                            raise ValueError("응답 생성이 중단됐습니다.")
                        read = asyncio.create_task(ws.receive_json())
                finally:
                    tasks = [task for task in (read, update) if task]
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
