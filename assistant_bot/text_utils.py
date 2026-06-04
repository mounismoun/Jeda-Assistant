from __future__ import annotations

import math
import re


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


def split_discord_message(text: str, limit: int = 1900) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    remaining = text.strip()

    while remaining:
        if len(remaining) <= limit:
            parts.append(remaining)
            break

        cut = max(
            remaining.rfind("\n\n", 0, limit),
            remaining.rfind("\n", 0, limit),
            remaining.rfind(". ", 0, limit),
        )
        if cut < limit * 0.5:
            cut = limit

        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()

    return parts


def strip_bot_mentions(content: str, bot_id: int) -> str:
    return re.sub(rf"<@!?{bot_id}>", "", content).strip()

