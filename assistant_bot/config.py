from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    discord_token: str
    discord_client_id: str | None
    openai_api_key: str
    router_model: str
    easy_model: str
    medium_model: str
    hard_model: str
    embedding_model: str
    database_path: str
    max_attachment_bytes: int
    context_compression_chars: int
    retrieval_limit: int
    openai_timeout_seconds: float
    openai_max_retries: int
    pending_confirmation_ttl_minutes: int
    task_reminder_interval_minutes: int
    task_reminder_batch_size: int
    timezone: str
    log_level: str
    log_file: str | None


def load_config() -> Config:
    load_dotenv()

    discord_token = require_env("DISCORD_TOKEN")
    openai_api_key = require_env("OPENAI_API_KEY")

    return Config(
        discord_token=discord_token,
        discord_client_id=os.getenv("DISCORD_CLIENT_ID"),
        openai_api_key=openai_api_key,
        router_model=os.getenv("OPENAI_ROUTER_MODEL", "gpt-5.4-mini"),
        easy_model=os.getenv("OPENAI_EASY_MODEL", "gpt-5.4-mini"),
        medium_model=os.getenv("OPENAI_MEDIUM_MODEL", "gpt-5.4"),
        hard_model=os.getenv("OPENAI_HARD_MODEL", "gpt-5.5"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        database_path=os.getenv("DATABASE_PATH", "./data/assistant.sqlite"),
        max_attachment_bytes=int(os.getenv("MAX_ATTACHMENT_BYTES", str(10 * 1024 * 1024))),
        context_compression_chars=int(os.getenv("CONTEXT_COMPRESSION_CHARS", "20000")),
        retrieval_limit=int(os.getenv("RETRIEVAL_LIMIT", "8")),
        openai_timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30")),
        openai_max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
        pending_confirmation_ttl_minutes=int(os.getenv("PENDING_CONFIRMATION_TTL_MINUTES", "10")),
        task_reminder_interval_minutes=int(os.getenv("TASK_REMINDER_INTERVAL_MINUTES", "60")),
        task_reminder_batch_size=int(os.getenv("TASK_REMINDER_BATCH_SIZE", "20")),
        timezone=os.getenv("ASSISTANT_TIMEZONE", "Asia/Seoul"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE"),
    )


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} 환경 변수가 필요합니다. .env.example을 참고하세요.")
    return value
