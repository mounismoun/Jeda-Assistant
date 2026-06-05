from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    category: str
    source: str = "naver"
    published_at: str | None = None


class NaverSearchProvider:
    BASE_URL = "https://openapi.naver.com/v1/search"
    SUPPORTED_CATEGORIES = {"webkr", "news", "blog", "shop"}

    def __init__(
        self,
        *,
        client_id: str | None,
        client_secret: str | None,
        timeout_seconds: float = 10,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout_seconds = timeout_seconds

    def search(
        self,
        *,
        query: str,
        category: str = "webkr",
        display: int = 5,
        start: int = 1,
        sort: str = "sim",
    ) -> list[SearchResult]:
        if not self.client_id or not self.client_secret:
            raise RuntimeError("NAVER_SEARCH_CLIENT_ID와 NAVER_SEARCH_CLIENT_SECRET 환경 변수가 필요합니다.")
        if category not in self.SUPPORTED_CATEGORIES:
            category = "webkr"
        params = urllib.parse.urlencode(
            {
                "query": query,
                "display": max(1, min(int(display), 20)),
                "start": max(1, int(start)),
                "sort": sort,
            }
        )
        request = urllib.request.Request(
            f"{self.BASE_URL}/{category}.json?{params}",
            headers={
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret,
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [normalize_naver_item(item, category=category) for item in payload.get("items", [])]


def normalize_naver_item(item: dict[str, Any], *, category: str) -> SearchResult:
    title = clean_naver_text(str(item.get("title", "")))
    snippet = clean_naver_text(str(item.get("description", "")))
    url = str(item.get("link") or item.get("originallink") or "")
    published_at = str(item.get("pubDate") or item.get("postdate") or "") or None
    if category == "shop":
        price = str(item.get("lprice") or "").strip()
        mall = clean_naver_text(str(item.get("mallName", "")))
        extras = []
        if price:
            extras.append(f"최저가 {price}원")
        if mall:
            extras.append(mall)
        if extras:
            snippet = f"{snippet} ({', '.join(extras)})".strip()
    return SearchResult(
        title=title,
        url=url,
        snippet=snippet,
        category=category,
        published_at=published_at,
    )


def clean_naver_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    replacements = {
        "&quot;": '"',
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&#39;": "'",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return re.sub(r"\s+", " ", value).strip()
