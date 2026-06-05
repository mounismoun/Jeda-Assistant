from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RouteIntent = Literal[
    "chat",
    "help",
    "status",
    "current_time",
    "cancel_pending",
    "remember",
    "recall",
    "list_memory",
    "update_memory",
    "delete_memory",
    "restore_memory",
    "analyze_document",
    "weather",
    "web_search",
    "web_url",
    "confirm_web_search",
    "reset_context",
    "manage_task",
    "manage_reminder",
    "daily_briefing",
    "unsupported",
]
Difficulty = Literal["easy", "medium", "hard"]
Preference = Literal["fast", "cheap", "precise", "deep", "balanced"]


@dataclass(frozen=True)
class ConversationScope:
    conversation_id: str
    channel_id: str
    user_id: str
    guild_id: str | None


@dataclass(frozen=True)
class RoutingResult:
    intent: RouteIntent
    confidence: float
    reason: str
    search_need_score: int = 0
    search_decision: str = "not_needed"
    search_reason: str = ""


@dataclass(frozen=True)
class ExecutionContext:
    latest_summary: str = ""
    recent_context: str = ""
    focused_context: str = ""
    cross_location_context: str = ""
    route_reason: str = ""
    route_search_need_score: int = 0
    route_search_decision: str = "not_needed"
    route_search_reason: str = ""

    def for_router(self) -> str:
        return join_context_parts(
            ("이전 요약", self.latest_summary),
            ("최근 대화", self.recent_context),
            ("같은 사용자 다른 위치 최근 맥락", self.cross_location_context),
        )

    def for_agent(self) -> str:
        return join_context_parts(
            ("이전 요약", self.latest_summary),
            ("관련 최근 맥락", self.focused_context),
            ("같은 사용자 다른 위치 최근 맥락", self.cross_location_context),
        )

    def for_response(self, *, max_chars: int) -> str:
        text = join_context_parts(
            ("이전 요약", self.latest_summary),
            ("관련 최근 맥락", self.focused_context),
            ("같은 사용자 다른 위치 최근 맥락", self.cross_location_context),
        )
        return text[: max(0, max_chars)].rstrip()


def join_context_parts(*parts: tuple[str, str]) -> str:
    return "\n\n".join(f"{label}:\n{value}" for label, value in parts if value.strip())


@dataclass(frozen=True)
class ModelChoice:
    difficulty: Difficulty
    model: str
    reason: str


@dataclass(frozen=True)
class ExtractedAttachment:
    filename: str
    content_type: str | None
    text: str


@dataclass(frozen=True)
class PreparedAttachment:
    filename: str
    content_type: str | None
    text: str
    size: int
    extraction_method: str
    used_vision_ocr: bool = False


@dataclass(frozen=True)
class MemorySearchResult:
    id: int
    kind: Literal["memory", "document"]
    title: str
    text: str
    score: float
    source_message_id: str | None
    created_at: str
    source_location: str = "DM"


@dataclass(frozen=True)
class MemoryListItem:
    id: int
    kind: Literal["memory", "document"]
    title: str
    created_at: str
    detail: str
    source_location: str


@dataclass(frozen=True)
class MemoryDetail:
    id: int
    kind: Literal["memory", "document"]
    title: str
    text: str
    created_at: str
    source_message_id: str | None
    chunk_count: int = 0
    source_location: str = "DM"


@dataclass(frozen=True)
class PendingAttachmentRequest:
    id: int
    conversation_id: str
    channel_id: str
    message_id: str
    user_id: str
    guild_id: str | None
    filenames: list[str]
    created_at: str


@dataclass(frozen=True)
class PendingMemoryDeletion:
    id: int
    conversation_id: str
    channel_id: str
    message_id: str
    user_id: str
    guild_id: str | None
    memory_count: int
    document_count: int
    mode: str
    memory_ids: list[int]
    document_ids: list[int]
    created_at: str


@dataclass(frozen=True)
class PendingMemoryCapture:
    id: int
    conversation_id: str
    channel_id: str
    message_id: str
    user_id: str
    guild_id: str | None
    mode: str
    created_at: str


@dataclass(frozen=True)
class PendingWebSearchConfirmation:
    id: int
    conversation_id: str
    channel_id: str
    message_id: str
    user_id: str
    guild_id: str | None
    query_text: str
    search_need_score: int
    search_reason: str
    created_at: str


@dataclass(frozen=True)
class TaskItem:
    id: int
    user_id: str
    conversation_id: str
    channel_id: str | None
    title: str
    status: str
    priority: str
    due_at: str | None
    created_at: str
    completed_at: str | None = None
    reminder_sent_at: str | None = None
    deleted_at: str | None = None
    source_message_id: str | None = None
    source_location: str = "DM"


@dataclass(frozen=True)
class ReminderItem:
    id: int
    user_id: str
    conversation_id: str
    channel_id: str | None
    text: str
    remind_at: str
    created_at: str
    sent_at: str | None = None
    source_message_id: str | None = None
    source_location: str = "DM"
