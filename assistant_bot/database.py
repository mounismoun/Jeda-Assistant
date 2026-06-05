from __future__ import annotations

import sqlite3
from pathlib import Path


class AppDatabase:
    def __init__(self, path: str) -> None:
        if path == ":memory:":
            self.connection = sqlite3.connect(path)
        else:
            db_path = Path(path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.migrate()

    def migrate(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS user_memories (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL,
              guild_id TEXT,
              title TEXT NOT NULL,
              text TEXT NOT NULL,
              embedding_json TEXT NOT NULL,
              source_message_id TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              deleted_at TEXT
            );

            CREATE TABLE IF NOT EXISTS documents (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL,
              guild_id TEXT,
              filename TEXT NOT NULL,
              content_type TEXT,
              source_message_id TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              deleted_at TEXT
            );

            CREATE TABLE IF NOT EXISTS document_chunks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
              chunk_index INTEGER NOT NULL,
              text TEXT NOT NULL,
              embedding_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS conversation_messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              conversation_id TEXT NOT NULL,
              role TEXT NOT NULL,
              user_id TEXT,
              content TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS conversation_summaries (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              conversation_id TEXT NOT NULL,
              summary TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              conversation_id TEXT NOT NULL,
              agent TEXT NOT NULL,
              intent TEXT,
              difficulty TEXT,
              model TEXT,
              reason TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS pending_attachment_requests (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              conversation_id TEXT NOT NULL,
              channel_id TEXT NOT NULL,
              message_id TEXT NOT NULL,
              user_id TEXT NOT NULL,
              guild_id TEXT,
              filenames_json TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              resolved_at TEXT
            );

            CREATE TABLE IF NOT EXISTS pending_memory_deletions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              conversation_id TEXT NOT NULL,
              channel_id TEXT NOT NULL,
              message_id TEXT NOT NULL,
              user_id TEXT NOT NULL,
              guild_id TEXT,
              memory_count INTEGER NOT NULL,
              document_count INTEGER NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              resolved_at TEXT
            );

            CREATE TABLE IF NOT EXISTS pending_memory_captures (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              conversation_id TEXT NOT NULL,
              channel_id TEXT NOT NULL,
              message_id TEXT NOT NULL,
              user_id TEXT NOT NULL,
              guild_id TEXT,
              mode TEXT NOT NULL DEFAULT 'next_message',
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              resolved_at TEXT
            );

            CREATE TABLE IF NOT EXISTS tasks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL,
              guild_id TEXT,
              conversation_id TEXT NOT NULL,
              channel_id TEXT,
              title TEXT NOT NULL,
              priority TEXT NOT NULL DEFAULT 'normal',
              due_at TEXT,
              status TEXT NOT NULL DEFAULT 'open',
              source_message_id TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              completed_at TEXT,
              reminder_sent_at TEXT,
              deleted_at TEXT
            );

            CREATE TABLE IF NOT EXISTS reminders (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL,
              guild_id TEXT,
              conversation_id TEXT NOT NULL,
              channel_id TEXT,
              text TEXT NOT NULL,
              remind_at TEXT NOT NULL,
              source_message_id TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              sent_at TEXT
            );
            """
        )
        self.add_column_if_missing("documents", "content_hash", "TEXT")
        self.add_column_if_missing("tasks", "channel_id", "TEXT")
        self.add_column_if_missing("tasks", "reminder_sent_at", "TEXT")
        self.add_column_if_missing("tasks", "priority", "TEXT NOT NULL DEFAULT 'normal'")
        self.connection.commit()

    def add_column_if_missing(self, table: str, column: str, definition: str) -> None:
        columns = {
            str(row["name"])
            for row in self.connection.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column in columns:
            return
        self.connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
