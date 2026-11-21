from __future__ import annotations

import math
import re


def format_numeric_answer(request: str, answer: str) -> str:
    if not re.search(r"(?:숫자만(?:\s*(?:답해|적어|알려)(?:\s*줘)?)?|(?:number|digits) only)[.!\s]*$", request, re.I):
        return answer
    scalar = re.fullmatch(
        r"([+−-]?\d+(?:,\d{3})*(?:\.\d+)?)(?:\s*(?:시간|개월|분|초|일|년|명|개|대|원|회|건|쪽|%))?(?:입니다|이에요|예요)?[.]?",
        answer.strip().replace("**", "").strip("`").strip(),
    )
    return scalar[1] if scalar else answer


def chunk_text(text: str, max_chars: int = 1600, overlap_chars: int = 180) -> list[str]:
    normalized = re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n")).strip()
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(normalized):
        target_end = min(start + max_chars, len(normalized))
        end = target_end

        if target_end < len(normalized):
            candidates = [
                normalized.rfind("\n\n", start, target_end),
                normalized.rfind(". ", start, target_end),
                normalized.rfind("\n", start, target_end),
            ]
            best_break = max(candidates)
            if best_break > start + max_chars * 0.55:
                end = best_break + 1

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(normalized):
            break
        start = max(0, end - overlap_chars)

    return chunks


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for left, right in zip(a, b, strict=True):
        dot += left * right
        norm_a += left * left
        norm_b += right * right

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


_DISCORD_BREAK = re.compile(
    r"(?P<link>\[[^\]\n]*\]\(<?https?://[^\s)]+>?\)|https?://[^\s>)]+)"
    r"""|(?P<sentence>[.!?。！？]+[”’"'*)\]]*(?=\s|$))"""
    r"|(?P<space>[^\S\n]+)"
)


def _discord_cut(text: str, capacity: int) -> int:
    # Discord counts supplementary characters such as emoji as two UTF-16 units.
    window = text[:capacity].encode("utf-16-le")[: 2 * capacity]
    end = len(window.decode("utf-16-le", errors="ignore"))
    newline = text.rfind("\n", 0, end + 1)
    if newline > 0:
        return newline

    # Only a line longer than a whole message needs an internal break.
    sentence = space = 0
    for match in _DISCORD_BREAK.finditer(text):
        if match.start() >= end:
            break
        if match.lastgroup == "link":
            if match.start() and match.end() > end and len(match[0].encode("utf-16-le")) <= 2 * capacity:
                return sentence or match.start()
        elif match.lastgroup == "space":
            space = match.start()
        elif match.end() <= end:
            sentence = match.end()
    return sentence or space or end


def split_discord_message(text: str, limit: int = 1900) -> list[str]:
    def length(value):
        return len(value.encode("utf-16-le")) // 2

    if length(text) <= limit:
        return [text]
    if limit < 12:
        raise ValueError("메시지 분할 길이가 너무 작습니다.")

    parts, remaining, fence = [], text.strip(), None
    while remaining:
        prefix = "" if fence is None else "```" + fence + "\n"
        capacity = limit - length(prefix)
        if length(remaining) <= capacity:
            parts.append(prefix + remaining)
            break
        # Reserve room for a closing fence only if the selected lines actually need one.
        for budget in (capacity, capacity - 4):
            cut = _discord_cut(remaining, budget)
            body = remaining[:cut].rstrip()
            next_fence = fence
            for marker in re.finditer(r"(?m)^[ \t]*```([^\n`]*)", body):
                next_fence = marker[1].strip()[: min(32, (limit - 10) // 2)] if next_fence is None else None
            suffix = "\n```" if next_fence is not None else ""
            if length(body + suffix) <= capacity:
                break
        if body:
            parts.append(prefix + body + suffix)
        fence = next_fence
        tail = remaining[cut:]
        remaining = tail.lstrip("\r\n") if tail.startswith(("\r", "\n")) else tail.lstrip()
    return parts


def strip_bot_mentions(content: str, bot_id: int) -> str:
    return re.sub(rf"<@!?{bot_id}>", "", content).strip()
