from __future__ import annotations

import re

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope, ExecutionContext, RoutingResult
from assistant_bot.stores import ConversationStore

from .agents.common import compact_preview, format_conversation_context, format_conversation_location


def build_execution_context(
    *,
    config: Config,
    conversations: ConversationStore,
    scope: ConversationScope,
    user_text: str,
    route: RoutingResult | None = None,
) -> ExecutionContext:
    recent_rows = conversations.recent_messages(
        scope.conversation_id,
        limit=config.agent_context_messages,
    )
    recent_context = format_conversation_context(recent_rows)
    latest_summary = conversations.latest_summary(scope.conversation_id) or ""
    cross_location_context = build_cross_location_context(
        config=config,
        conversations=conversations,
        scope=scope,
    )
    focused_context = build_focused_context(
        user_text=user_text,
        latest_summary=latest_summary,
        recent_context=recent_context,
        max_chars=config.focused_context_max_chars,
    )
    return ExecutionContext(
        latest_summary=latest_summary,
        recent_context=recent_context,
        focused_context=focused_context,
        cross_location_context=cross_location_context,
        route_reason=route.reason if route else "",
        route_search_need_score=route.search_need_score if route else 0,
        route_search_decision=route.search_decision if route else "not_needed",
        route_search_reason=route.search_reason if route else "",
    )


def build_router_context(
    *,
    config: Config,
    conversations: ConversationStore,
    scope: ConversationScope,
) -> str:
    recent_context = format_conversation_context(
        conversations.recent_messages(scope.conversation_id, limit=config.router_context_messages)
    )
    latest_summary = conversations.latest_summary(scope.conversation_id) or ""
    cross_location_context = build_cross_location_context(
        config=config,
        conversations=conversations,
        scope=scope,
    )
    return "\n\n".join(
        part
        for part in [
            f"이전 요약:\n{latest_summary}" if latest_summary else "",
            f"최근 대화:\n{recent_context}" if recent_context else "",
            f"같은 사용자 다른 위치 최근 맥락:\n{cross_location_context}" if cross_location_context else "",
        ]
        if part
    )


def build_cross_location_context(
    *,
    config: Config,
    conversations: ConversationStore,
    scope: ConversationScope,
) -> str:
    if config.user_context_conversations <= 0 or config.user_context_max_chars <= 0:
        return ""
    rows = conversations.recent_conversations_for_user(
        user_id=scope.user_id,
        limit=config.user_context_conversations + 1,
    )
    lines: list[str] = []
    for row in rows:
        conversation_id = str(row["conversation_id"])
        if conversation_id == scope.conversation_id:
            continue
        summary = conversations.latest_summary(conversation_id)
        latest_content = str(row.get("latest_content") or "")
        source = "요약" if summary else "최근 메시지"
        preview = compact_preview(summary or latest_content, limit=160)
        location = format_conversation_location(conversation_id)
        lines.append(f"- {location} · {source}: {preview}")
        if len(lines) >= config.user_context_conversations:
            break
    return trim_context_lines(lines, max_chars=config.user_context_max_chars)


def build_focused_context(
    *,
    user_text: str,
    latest_summary: str,
    recent_context: str,
    max_chars: int,
) -> str:
    if max_chars <= 0:
        return ""
    lines = [line.strip() for line in recent_context.splitlines() if line.strip()]
    if not lines and not latest_summary:
        return ""

    keyword_pattern = focused_keyword_pattern(user_text)
    selected: list[str] = []
    if is_follow_up_question(user_text):
        selected.extend(lines[-4:])
    else:
        selected.extend(line for line in lines if keyword_pattern.search(line))
        if not selected:
            selected.extend(lines[-2:])

    if latest_summary and keyword_pattern.search(latest_summary):
        selected.insert(0, f"summary: {latest_summary}")

    deduped: list[str] = []
    seen: set[str] = set()
    for line in selected:
        if line in seen:
            continue
        seen.add(line)
        deduped.append(line)

    return trim_context_lines(deduped, max_chars=max_chars)


def focused_keyword_pattern(user_text: str) -> re.Pattern[str]:
    tokens = [
        token
        for token in re.findall(r"[0-9A-Za-z가-힣]{2,}", user_text.casefold())
        if token not in STOPWORDS
    ]
    if not tokens:
        return re.compile(r"a^")
    return re.compile("|".join(re.escape(token) for token in tokens), flags=re.IGNORECASE)


def is_follow_up_question(user_text: str) -> bool:
    normalized = user_text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    follow_up_markers = [
        "그",
        "그거",
        "그 사람",
        "그 문서",
        "방금",
        "아까",
        "직전",
        "이어서",
        "임기",
        "언제까지",
        "취임",
        "나이",
        "출처",
        "근거",
        "자세히",
        "내부 내용",
        "latest",
        "previous",
    ]
    short_question = len(compact) <= 24 and any(marker in compact for marker in ["?", "뭐", "누구", "언제", "어디"])
    return short_question or any(marker in normalized or marker in compact for marker in follow_up_markers)


def trim_context_lines(lines: list[str], *, max_chars: int) -> str:
    kept: list[str] = []
    total = 0
    for line in reversed(lines):
        addition = len(line) + (1 if kept else 0)
        if kept and total + addition > max_chars:
            break
        if not kept and len(line) > max_chars:
            kept.append(line[-max_chars:])
            break
        kept.append(line)
        total += addition
    return "\n".join(reversed(kept)).strip()


STOPWORDS = {
    "그리고",
    "근데",
    "그럼",
    "지금",
    "오늘",
    "관련",
    "알려줘",
    "보여줘",
    "해줘",
    "해주세요",
    "언제",
    "까지",
    "누구",
    "뭐야",
}
