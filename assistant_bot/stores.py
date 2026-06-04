from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime, timedelta

from assistant_bot.models import (
    ConversationScope,
    MemoryDetail,
    MemoryListItem,
    MemorySearchResult,
    PendingAttachmentRequest,
    PendingMemoryDeletion,
    TaskItem,
)
from assistant_bot.openai_service import OpenAIService
from assistant_bot.text_utils import chunk_text, cosine_similarity

TASK_COLUMNS = """
id, user_id, guild_id, conversation_id, channel_id, title, status, priority,
due_at, source_message_id, created_at, completed_at, reminder_sent_at, deleted_at
"""


class AgentLogStore:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(
        self,
        *,
        conversation_id: str,
        agent: str,
        intent: str | None = None,
        difficulty: str | None = None,
        model: str | None = None,
        reason: str | None = None,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO agent_logs (conversation_id, agent, intent, difficulty, model, reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (conversation_id, agent, intent, difficulty, model, reason),
        )
        self.connection.commit()


class ConversationStore:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add_message(
        self,
        *,
        conversation_id: str,
        role: str,
        user_id: str | None,
        content: str,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO conversation_messages (conversation_id, role, user_id, content)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, role, user_id, content),
        )
        self.connection.commit()

    def recent_messages(self, conversation_id: str, limit: int = 24) -> list[sqlite3.Row]:
        rows = self.connection.execute(
            """
            SELECT role, content, created_at
            FROM conversation_messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        ).fetchall()
        return list(reversed(rows))

    def latest_user_message(self, *, conversation_id: str, user_id: str) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT role, content, created_at
            FROM conversation_messages
            WHERE conversation_id = ?
              AND role = 'user'
              AND user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (conversation_id, user_id),
        ).fetchone()

    def latest_summary(self, conversation_id: str) -> str | None:
        row = self.connection.execute(
            """
            SELECT summary
            FROM conversation_summaries
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (conversation_id,),
        ).fetchone()
        return str(row["summary"]) if row else None

    def add_summary(self, conversation_id: str, summary: str) -> None:
        self.connection.execute(
            """
            INSERT INTO conversation_summaries (conversation_id, summary)
            VALUES (?, ?)
            """,
            (conversation_id, summary),
        )
        self.connection.commit()

    def recent_char_count(self, conversation_id: str, limit: int = 80) -> int:
        return sum(len(row["content"]) for row in self.recent_messages(conversation_id, limit))

    def clear_conversation(self, conversation_id: str) -> dict[str, int]:
        message_cursor = self.connection.execute(
            """
            DELETE FROM conversation_messages
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        )
        summary_cursor = self.connection.execute(
            """
            DELETE FROM conversation_summaries
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        )
        self.connection.commit()
        return {
            "messages": int(message_cursor.rowcount),
            "summaries": int(summary_cursor.rowcount),
        }

    def recent_conversations_for_user(self, *, user_id: str, limit: int = 5) -> list[dict[str, object]]:
        max_items = max(1, limit)
        rows = self.connection.execute(
            """
            SELECT conversation_id, COUNT(*) AS user_message_count, MAX(created_at) AS latest_user_message_at
            FROM conversation_messages
            WHERE user_id = ?
            GROUP BY conversation_id
            ORDER BY latest_user_message_at DESC, conversation_id ASC
            LIMIT ?
            """,
            (user_id, max_items),
        ).fetchall()
        conversations: list[dict[str, object]] = []
        for row in rows:
            conversation_id = str(row["conversation_id"])
            latest = self.connection.execute(
                """
                SELECT role, user_id, content, created_at
                FROM conversation_messages
                WHERE conversation_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (conversation_id,),
            ).fetchone()
            summary_count = self.connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM conversation_summaries
                WHERE conversation_id = ?
                """,
                (conversation_id,),
            ).fetchone()
            conversations.append(
                {
                    "conversation_id": conversation_id,
                    "user_message_count": int(row["user_message_count"]),
                    "latest_user_message_at": str(row["latest_user_message_at"]),
                    "latest_role": str(latest["role"]) if latest else None,
                    "latest_content": str(latest["content"]) if latest else "",
                    "latest_message_at": str(latest["created_at"]) if latest else None,
                    "summary_count": int(summary_count["count"]) if summary_count else 0,
                }
            )
        return conversations


class PendingAttachmentStore:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(
        self,
        *,
        scope: ConversationScope,
        message_id: str,
        filenames: list[str],
    ) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO pending_attachment_requests (
              conversation_id, channel_id, message_id, user_id, guild_id, filenames_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                scope.conversation_id,
                scope.channel_id,
                message_id,
                scope.user_id,
                scope.guild_id,
                json.dumps(filenames, ensure_ascii=False),
            ),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def latest(self, *, scope: ConversationScope, ttl_minutes: int | None = None) -> PendingAttachmentRequest | None:
        if ttl_minutes is not None:
            self.resolve_expired(scope=scope, ttl_minutes=ttl_minutes)
        row = self.connection.execute(
            """
            SELECT id, conversation_id, channel_id, message_id, user_id, guild_id, filenames_json, created_at
            FROM pending_attachment_requests
            WHERE resolved_at IS NULL
              AND conversation_id = ?
              AND user_id = ?
              AND (guild_id IS NULL OR guild_id = ?)
            ORDER BY id DESC
            LIMIT 1
            """,
            (scope.conversation_id, scope.user_id, scope.guild_id),
        ).fetchone()
        if not row:
            return None
        return PendingAttachmentRequest(
            id=int(row["id"]),
            conversation_id=str(row["conversation_id"]),
            channel_id=str(row["channel_id"]),
            message_id=str(row["message_id"]),
            user_id=str(row["user_id"]),
            guild_id=str(row["guild_id"]) if row["guild_id"] else None,
            filenames=json.loads(row["filenames_json"]),
            created_at=str(row["created_at"]),
        )

    def unresolved_count(self, *, scope: ConversationScope, ttl_minutes: int | None = None) -> int:
        if ttl_minutes is not None:
            self.resolve_expired(scope=scope, ttl_minutes=ttl_minutes)
        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM pending_attachment_requests
            WHERE resolved_at IS NULL
              AND conversation_id = ?
              AND user_id = ?
              AND (guild_id IS NULL OR guild_id = ?)
            """,
            (scope.conversation_id, scope.user_id, scope.guild_id),
        ).fetchone()
        return int(row["count"])

    def resolve(self, request_id: int) -> None:
        self.connection.execute(
            """
            UPDATE pending_attachment_requests
            SET resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (request_id,),
        )
        self.connection.commit()

    def resolve_latest(
        self,
        *,
        scope: ConversationScope,
        ttl_minutes: int | None = None,
    ) -> PendingAttachmentRequest | None:
        request = self.latest(scope=scope, ttl_minutes=ttl_minutes)
        if request is None:
            return None
        self.resolve(request.id)
        return request

    def resolve_expired(self, *, scope: ConversationScope, ttl_minutes: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(minutes=ttl_minutes)
        cutoff_text = cutoff.strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.connection.execute(
            """
            UPDATE pending_attachment_requests
            SET resolved_at = CURRENT_TIMESTAMP
            WHERE resolved_at IS NULL
              AND conversation_id = ?
              AND user_id = ?
              AND (guild_id IS NULL OR guild_id = ?)
              AND created_at < ?
            """,
            (scope.conversation_id, scope.user_id, scope.guild_id, cutoff_text),
        )
        self.connection.commit()
        return int(cursor.rowcount)


class PendingMemoryDeletionStore:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, *, scope: ConversationScope, message_id: str, memory_count: int, document_count: int) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO pending_memory_deletions (
              conversation_id, channel_id, message_id, user_id, guild_id, memory_count, document_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scope.conversation_id,
                scope.channel_id,
                message_id,
                scope.user_id,
                scope.guild_id,
                memory_count,
                document_count,
            ),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def latest(self, *, scope: ConversationScope, ttl_minutes: int | None = None) -> PendingMemoryDeletion | None:
        if ttl_minutes is not None:
            self.resolve_expired(scope=scope, ttl_minutes=ttl_minutes)
        row = self.connection.execute(
            """
            SELECT
              id, conversation_id, channel_id, message_id, user_id, guild_id,
              memory_count, document_count, created_at
            FROM pending_memory_deletions
            WHERE resolved_at IS NULL
              AND conversation_id = ?
              AND user_id = ?
              AND (guild_id IS NULL OR guild_id = ?)
            ORDER BY id DESC
            LIMIT 1
            """,
            (scope.conversation_id, scope.user_id, scope.guild_id),
        ).fetchone()
        if not row:
            return None
        return PendingMemoryDeletion(
            id=int(row["id"]),
            conversation_id=str(row["conversation_id"]),
            channel_id=str(row["channel_id"]),
            message_id=str(row["message_id"]),
            user_id=str(row["user_id"]),
            guild_id=str(row["guild_id"]) if row["guild_id"] else None,
            memory_count=int(row["memory_count"]),
            document_count=int(row["document_count"]),
            created_at=str(row["created_at"]),
        )

    def unresolved_count(self, *, scope: ConversationScope, ttl_minutes: int | None = None) -> int:
        if ttl_minutes is not None:
            self.resolve_expired(scope=scope, ttl_minutes=ttl_minutes)
        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM pending_memory_deletions
            WHERE resolved_at IS NULL
              AND conversation_id = ?
              AND user_id = ?
              AND (guild_id IS NULL OR guild_id = ?)
            """,
            (scope.conversation_id, scope.user_id, scope.guild_id),
        ).fetchone()
        return int(row["count"])

    def resolve(self, request_id: int) -> None:
        self.connection.execute(
            """
            UPDATE pending_memory_deletions
            SET resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (request_id,),
        )
        self.connection.commit()

    def resolve_latest(
        self,
        *,
        scope: ConversationScope,
        ttl_minutes: int | None = None,
    ) -> PendingMemoryDeletion | None:
        request = self.latest(scope=scope, ttl_minutes=ttl_minutes)
        if request is None:
            return None
        self.resolve(request.id)
        return request

    def resolve_expired(self, *, scope: ConversationScope, ttl_minutes: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(minutes=ttl_minutes)
        cutoff_text = cutoff.strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.connection.execute(
            """
            UPDATE pending_memory_deletions
            SET resolved_at = CURRENT_TIMESTAMP
            WHERE resolved_at IS NULL
              AND conversation_id = ?
              AND user_id = ?
              AND (guild_id IS NULL OR guild_id = ?)
              AND created_at < ?
            """,
            (scope.conversation_id, scope.user_id, scope.guild_id, cutoff_text),
        )
        self.connection.commit()
        return int(cursor.rowcount)


class TaskStore:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(
        self,
        *,
        scope: ConversationScope,
        title: str,
        priority: str = "normal",
        due_at: str | None = None,
        source_message_id: str | None = None,
    ) -> int:
        created_at = current_timestamp()
        cursor = self.connection.execute(
            """
            INSERT INTO tasks (
              user_id, guild_id, conversation_id, channel_id, title, priority, due_at, source_message_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scope.user_id,
                scope.guild_id,
                scope.conversation_id,
                scope.channel_id,
                title,
                normalize_task_priority(priority),
                due_at,
                source_message_id,
                created_at,
            ),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def find_open_duplicate(self, *, scope: ConversationScope, title: str) -> TaskItem | None:
        row = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
              AND LOWER(TRIM(title)) = LOWER(TRIM(?))
            ORDER BY id DESC
            LIMIT 1
            """,
            (scope.user_id, title),
        ).fetchone()
        return task_item_from_row(row) if row else None

    def get(self, *, scope: ConversationScope, task_id: int, include_deleted: bool = False) -> TaskItem | None:
        where = ["user_id = ?", "id = ?"]
        if not include_deleted:
            where.append("deleted_at IS NULL")
        row = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE {" AND ".join(where)}
            LIMIT 1
            """,
            (scope.user_id, task_id),
        ).fetchone()
        return task_item_from_row(row) if row else None

    def latest(self, *, scope: ConversationScope) -> TaskItem | None:
        row = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE deleted_at IS NULL
              AND user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (scope.user_id,),
        ).fetchone()
        return task_item_from_row(row) if row else None

    def latest_reminded_open(self, *, scope: ConversationScope) -> TaskItem | None:
        row = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND reminder_sent_at IS NOT NULL
              AND user_id = ?
            ORDER BY reminder_sent_at DESC, id DESC
            LIMIT 1
            """,
            (scope.user_id,),
        ).fetchone()
        return task_item_from_row(row) if row else None

    def list_open(self, *, scope: ConversationScope, limit: int = 10) -> list[TaskItem]:
        rows = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
            ORDER BY
              CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
              CASE WHEN due_at IS NULL THEN 1 ELSE 0 END,
              due_at ASC,
              id DESC
            LIMIT ?
            """,
            (scope.user_id, max(1, limit)),
        ).fetchall()
        return [task_item_from_row(row) for row in rows]

    def list_due(self, *, scope: ConversationScope, due_before: str, limit: int = 10) -> list[TaskItem]:
        due_cutoff = normalize_due_cutoff(due_before)
        rows = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
              AND due_at IS NOT NULL
              AND due_at <= ?
            ORDER BY
              CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
              due_at ASC,
              id DESC
            LIMIT ?
            """,
            (scope.user_id, due_cutoff, max(1, limit)),
        ).fetchall()
        return [task_item_from_row(row) for row in rows]

    def list_recent(
        self,
        *,
        user_id: str | None = None,
        status: str = "open",
        due_after: str | None = None,
        due_before: str | None = None,
        undated: bool = False,
        limit: int = 20,
    ) -> list[TaskItem]:
        where = ["deleted_at IS NULL"]
        params: list[object] = []
        if user_id:
            where.append("user_id = ?")
            params.append(user_id)
        if status != "all":
            where.append("status = ?")
            params.append(status)
        if undated:
            where.append("due_at IS NULL")
        elif due_after or due_before:
            where.append("due_at IS NOT NULL")
        if due_after:
            where.append("due_at >= ?")
            params.append(normalize_due_start(due_after))
        if due_before:
            where.append("due_at <= ?")
            params.append(normalize_due_cutoff(due_before))
        params.append(max(1, limit))
        rows = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE {" AND ".join(where)}
            ORDER BY
              CASE WHEN status = 'open' THEN 0 ELSE 1 END,
              CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
              CASE WHEN due_at IS NULL THEN 1 ELSE 0 END,
              due_at ASC,
              id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [task_item_from_row(row) for row in rows]

    def list_deleted(
        self,
        *,
        scope: ConversationScope | None = None,
        user_id: str | None = None,
        limit: int = 20,
    ) -> list[TaskItem]:
        where = ["deleted_at IS NOT NULL"]
        params: list[object] = []
        effective_user_id = scope.user_id if scope else user_id
        if effective_user_id:
            where.append("user_id = ?")
            params.append(effective_user_id)
        params.append(max(1, limit))
        rows = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE {" AND ".join(where)}
            ORDER BY deleted_at DESC, id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [task_item_from_row(row) for row in rows]

    def search(self, *, scope: ConversationScope, keyword: str, limit: int = 10) -> list[TaskItem]:
        cleaned_keyword = keyword.strip()
        if not cleaned_keyword:
            return []
        like = f"%{cleaned_keyword.replace('%', '').replace('_', '')}%"
        rows = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE deleted_at IS NULL
              AND user_id = ?
              AND title LIKE ?
            ORDER BY
              CASE WHEN status = 'open' THEN 0 ELSE 1 END,
              CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
              CASE WHEN due_at IS NULL THEN 1 ELSE 0 END,
              due_at ASC,
              id DESC
            LIMIT ?
            """,
            (scope.user_id, like, max(1, limit)),
        ).fetchall()
        return [task_item_from_row(row) for row in rows]

    def complete(self, *, scope: ConversationScope, task_ids: list[int]) -> int:
        if not task_ids:
            return 0
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
              AND id IN ({",".join("?" for _ in task_ids)})
            """,
            [scope.user_id, *task_ids],
        )
        self.connection.commit()
        return int(cursor.rowcount)

    def reopen(self, *, scope: ConversationScope, task_ids: list[int]) -> int:
        if not task_ids:
            return 0
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET status = 'open', completed_at = NULL, reminder_sent_at = NULL
            WHERE deleted_at IS NULL
              AND status = 'completed'
              AND user_id = ?
              AND id IN ({",".join("?" for _ in task_ids)})
            """,
            [scope.user_id, *task_ids],
        )
        self.connection.commit()
        return int(cursor.rowcount)

    def reopen_latest_completed(self, *, scope: ConversationScope) -> TaskItem | None:
        row = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE deleted_at IS NULL
              AND status = 'completed'
              AND user_id = ?
            ORDER BY completed_at DESC, id DESC
            LIMIT 1
            """,
            (scope.user_id,),
        ).fetchone()
        if row is None:
            return None
        item = task_item_from_row(row)
        self.reopen(scope=scope, task_ids=[item.id])
        return item

    def delete(self, *, scope: ConversationScope, task_ids: list[int]) -> int:
        if not task_ids:
            return 0
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE deleted_at IS NULL
              AND user_id = ?
              AND id IN ({",".join("?" for _ in task_ids)})
            """,
            [scope.user_id, *task_ids],
        )
        self.connection.commit()
        return int(cursor.rowcount)

    def restore(self, *, scope: ConversationScope, task_ids: list[int]) -> int:
        if not task_ids:
            return 0
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET deleted_at = NULL
            WHERE deleted_at IS NOT NULL
              AND user_id = ?
              AND id IN ({",".join("?" for _ in task_ids)})
            """,
            [scope.user_id, *task_ids],
        )
        self.connection.commit()
        return int(cursor.rowcount)

    def restore_latest_deleted(self, *, scope: ConversationScope) -> TaskItem | None:
        row = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE deleted_at IS NOT NULL
              AND user_id = ?
            ORDER BY deleted_at DESC, id DESC
            LIMIT 1
            """,
            (scope.user_id,),
        ).fetchone()
        if row is None:
            return None
        task = task_item_from_row(row)
        self.restore(scope=scope, task_ids=[task.id])
        return task

    def postpone(self, *, scope: ConversationScope, task_ids: list[int], due_at: str) -> int:
        if not task_ids:
            return 0
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET due_at = ?, reminder_sent_at = NULL
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
              AND id IN ({",".join("?" for _ in task_ids)})
            """,
            [due_at, scope.user_id, *task_ids],
        )
        self.connection.commit()
        return int(cursor.rowcount)

    def clear_due(self, *, scope: ConversationScope, task_ids: list[int]) -> int:
        if not task_ids:
            return 0
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET due_at = NULL, reminder_sent_at = NULL
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
              AND id IN ({",".join("?" for _ in task_ids)})
            """,
            [scope.user_id, *task_ids],
        )
        self.connection.commit()
        return int(cursor.rowcount)

    def rename(self, *, scope: ConversationScope, task_ids: list[int], title: str) -> int:
        if not task_ids:
            return 0
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET title = ?
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
              AND id IN ({",".join("?" for _ in task_ids)})
            """,
            [title, scope.user_id, *task_ids],
        )
        self.connection.commit()
        return int(cursor.rowcount)

    def set_priority(self, *, scope: ConversationScope, task_ids: list[int], priority: str) -> int:
        if not task_ids:
            return 0
        normalized_priority = normalize_task_priority(priority)
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET priority = ?
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
              AND id IN ({",".join("?" for _ in task_ids)})
            """,
            [normalized_priority, scope.user_id, *task_ids],
        )
        self.connection.commit()
        return int(cursor.rowcount)

    def stats(self, *, scope: ConversationScope) -> dict[str, int]:
        open_row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM tasks
            WHERE deleted_at IS NULL
              AND status = 'open'
              AND user_id = ?
            """,
            (scope.user_id,),
        ).fetchone()
        completed_row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM tasks
            WHERE deleted_at IS NULL
              AND status = 'completed'
              AND user_id = ?
            """,
            (scope.user_id,),
        ).fetchone()
        return {
            "open": int(open_row["count"]),
            "completed": int(completed_row["count"]),
        }

    def due_for_reminder(self, *, today: str, limit: int = 50, user_id: str | None = None) -> list[TaskItem]:
        due_cutoff = normalize_due_cutoff(today)
        where = [
            "deleted_at IS NULL",
            "status = 'open'",
            "due_at IS NOT NULL",
            "due_at <= ?",
            "reminder_sent_at IS NULL",
        ]
        params: list[object] = [due_cutoff]
        if user_id:
            where.append("user_id = ?")
            params.append(user_id)
        params.append(max(1, limit))
        rows = self.connection.execute(
            f"""
            SELECT {TASK_COLUMNS}
            FROM tasks
            WHERE {" AND ".join(where)}
            ORDER BY
              CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
              due_at ASC,
              id ASC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [task_item_from_row(row) for row in rows]

    def mark_reminded(self, task_id: int) -> None:
        self.connection.execute(
            """
            UPDATE tasks
            SET reminder_sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (task_id,),
        )
        self.connection.commit()


class MemoryStore:
    def __init__(self, connection: sqlite3.Connection, openai: OpenAIService) -> None:
        self.connection = connection
        self.openai = openai

    def find_duplicate_text_memory(self, *, scope: ConversationScope, text: str) -> MemoryDetail | None:
        normalized = normalize_memory_text(text)
        if not normalized:
            return None
        rows = self.connection.execute(
            """
            SELECT id, title, text, guild_id, source_message_id, created_at
            FROM user_memories
            WHERE deleted_at IS NULL
              AND user_id = ?
            ORDER BY id DESC
            """,
            (scope.user_id,),
        ).fetchall()
        for row in rows:
            if normalize_memory_text(str(row["text"])) != normalized:
                continue
            return MemoryDetail(
                id=int(row["id"]),
                kind="memory",
                title=str(row["title"]),
                text=str(row["text"]),
                created_at=str(row["created_at"]),
                source_message_id=str(row["source_message_id"]) if row["source_message_id"] else None,
                source_location=source_location(row["guild_id"]),
            )
        return None

    async def save_text_memory(
        self,
        *,
        scope: ConversationScope,
        text: str,
        source_message_id: str,
    ) -> int:
        embedding = await self.openai.embedding(text)
        title = " ".join(text.split())[:48] or "저장된 기억"
        created_at = current_timestamp()
        cursor = self.connection.execute(
            """
            INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (scope.user_id, scope.guild_id, title, text, json.dumps(embedding), source_message_id, created_at),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    async def update_text_memory(
        self,
        *,
        scope: ConversationScope,
        memory_id: int,
        text: str,
    ) -> bool:
        embedding = await self.openai.embedding(text)
        title = " ".join(text.split())[:48] or "수정된 기억"
        cursor = self.connection.execute(
            """
            UPDATE user_memories
            SET title = ?, text = ?, embedding_json = ?
            WHERE deleted_at IS NULL
              AND user_id = ?
              AND id = ?
            """,
            (title, text, json.dumps(embedding), scope.user_id, memory_id),
        )
        self.connection.commit()
        return int(cursor.rowcount) == 1

    async def save_document(
        self,
        *,
        scope: ConversationScope,
        filename: str,
        content_type: str | None,
        text: str,
        source_message_id: str,
    ) -> tuple[int, int]:
        content_hash = document_content_hash(text)
        created_at = current_timestamp()
        cursor = self.connection.execute(
            """
            INSERT INTO documents (
              user_id, guild_id, filename, content_type, content_hash, source_message_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (scope.user_id, scope.guild_id, filename, content_type, content_hash, source_message_id, created_at),
        )
        document_id = int(cursor.lastrowid)

        chunks = chunk_text(text)
        for index, chunk in enumerate(chunks):
            embedding = await self.openai.embedding(chunk)
            self.connection.execute(
                """
                INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
                VALUES (?, ?, ?, ?)
                """,
                (document_id, index, chunk, json.dumps(embedding)),
            )

        self.connection.commit()
        return document_id, len(chunks)

    def find_duplicate_document(self, *, scope: ConversationScope, text: str) -> MemoryDetail | None:
        content_hash = document_content_hash(text)
        normalized = normalize_document_text(text)
        if not normalized:
            return None
        document_rows = self.connection.execute(
            """
            SELECT id, filename, guild_id, content_hash, source_message_id, created_at
            FROM documents
            WHERE deleted_at IS NULL
              AND user_id = ?
            ORDER BY id DESC
            """,
            (scope.user_id,),
        ).fetchall()
        for row in document_rows:
            row_hash = str(row["content_hash"]) if row["content_hash"] else None
            if row_hash == content_hash:
                return self.get_document_detail(scope=scope, document_id=int(row["id"]))
            if row_hash is not None:
                continue
            if normalize_document_text(self.document_text(int(row["id"]))) == normalized:
                return self.get_document_detail(scope=scope, document_id=int(row["id"]))
        return None

    async def search(
        self,
        *,
        scope: ConversationScope,
        query: str,
        limit: int,
    ) -> list[MemorySearchResult]:
        query_embedding = await self.openai.embedding(query)
        memory_rows = self.connection.execute(
            """
            SELECT id, title, text, embedding_json, source_message_id, created_at, guild_id
            FROM user_memories
            WHERE deleted_at IS NULL
              AND user_id = ?
            """,
            (scope.user_id,),
        ).fetchall()

        document_rows = self.connection.execute(
            """
            SELECT
              documents.id AS id,
              documents.filename AS title,
              document_chunks.text AS text,
              document_chunks.embedding_json AS embedding_json,
              documents.source_message_id AS source_message_id,
              documents.created_at AS created_at,
              documents.guild_id AS guild_id
            FROM document_chunks
            JOIN documents ON documents.id = document_chunks.document_id
            WHERE documents.deleted_at IS NULL
              AND documents.user_id = ?
            """,
            (scope.user_id,),
        ).fetchall()

        results = [
            self._to_result(row, "memory", query_embedding) for row in memory_rows
        ] + [
            self._to_result(row, "document", query_embedding) for row in document_rows
        ]
        return sorted(results, key=lambda result: result.score, reverse=True)[:limit]

    def recent_items(self, *, scope: ConversationScope, limit: int = 10) -> list[MemoryListItem]:
        memory_rows = self.connection.execute(
            """
            SELECT id, title, text AS detail, guild_id, created_at
            FROM user_memories
            WHERE deleted_at IS NULL
              AND user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (scope.user_id, limit),
        ).fetchall()

        document_rows = self.connection.execute(
            """
            SELECT
              documents.id AS id,
              documents.filename AS title,
              COUNT(document_chunks.id) || ' chunks' AS detail,
              documents.guild_id AS guild_id,
              documents.created_at AS created_at
            FROM documents
            LEFT JOIN document_chunks ON document_chunks.document_id = documents.id
            WHERE documents.deleted_at IS NULL
              AND documents.user_id = ?
            GROUP BY documents.id
            ORDER BY documents.id DESC
            LIMIT ?
            """,
            (scope.user_id, limit),
        ).fetchall()

        items = [
            MemoryListItem(
                id=int(row["id"]),
                kind="memory",
                title=str(row["title"]),
                created_at=str(row["created_at"]),
                detail=str(row["detail"])[:80],
                source_location=source_location(row["guild_id"]),
            )
            for row in memory_rows
        ] + [
            MemoryListItem(
                id=int(row["id"]),
                kind="document",
                title=str(row["title"]),
                created_at=str(row["created_at"]),
                detail=str(row["detail"]),
                source_location=source_location(row["guild_id"]),
            )
            for row in document_rows
        ]
        kind_order = {"memory": 0, "document": 1}
        return sorted(items, key=lambda item: (item.created_at, kind_order[item.kind], item.id), reverse=True)[:limit]

    def deleted_items(self, *, scope: ConversationScope, limit: int = 10) -> list[MemoryListItem]:
        memory_rows = self.connection.execute(
            """
            SELECT id, title, text AS detail, guild_id, deleted_at AS created_at
            FROM user_memories
            WHERE deleted_at IS NOT NULL
              AND user_id = ?
            ORDER BY deleted_at DESC, id DESC
            LIMIT ?
            """,
            (scope.user_id, limit),
        ).fetchall()

        document_rows = self.connection.execute(
            """
            SELECT
              documents.id AS id,
              documents.filename AS title,
              COUNT(document_chunks.id) || ' chunks' AS detail,
              documents.guild_id AS guild_id,
              documents.deleted_at AS created_at
            FROM documents
            LEFT JOIN document_chunks ON document_chunks.document_id = documents.id
            WHERE documents.deleted_at IS NOT NULL
              AND documents.user_id = ?
            GROUP BY documents.id
            ORDER BY documents.deleted_at DESC, documents.id DESC
            LIMIT ?
            """,
            (scope.user_id, limit),
        ).fetchall()

        items = [
            MemoryListItem(
                id=int(row["id"]),
                kind="memory",
                title=str(row["title"]),
                created_at=str(row["created_at"]),
                detail=str(row["detail"])[:80],
                source_location=source_location(row["guild_id"]),
            )
            for row in memory_rows
        ] + [
            MemoryListItem(
                id=int(row["id"]),
                kind="document",
                title=str(row["title"]),
                created_at=str(row["created_at"]),
                detail=str(row["detail"]),
                source_location=source_location(row["guild_id"]),
            )
            for row in document_rows
        ]
        return sorted(items, key=lambda item: item.created_at, reverse=True)[:limit]

    def stats(self, *, scope: ConversationScope) -> dict[str, int]:
        memory_count = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM user_memories
            WHERE deleted_at IS NULL
              AND user_id = ?
            """,
            (scope.user_id,),
        ).fetchone()["count"]
        document_count = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM documents
            WHERE deleted_at IS NULL
              AND user_id = ?
            """,
            (scope.user_id,),
        ).fetchone()["count"]
        chunk_count = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM document_chunks
            JOIN documents ON documents.id = document_chunks.document_id
            WHERE documents.deleted_at IS NULL
              AND documents.user_id = ?
            """,
            (scope.user_id,),
        ).fetchone()["count"]
        return {
            "memories": int(memory_count),
            "documents": int(document_count),
            "chunks": int(chunk_count),
        }

    def get_memory_detail(self, *, scope: ConversationScope, memory_id: int) -> MemoryDetail | None:
        row = self.connection.execute(
            """
            SELECT id, title, text, guild_id, source_message_id, created_at
            FROM user_memories
            WHERE deleted_at IS NULL
              AND user_id = ?
              AND id = ?
            """,
            (scope.user_id, memory_id),
        ).fetchone()
        if not row:
            return None
        return MemoryDetail(
            id=int(row["id"]),
            kind="memory",
            title=str(row["title"]),
            text=str(row["text"]),
            created_at=str(row["created_at"]),
            source_message_id=str(row["source_message_id"]) if row["source_message_id"] else None,
            source_location=source_location(row["guild_id"]),
        )

    def get_document_detail(self, *, scope: ConversationScope, document_id: int) -> MemoryDetail | None:
        row = self.connection.execute(
            """
            SELECT id, filename, guild_id, source_message_id, created_at
            FROM documents
            WHERE deleted_at IS NULL
              AND user_id = ?
              AND id = ?
            """,
            (scope.user_id, document_id),
        ).fetchone()
        if not row:
            return None

        chunk_rows = self.connection.execute(
            """
            SELECT text
            FROM document_chunks
            WHERE document_id = ?
            ORDER BY chunk_index ASC
            """,
            (document_id,),
        ).fetchall()
        return MemoryDetail(
            id=int(row["id"]),
            kind="document",
            title=str(row["filename"]),
            text="\n\n".join(str(chunk["text"]) for chunk in chunk_rows),
            created_at=str(row["created_at"]),
            source_message_id=str(row["source_message_id"]) if row["source_message_id"] else None,
            chunk_count=len(chunk_rows),
            source_location=source_location(row["guild_id"]),
        )

    def document_text(self, document_id: int) -> str:
        chunk_rows = self.connection.execute(
            """
            SELECT text
            FROM document_chunks
            WHERE document_id = ?
            ORDER BY chunk_index ASC
            """,
            (document_id,),
        ).fetchall()
        return "\n\n".join(str(chunk["text"]) for chunk in chunk_rows)

    def delete_latest_item(self, *, scope: ConversationScope) -> MemoryListItem | None:
        row = self.connection.execute(
            """
            SELECT kind, id, title, detail, guild_id, created_at
            FROM (
              SELECT
                'memory' AS kind,
                id,
                title,
                text AS detail,
                guild_id,
                created_at
              FROM user_memories
              WHERE deleted_at IS NULL
                AND user_id = ?
              UNION ALL
              SELECT
                'document' AS kind,
                documents.id AS id,
                documents.filename AS title,
                COUNT(document_chunks.id) || ' chunks' AS detail,
                documents.guild_id AS guild_id,
                documents.created_at AS created_at
              FROM documents
              LEFT JOIN document_chunks ON document_chunks.document_id = documents.id
              WHERE documents.deleted_at IS NULL
                AND documents.user_id = ?
              GROUP BY documents.id
            )
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (scope.user_id, scope.user_id),
        ).fetchone()
        if row is None:
            return None

        item = MemoryListItem(
            id=int(row["id"]),
            kind=str(row["kind"]),  # type: ignore[arg-type]
            title=str(row["title"]),
            created_at=str(row["created_at"]),
            detail=str(row["detail"])[:80],
            source_location=source_location(row["guild_id"]),
        )
        if item.kind == "memory":
            self.delete_memory_ids(scope=scope, memory_ids=[item.id])
        else:
            self.delete_document_ids(scope=scope, document_ids=[item.id])
        return item

    def delete_by_query(self, *, scope: ConversationScope, query: str) -> int:
        term = f"%{query.replace('%', '').replace('_', '')}%"
        memory_cursor = self.connection.execute(
            """
            UPDATE user_memories
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE deleted_at IS NULL
              AND user_id = ?
              AND (title LIKE ? OR text LIKE ?)
            """,
            (scope.user_id, term, term),
        )
        document_cursor = self.connection.execute(
            """
            UPDATE documents
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE deleted_at IS NULL
              AND user_id = ?
              AND filename LIKE ?
            """,
            (scope.user_id, term),
        )
        self.connection.commit()
        return int(memory_cursor.rowcount) + int(document_cursor.rowcount)

    def restore_latest_deleted_item(self, *, scope: ConversationScope) -> MemoryListItem | None:
        row = self.connection.execute(
            """
            SELECT kind, id, title, detail, guild_id, created_at, deleted_at
            FROM (
              SELECT
                'memory' AS kind,
                id,
                title,
                text AS detail,
                guild_id,
                created_at,
                deleted_at
              FROM user_memories
              WHERE deleted_at IS NOT NULL
                AND user_id = ?
              UNION ALL
              SELECT
                'document' AS kind,
                documents.id AS id,
                documents.filename AS title,
                COUNT(document_chunks.id) || ' chunks' AS detail,
                documents.guild_id AS guild_id,
                documents.created_at AS created_at,
                documents.deleted_at AS deleted_at
              FROM documents
              LEFT JOIN document_chunks ON document_chunks.document_id = documents.id
              WHERE documents.deleted_at IS NOT NULL
                AND documents.user_id = ?
              GROUP BY documents.id
            )
            ORDER BY deleted_at DESC, id DESC
            LIMIT 1
            """,
            (scope.user_id, scope.user_id),
        ).fetchone()
        if row is None:
            return None

        item = MemoryListItem(
            id=int(row["id"]),
            kind=str(row["kind"]),  # type: ignore[arg-type]
            title=str(row["title"]),
            created_at=str(row["created_at"]),
            detail=str(row["detail"])[:80],
            source_location=source_location(row["guild_id"]),
        )
        table = "user_memories" if item.kind == "memory" else "documents"
        self.connection.execute(
            f"""
            UPDATE {table}
            SET deleted_at = NULL
            WHERE user_id = ?
              AND id = ?
              AND deleted_at IS NOT NULL
            """,
            (scope.user_id, item.id),
        )
        self.connection.commit()
        return item

    def restore_memory_ids(self, *, scope: ConversationScope, memory_ids: list[int]) -> int:
        if not memory_ids:
            return 0
        restored = 0
        for memory_id in memory_ids:
            cursor = self.connection.execute(
                """
                UPDATE user_memories
                SET deleted_at = NULL
                WHERE deleted_at IS NOT NULL
                  AND user_id = ?
                  AND id = ?
                """,
                (scope.user_id, memory_id),
            )
            restored += int(cursor.rowcount)
        self.connection.commit()
        return restored

    def restore_document_ids(self, *, scope: ConversationScope, document_ids: list[int]) -> int:
        if not document_ids:
            return 0
        restored = 0
        for document_id in document_ids:
            cursor = self.connection.execute(
                """
                UPDATE documents
                SET deleted_at = NULL
                WHERE deleted_at IS NOT NULL
                  AND user_id = ?
                  AND id = ?
                """,
                (scope.user_id, document_id),
            )
            restored += int(cursor.rowcount)
        self.connection.commit()
        return restored

    def delete_all_for_user(self, *, scope: ConversationScope) -> int:
        memory_cursor = self.connection.execute(
            """
            UPDATE user_memories
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE deleted_at IS NULL
              AND user_id = ?
            """,
            (scope.user_id,),
        )
        document_cursor = self.connection.execute(
            """
            UPDATE documents
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE deleted_at IS NULL
              AND user_id = ?
            """,
            (scope.user_id,),
        )
        self.connection.commit()
        return int(memory_cursor.rowcount) + int(document_cursor.rowcount)

    def delete_memory_ids(self, *, scope: ConversationScope, memory_ids: list[int]) -> int:
        if not memory_ids:
            return 0
        deleted = 0
        for memory_id in memory_ids:
            cursor = self.connection.execute(
                """
                UPDATE user_memories
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE deleted_at IS NULL
                  AND user_id = ?
                  AND id = ?
                """,
                (scope.user_id, memory_id),
            )
            deleted += int(cursor.rowcount)
        self.connection.commit()
        return deleted

    def delete_document_ids(self, *, scope: ConversationScope, document_ids: list[int]) -> int:
        if not document_ids:
            return 0
        deleted = 0
        for document_id in document_ids:
            cursor = self.connection.execute(
                """
                UPDATE documents
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE deleted_at IS NULL
                  AND user_id = ?
                  AND id = ?
                """,
                (scope.user_id, document_id),
            )
            deleted += int(cursor.rowcount)
        self.connection.commit()
        return deleted

    @staticmethod
    def _to_result(
        row: sqlite3.Row,
        kind: str,
        query_embedding: list[float],
    ) -> MemorySearchResult:
        embedding = json.loads(row["embedding_json"])
        return MemorySearchResult(
            id=int(row["id"]),
            kind=kind,  # type: ignore[arg-type]
            title=str(row["title"]),
            text=str(row["text"]),
            score=cosine_similarity(query_embedding, embedding),
            source_message_id=str(row["source_message_id"]) if row["source_message_id"] else None,
            created_at=str(row["created_at"]),
            source_location=source_location(row["guild_id"]),
        )


def source_location(guild_id: object) -> str:
    return "DM" if guild_id is None else "서버"


def current_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")


def task_item_from_row(row: sqlite3.Row) -> TaskItem:
    return TaskItem(
        id=int(row["id"]),
        user_id=str(row["user_id"]),
        conversation_id=str(row["conversation_id"]),
        channel_id=str(row["channel_id"]) if row["channel_id"] else None,
        title=str(row["title"]),
        status=str(row["status"]),
        priority=str(row["priority"]) if row["priority"] else "normal",
        due_at=str(row["due_at"]) if row["due_at"] else None,
        created_at=str(row["created_at"]),
        completed_at=str(row["completed_at"]) if row["completed_at"] else None,
        reminder_sent_at=str(row["reminder_sent_at"]) if row["reminder_sent_at"] else None,
        deleted_at=str(row["deleted_at"]) if row["deleted_at"] else None,
        source_message_id=str(row["source_message_id"]) if row["source_message_id"] else None,
        source_location=source_location(row["guild_id"]),
    )


def normalize_task_priority(priority: str | None) -> str:
    normalized = (priority or "normal").strip().casefold()
    if normalized in {"high", "높음", "높아", "중요", "긴급", "urgent", "important"}:
        return "high"
    if normalized in {"low", "낮음", "낮아", "나중", "천천히"}:
        return "low"
    return "normal"


def normalize_due_cutoff(value: str) -> str:
    cleaned = value.strip()
    if is_date_only_due(cleaned):
        return f"{cleaned} 23:59"
    return cleaned


def normalize_due_start(value: str) -> str:
    cleaned = value.strip()
    return cleaned


def is_date_only_due(value: str) -> bool:
    return len(value) == 10 and value[4] == "-" and value[7] == "-" and value.replace("-", "").isdigit()


def normalize_memory_text(text: str) -> str:
    return " ".join(text.casefold().split())


def normalize_document_text(text: str) -> str:
    return "\n".join(line.strip() for line in text.casefold().splitlines() if line.strip())


def document_content_hash(text: str) -> str:
    normalized = normalize_document_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
