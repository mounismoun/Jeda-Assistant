from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class PageContent:
    url: str
    final_url: str
    title: str
    text: str
    success: bool
    error: str = ""


class ReadableHtmlParser(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "svg", "canvas", "nav", "footer", "header", "aside"}
    BLOCK_TAGS = {"p", "br", "div", "section", "article", "main", "li", "tr", "h1", "h2", "h3", "h4"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        if tag == "title":
            self.in_title = True
        if tag in self.BLOCK_TAGS and not self.skip_depth:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self.in_title = False
        if tag in self.BLOCK_TAGS and not self.skip_depth:
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        cleaned = data.strip()
        if not cleaned:
            return
        if self.in_title:
            self.title_parts.append(cleaned)
        if not self.skip_depth:
            self.text_parts.append(cleaned)

    @property
    def title(self) -> str:
        return normalize_text(" ".join(self.title_parts))

    @property
    def text(self) -> str:
        text = "\n".join(part for part in self.text_parts if part.strip())
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return normalize_text(text)


class WebPageReader:
    def __init__(self, *, timeout_seconds: float = 8, max_bytes: int = 1024 * 1024, max_chars: int = 6000) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self.max_chars = max_chars

    def read(self, url: str) -> PageContent:
        target_url = normalize_naver_blog_url(url)
        try:
            request = urllib.request.Request(
                target_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; SleepGPTBot/0.1; +https://localhost)",
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                content_type = str(response.headers.get("Content-Type", "")).lower()
                if "html" not in content_type:
                    return PageContent(
                        url=url,
                        final_url=str(response.geturl()),
                        title="",
                        text="",
                        success=False,
                        error="HTML 응답이 아님",
                    )
                raw = response.read(self.max_bytes + 1)
                if len(raw) > self.max_bytes:
                    raw = raw[: self.max_bytes]
                encoding = response.headers.get_content_charset() or "utf-8"
                html = raw.decode(encoding, errors="replace")
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            return PageContent(url=url, final_url=target_url, title="", text="", success=False, error=str(error))

        parser = ReadableHtmlParser()
        parser.feed(html)
        text = parser.text[: self.max_chars].strip()
        if not text:
            return PageContent(
                url=url,
                final_url=target_url,
                title=parser.title,
                text="",
                success=False,
                error="본문 텍스트 없음",
            )
        return PageContent(url=url, final_url=target_url, title=parser.title, text=text, success=True)


def normalize_naver_blog_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower() != "blog.naver.com":
        return url
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 2 and parts[1].isdigit():
        return f"https://m.blog.naver.com/{parts[0]}/{parts[1]}"
    return url


def normalize_text(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    return re.sub(r"\n\s+", "\n", value).strip()
