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
