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
    router_context_messages: int = 16
    agent_context_messages: int = 12
    focused_context_max_chars: int = 2000
    response_context_max_chars: int = 1200
    user_context_conversations: int = 3
    user_context_max_chars: int = 1000
    vision_ocr_model: str = "gpt-5.4-mini"
    vision_ocr_per_message_bytes: int = 10 * 1024 * 1024
    vision_ocr_daily_bytes: int = 50 * 1024 * 1024
    kma_api_auth_key: str | None = None
    kma_api_timeout_seconds: float = 8
    kma_api_cache_ttl_minutes: int = 20
    kma_location_resource_path: str = "resources/kma_locations.csv"
    web_search_provider: str = "naver"
    naver_search_client_id: str | None = None
    naver_search_client_secret: str | None = None
    web_search_max_results: int = 10
    web_search_timeout_seconds: float = 10
    web_search_daily_limit_per_user: int = 50
    web_search_required_threshold: int = 70
    web_search_confirm_threshold: int = 45
    web_search_read_top_n: int = 5
    web_page_timeout_seconds: float = 8
    web_page_max_chars: int = 6000
    web_page_max_bytes: int = 1024 * 1024
    web_cache_enabled: bool = True
    web_search_cache_ttl_minutes: int = 30
    web_page_cache_ttl_minutes: int = 360
    web_cache_fallback_on_error: bool = True


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
        openai_timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "0")),
        openai_max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
        pending_confirmation_ttl_minutes=int(os.getenv("PENDING_CONFIRMATION_TTL_MINUTES", "10")),
        task_reminder_interval_minutes=int(os.getenv("TASK_REMINDER_INTERVAL_MINUTES", "1")),
        task_reminder_batch_size=int(os.getenv("TASK_REMINDER_BATCH_SIZE", "20")),
        timezone=os.getenv("ASSISTANT_TIMEZONE", "Asia/Seoul"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE"),
        router_context_messages=int(os.getenv("ROUTER_CONTEXT_MESSAGES", "16")),
        agent_context_messages=int(os.getenv("AGENT_CONTEXT_MESSAGES", "12")),
        focused_context_max_chars=int(os.getenv("FOCUSED_CONTEXT_MAX_CHARS", "2000")),
        response_context_max_chars=int(os.getenv("RESPONSE_CONTEXT_MAX_CHARS", "1200")),
        user_context_conversations=int(os.getenv("USER_CONTEXT_CONVERSATIONS", "3")),
        user_context_max_chars=int(os.getenv("USER_CONTEXT_MAX_CHARS", "1000")),
        vision_ocr_model="gpt-5.4-mini",
        vision_ocr_per_message_bytes=int(os.getenv("VISION_OCR_PER_MESSAGE_BYTES", str(10 * 1024 * 1024))),
        vision_ocr_daily_bytes=int(os.getenv("VISION_OCR_DAILY_BYTES", str(50 * 1024 * 1024))),
        kma_api_auth_key=os.getenv("KMA_API_AUTH_KEY"),
        kma_api_timeout_seconds=float(os.getenv("KMA_API_TIMEOUT_SECONDS", "8")),
        kma_api_cache_ttl_minutes=int(os.getenv("KMA_API_CACHE_TTL_MINUTES", "20")),
        kma_location_resource_path=os.getenv("KMA_LOCATION_RESOURCE_PATH", "resources/kma_locations.csv"),
        web_search_provider=os.getenv("WEB_SEARCH_PROVIDER", "naver"),
        naver_search_client_id=os.getenv("NAVER_SEARCH_CLIENT_ID"),
        naver_search_client_secret=os.getenv("NAVER_SEARCH_CLIENT_SECRET"),
        web_search_max_results=int(os.getenv("WEB_SEARCH_MAX_RESULTS", "10")),
        web_search_timeout_seconds=float(os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "10")),
        web_search_daily_limit_per_user=int(os.getenv("WEB_SEARCH_DAILY_LIMIT_PER_USER", "50")),
        web_search_required_threshold=int(os.getenv("WEB_SEARCH_REQUIRED_THRESHOLD", "70")),
        web_search_confirm_threshold=int(os.getenv("WEB_SEARCH_CONFIRM_THRESHOLD", "45")),
        web_search_read_top_n=int(os.getenv("WEB_SEARCH_READ_TOP_N", "5")),
        web_page_timeout_seconds=float(os.getenv("WEB_PAGE_TIMEOUT_SECONDS", "8")),
        web_page_max_chars=int(os.getenv("WEB_PAGE_MAX_CHARS", "6000")),
        web_page_max_bytes=int(os.getenv("WEB_PAGE_MAX_BYTES", str(1024 * 1024))),
        web_cache_enabled=parse_bool_env(os.getenv("WEB_CACHE_ENABLED", "true")),
        web_search_cache_ttl_minutes=int(os.getenv("WEB_SEARCH_CACHE_TTL_MINUTES", "30")),
        web_page_cache_ttl_minutes=int(os.getenv("WEB_PAGE_CACHE_TTL_MINUTES", "360")),
        web_cache_fallback_on_error=parse_bool_env(os.getenv("WEB_CACHE_FALLBACK_ON_ERROR", "true")),
    )


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} 환경 변수가 필요합니다. .env.example을 참고하세요.")
    return value


def parse_bool_env(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}
