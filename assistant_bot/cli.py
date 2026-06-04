from __future__ import annotations

import argparse
import asyncio
import json
import os
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv
from openai import AsyncOpenAI

from assistant_bot.agent_registry import AgentContext, build_agent_registry
from assistant_bot.agents import (
    ConversationAgent,
    MemoryAgent,
    ReminderAgent,
    RouterAgent,
    TaskAgent,
    UtilityAgent,
    asks_to_delete_all_memories,
    compact_preview,
    format_conversation_context,
    format_conversation_location,
    format_task_detail,
    format_task_priority,
)
from assistant_bot.bot import is_memory_deletion_confirmation, is_negative_confirmation, is_positive_confirmation
from assistant_bot.config import Config
from assistant_bot.database import AppDatabase
from assistant_bot.file_extractor import extract_local_file_text
from assistant_bot.models import ConversationScope, RoutingResult
from assistant_bot.openai_service import OpenAIService
from assistant_bot.stores import (
    AgentLogStore,
    ConversationStore,
    MemoryStore,
    PendingAttachmentStore,
    PendingMemoryDeletionStore,
    ReminderStore,
    TaskStore,
)
from assistant_bot.time_utils import now_in_timezone, today_string

DEFAULT_DATABASE_PATH = "./data/assistant.sqlite"
REQUIRED_ENV_NAMES = ["DISCORD_TOKEN", "OPENAI_API_KEY"]
OPTIONAL_ENV_NAMES = [
    "DISCORD_CLIENT_ID",
    "OPENAI_ROUTER_MODEL",
    "OPENAI_EASY_MODEL",
    "OPENAI_MEDIUM_MODEL",
    "OPENAI_HARD_MODEL",
    "OPENAI_EMBEDDING_MODEL",
    "OPENAI_TIMEOUT_SECONDS",
    "OPENAI_MAX_RETRIES",
    "DATABASE_PATH",
    "ASSISTANT_TIMEZONE",
    "MAX_ATTACHMENT_BYTES",
    "CONTEXT_COMPRESSION_CHARS",
    "RETRIEVAL_LIMIT",
    "PENDING_CONFIRMATION_TTL_MINUTES",
    "TASK_REMINDER_INTERVAL_MINUTES",
    "TASK_REMINDER_BATCH_SIZE",
    "LOG_LEVEL",
    "LOG_FILE",
]


@dataclass(frozen=True)
class DoctorResult:
    ok: bool
    lines: list[str]


@dataclass(frozen=True)
class OpenAICheckResult:
    name: str
    ok: bool
    detail: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Discord 대화형 비서 운영 도구")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="환경 변수와 기본 설정을 점검한다")
    subparsers.add_parser("openai-check", help="OpenAI 텍스트 응답과 embedding 연결을 점검한다")
    subparsers.add_parser("invite", help="Discord 봇 초대 URL을 생성한다")
    subparsers.add_parser("init-db", help="SQLite 저장소를 생성하고 핵심 테이블을 점검한다")
    subparsers.add_parser("stats", help="SQLite 저장소 상태를 출력한다")
    users_parser = subparsers.add_parser("users", help="사용자별 저장 기억 현황을 조회한다")
    users_parser.add_argument("--limit", "-n", type=int, default=20, help="최대 사용자 수")
    memories_parser = subparsers.add_parser("memories", help="최근 저장된 기억과 문서를 목록으로 조회한다")
    memories_parser.add_argument("--limit", "-n", type=int, default=20, help="최대 결과 수")
    memories_parser.add_argument("--user-id", help="특정 Discord user_id의 기억만 조회한다")
    memories_parser.add_argument(
        "--kind",
        choices=["all", "memory", "document"],
        default="all",
        help="조회할 항목 종류",
    )
    deleted_parser = subparsers.add_parser("deleted", help="삭제된 기억과 문서를 목록으로 조회한다")
    deleted_parser.add_argument("--limit", "-n", type=int, default=20, help="최대 결과 수")
    deleted_parser.add_argument("--user-id", help="특정 Discord user_id의 삭제 항목만 조회한다")
    deleted_parser.add_argument(
        "--kind",
        choices=["all", "memory", "document"],
        default="all",
        help="조회할 항목 종류",
    )
    undelete_parser = subparsers.add_parser("undelete", help="삭제된 기억이나 문서를 ID로 복구한다")
    undelete_parser.add_argument("--user-id", required=True, help="복구 대상 Discord user_id")
    undelete_parser.add_argument("--memory-id", type=int, action="append", default=[], help="복구할 메모 ID")
    undelete_parser.add_argument("--document-id", type=int, action="append", default=[], help="복구할 문서 ID")
    export_parser = subparsers.add_parser("export", help="기억, 문서, 할 일을 JSON으로 내보낸다")
    export_parser.add_argument("--output", "-o", help="저장할 JSON 파일 경로. 생략하면 stdout에 출력한다")
    export_parser.add_argument("--user-id", help="특정 Discord user_id의 데이터만 내보낸다")
    search_parser = subparsers.add_parser("search", help="저장된 기억, 문서, 할 일을 키워드로 검색한다")
    search_parser.add_argument("keyword", help="검색할 키워드")
    search_parser.add_argument("--limit", "-n", type=int, default=10, help="최대 결과 수")
    search_parser.add_argument("--user-id", help="특정 Discord user_id의 데이터만 검색한다")
    ingest_parser = subparsers.add_parser("ingest", help="로컬 파일을 사용자 장기 기억 문서로 저장한다")
    ingest_parser.add_argument("paths", nargs="+", help="저장할 로컬 파일 경로. .txt, .md, .pdf 지원")
    ingest_parser.add_argument("--user-id", default="local-user", help="기억을 저장할 사용자 ID")
    ingest_parser.add_argument("--guild-id", help="서버 위치로 저장할 때 사용할 guild ID")
    route_parser = subparsers.add_parser("route", help="메시지가 어떤 intent로 분류될지 빠르게 확인한다")
    route_parser.add_argument("message", help="확인할 사용자 메시지")
    route_parser.add_argument("--attachments", action="store_true", help="첨부 파일이 있는 상황으로 가정한다")
    ask_parser = subparsers.add_parser("ask", help="Discord 없이 로컬에서 텍스트 대화를 실행한다")
    ask_parser.add_argument("message", help="로컬에서 실행할 사용자 메시지")
    ask_parser.add_argument("--user-id", default="local-user", help="대화에 사용할 사용자 ID")
    ask_parser.add_argument("--conversation-id", help="대화 ID. 생략하면 user-id 기준 로컬 대화 ID를 사용한다")
    ask_parser.add_argument("--channel-id", default="local-cli", help="대화에 사용할 채널 ID")
    ask_parser.add_argument("--guild-id", help="서버 위치를 흉내낼 때 사용할 guild ID")
    ask_parser.add_argument("--author-name", default="local-user", help="대화에 사용할 사용자 이름")
    briefing_parser = subparsers.add_parser("briefing", help="사용자별 오늘 브리핑을 출력한다")
    briefing_parser.add_argument("--user-id", default="local-user", help="대상 Discord user_id")
    briefing_parser.add_argument("--guild-id", help="서버 위치를 흉내낼 때 사용할 guild ID")
    snapshot_parser = subparsers.add_parser("snapshot", help="사용자별 기억, 할 일, 최근 대화 위치를 요약한다")
    snapshot_parser.add_argument("--user-id", default="local-user", help="대상 Discord user_id")
    snapshot_parser.add_argument("--limit", "-n", type=int, default=5, help="섹션별 최대 결과 수")
    conversations_parser = subparsers.add_parser("conversations", help="대화 컨텍스트 현황을 조회한다")
    conversations_parser.add_argument("--limit", "-n", type=int, default=20, help="최대 결과 수")
    clear_conversation_parser = subparsers.add_parser(
        "clear-conversation",
        help="특정 대화 컨텍스트의 메시지와 요약을 삭제한다",
    )
    clear_conversation_parser.add_argument("--conversation-id", required=True, help="초기화할 conversation_id")
    tasks_parser = subparsers.add_parser("tasks", help="사용자별 할 일을 조회하거나 관리한다")
    tasks_parser.add_argument("--user-id", default="local-user", help="대상 Discord user_id")
    tasks_parser.add_argument("--guild-id", help="서버 위치로 저장할 때 사용할 guild ID")
    tasks_parser.add_argument("--limit", "-n", type=int, default=20, help="최대 결과 수")
    tasks_parser.add_argument(
        "--status",
        choices=["open", "completed", "all"],
        default="open",
        help="조회할 할 일 상태",
    )
    tasks_action = tasks_parser.add_mutually_exclusive_group()
    tasks_action.add_argument("--add", help="추가할 할 일 제목")
    tasks_action.add_argument("--complete", type=int, action="append", default=[], help="완료 처리할 할 일 ID")
    tasks_action.add_argument("--show", type=int, action="append", default=[], help="상세 조회할 할 일 ID")
    tasks_action.add_argument(
        "--reopen",
        type=int,
        action="append",
        default=[],
        help="완료 상태를 취소하고 다시 열 할 일 ID",
    )
    tasks_action.add_argument("--restore", type=int, action="append", default=[], help="삭제한 할 일을 복구할 ID")
    tasks_action.add_argument("--postpone", type=int, action="append", default=[], help="기한을 미룰 할 일 ID")
    tasks_action.add_argument("--rename", type=int, action="append", default=[], help="제목을 바꿀 할 일 ID")
    tasks_action.add_argument("--set-priority", type=int, action="append", default=[], help="우선순위를 바꿀 할 일 ID")
    tasks_action.add_argument("--delete", type=int, action="append", default=[], help="삭제할 할 일 ID")
    tasks_parser.add_argument("--deleted", action="store_true", help="삭제한 할 일 목록을 조회한다")
    tasks_parser.add_argument("--title", help="--rename에 사용할 새 할 일 제목")
    tasks_parser.add_argument("--priority", choices=["high", "normal", "low"], help="할 일 우선순위")
    tasks_parser.add_argument("--due", help="할 일 기한. 예: 2026-06-10")
    tasks_parser.add_argument("--due-after", help="해당 날짜/시각 이후인 열린 할 일만 조회한다. 예: 2026-06-10")
    tasks_parser.add_argument("--due-before", help="해당 날짜까지인 열린 할 일만 조회한다. 예: 2026-06-10")
    tasks_parser.add_argument("--undated", action="store_true", help="기한 없는 열린 할 일만 조회한다")
    logs_parser = subparsers.add_parser("logs", help="최근 에이전트 라우팅과 모델 선택 로그를 조회한다")
    logs_parser.add_argument("--limit", "-n", type=int, default=20, help="최대 결과 수")
    logs_parser.add_argument("--agent", help="특정 에이전트 로그만 조회한다")
    logs_parser.add_argument("--conversation-id", help="특정 conversation_id 로그만 조회한다")
    reminders_parser = subparsers.add_parser("reminders", help="발송 대기 중인 사용자 알림 대상을 미리 확인한다")
    reminders_parser.add_argument("--limit", "-n", type=int, default=20, help="최대 결과 수")
    reminders_parser.add_argument("--user-id", help="특정 Discord user_id의 리마인더만 조회한다")
    reminders_parser.add_argument("--as-of", help="기준 날짜/시각. 예: 2026-06-10 또는 2026-06-10 09:30")
    cleanup_parser = subparsers.add_parser("cleanup", help="오래된 운영 로그, 대화 기록, 삭제 항목을 정리한다")
    cleanup_parser.add_argument("--days", type=int, default=30, help="보존할 최근 일수")
    cleanup_parser.add_argument(
        "--target",
        choices=["all", "conversations", "logs", "pending", "deleted"],
        default="all",
        help="정리 대상",
    )
    cleanup_parser.add_argument("--force", action="store_true", help="미리보기 없이 실제로 삭제한다")
    backup_parser = subparsers.add_parser("backup", help="SQLite 저장소 전체를 백업한다")
    backup_parser.add_argument("--output", "-o", required=True, help="저장할 SQLite 백업 파일 경로")
    backup_parser.add_argument("--overwrite", action="store_true", help="출력 파일이 이미 있어도 덮어쓴다")
    restore_parser = subparsers.add_parser("restore", help="SQLite 백업 파일로 저장소를 복구한다")
    restore_parser.add_argument("--input", "-i", required=True, help="복구에 사용할 SQLite 백업 파일 경로")
    restore_parser.add_argument("--force", action="store_true", help="확인 없이 현재 저장소를 백업 파일로 교체한다")

    args = parser.parse_args()
    load_dotenv()

    if args.command == "doctor":
        result = run_doctor(os.environ)
        print("\n".join(result.lines))
        raise SystemExit(0 if result.ok else 1)

    if args.command == "openai-check":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY가 필요합니다. .env.example을 참고해 설정해 주세요.")
            raise SystemExit(1)
        results = asyncio.run(
            run_openai_checks(
                AsyncOpenAI(api_key=api_key),
                text_model=os.getenv("OPENAI_EASY_MODEL", "gpt-5.4-mini"),
                embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            )
        )
        print(format_openai_check_results(results))
        raise SystemExit(0 if all(result.ok for result in results) else 1)

    if args.command == "invite":
        client_id = os.getenv("DISCORD_CLIENT_ID")
        if not client_id:
            print("DISCORD_CLIENT_ID가 필요합니다. .env.example을 참고해 설정해 주세요.")
            raise SystemExit(1)
        print(build_invite_url(client_id))
        raise SystemExit(0)

    if args.command == "init-db":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        result = initialize_database(database_path)
        print(format_initialize_database_result(result))
        raise SystemExit(0 if result["ok"] else 1)

    if args.command == "stats":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        stats = collect_database_stats(database_path)
        print(format_database_stats(stats, database_path))
        raise SystemExit(0)

    if args.command == "users":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        users = list_users(database_path, limit=args.limit)
        print(format_users(users))
        raise SystemExit(0)

    if args.command == "memories":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        items = list_recent_memories(
            database_path,
            limit=args.limit,
            user_id=args.user_id,
            kind=args.kind,
        )
        print(format_recent_memories(items))
        raise SystemExit(0)

    if args.command == "deleted":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        items = list_deleted_memories(
            database_path,
            limit=args.limit,
            user_id=args.user_id,
            kind=args.kind,
        )
        print(format_deleted_memories(items))
        raise SystemExit(0)

    if args.command == "undelete":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        try:
            result = undelete_items(
                database_path,
                user_id=args.user_id,
                memory_ids=args.memory_id,
                document_ids=args.document_id,
            )
        except ValueError as error:
            print(str(error))
            raise SystemExit(1) from error
        print(format_undelete_result(result))
        raise SystemExit(0 if result["restored_total"] else 1)

    if args.command == "export":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        payload = export_database(database_path, user_id=args.user_id)
        output = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as file:
                file.write(output)
                file.write("\n")
            print(f"데이터 export를 저장했습니다: {args.output}")
        else:
            print(output)
        raise SystemExit(0)

    if args.command == "search":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        results = search_database(database_path, args.keyword, limit=args.limit, user_id=args.user_id)
        print(format_search_results(results, args.keyword, user_id=args.user_id))
        raise SystemExit(0)

    if args.command == "ingest":
        try:
            config = load_cli_config(os.environ)
        except RuntimeError as error:
            print(str(error))
            raise SystemExit(1) from error
        results = asyncio.run(
            ingest_local_files(
                config=config,
                paths=args.paths,
                user_id=args.user_id,
                guild_id=args.guild_id,
            )
        )
        print(format_ingest_results(results))
        raise SystemExit(0 if all(result["ok"] for result in results) else 1)

    if args.command == "route":
        from assistant_bot.agents import heuristic_route

        route = heuristic_route(args.message, args.attachments)
        print(format_route_result(route))
        raise SystemExit(0)

    if args.command == "ask":
        try:
            config = load_cli_config(os.environ)
        except RuntimeError as error:
            print(str(error))
            raise SystemExit(1) from error
        answer = asyncio.run(
            run_local_text_interaction(
                config=config,
                text=args.message,
                user_id=args.user_id,
                conversation_id=args.conversation_id,
                channel_id=args.channel_id,
                guild_id=args.guild_id,
                author_name=args.author_name,
            )
        )
        print(answer)
        raise SystemExit(0)

    if args.command == "briefing":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        print(generate_cli_briefing(database_path, user_id=args.user_id, guild_id=args.guild_id))
        raise SystemExit(0)

    if args.command == "snapshot":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        snapshot = build_user_snapshot(database_path, user_id=args.user_id, limit=args.limit)
        print(format_user_snapshot(snapshot))
        raise SystemExit(0)

    if args.command == "conversations":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        conversations = list_conversations(database_path, limit=args.limit)
        print(format_conversations(conversations))
        raise SystemExit(0)

    if args.command == "clear-conversation":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        result = clear_conversation(database_path, conversation_id=args.conversation_id)
        print(format_clear_conversation_result(result))
        raise SystemExit(0)

    if args.command == "tasks":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        result = manage_tasks(
            database_path,
            user_id=args.user_id,
            guild_id=args.guild_id,
            add_title=args.add,
            due_at=args.due,
            complete_ids=args.complete,
            show_ids=args.show,
            reopen_ids=args.reopen,
            restore_ids=args.restore,
            postpone_ids=args.postpone,
            rename_ids=args.rename,
            new_title=args.title,
            priority_ids=args.set_priority,
            priority=args.priority,
            delete_ids=args.delete,
            deleted=args.deleted,
            status=args.status,
            due_after=args.due_after,
            due_before=args.due_before,
            undated=args.undated,
            limit=args.limit,
        )
        print(format_tasks_result(result))
        raise SystemExit(0 if result["ok"] else 1)

    if args.command == "logs":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        logs = fetch_agent_logs(
            database_path,
            limit=args.limit,
            agent=args.agent,
            conversation_id=args.conversation_id,
        )
        print(format_agent_logs(logs))
        raise SystemExit(0)

    if args.command == "reminders":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        config = make_cli_utility_config(database_path)
        reminders = list_due_reminders(
            database_path,
            limit=args.limit,
            user_id=args.user_id,
            as_of=args.as_of,
            timezone_name=config.timezone,
        )
        print(format_due_reminders(reminders))
        raise SystemExit(0)

    if args.command == "cleanup":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        result = cleanup_database(
            database_path,
            days=args.days,
            target=args.target,
            apply=args.force,
        )
        print(format_cleanup_result(result))
        raise SystemExit(0)

    if args.command == "backup":
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        backup_database(database_path, args.output, overwrite=args.overwrite)
        print(f"SQLite 백업을 저장했습니다: {args.output}")
        raise SystemExit(0)

    if args.command == "restore":
        if not args.force:
            print("복구는 현재 SQLite 저장소를 교체합니다. 실행하려면 --force를 붙여 주세요.")
            raise SystemExit(1)
        database_path = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
        safety_backup = restore_database(database_path, args.input)
        print(f"SQLite 저장소를 복구했습니다: {database_path}")
        print(f"복구 전 안전 백업: {safety_backup}")
        raise SystemExit(0)


def run_doctor(env: Mapping[str, str]) -> DoctorResult:
    lines = ["환경 설정 점검 결과:"]
    ok = True

    for name in REQUIRED_ENV_NAMES:
        value = env.get(name, "")
        if not value:
            lines.append(f"- {name}: 누락")
            ok = False
        elif is_example_secret_value(value):
            lines.append(f"- {name}: 예시값으로 보입니다")
            ok = False
        else:
            lines.append(f"- {name}: 설정됨")

    for name in OPTIONAL_ENV_NAMES:
        value = env.get(name)
        lines.append(f"- {name}: {'설정됨' if value else '기본값 사용'}")

    numeric_checks = {
        "MAX_ATTACHMENT_BYTES": 10 * 1024 * 1024,
        "CONTEXT_COMPRESSION_CHARS": 20_000,
        "RETRIEVAL_LIMIT": 8,
        "OPENAI_MAX_RETRIES": 2,
        "PENDING_CONFIRMATION_TTL_MINUTES": 10,
        "TASK_REMINDER_INTERVAL_MINUTES": 1,
        "TASK_REMINDER_BATCH_SIZE": 20,
    }
    for name, default in numeric_checks.items():
        raw_value = env.get(name, str(default))
        if not raw_value.isdigit() or int(raw_value) <= 0:
            lines.append(f"- {name}: 양의 정수여야 합니다")
            ok = False

    timeout_value = env.get("OPENAI_TIMEOUT_SECONDS", "30")
    try:
        if float(timeout_value) <= 0:
            raise ValueError
    except ValueError:
        lines.append("- OPENAI_TIMEOUT_SECONDS: 양의 숫자여야 합니다")
        ok = False

    log_level = env.get("LOG_LEVEL", "INFO").strip().upper()
    valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level in valid_log_levels:
        lines.append(f"- LOG_LEVEL 유효성: 통과 ({log_level})")
    else:
        lines.append("- LOG_LEVEL 유효성: DEBUG, INFO, WARNING, ERROR, CRITICAL 중 하나여야 합니다")
        ok = False

    timezone_name = env.get("ASSISTANT_TIMEZONE", "Asia/Seoul")
    try:
        ZoneInfo(timezone_name)
        lines.append(f"- ASSISTANT_TIMEZONE 유효성: 통과 ({timezone_name})")
    except ZoneInfoNotFoundError:
        lines.append(f"- ASSISTANT_TIMEZONE 유효성: 알 수 없는 타임존 `{timezone_name}`")
        ok = False

    database_path = Path(env.get("DATABASE_PATH", DEFAULT_DATABASE_PATH))
    database_parent = database_path.parent
    if database_path.exists() and database_path.is_dir():
        lines.append("- DATABASE_PATH: 파일 경로여야 합니다")
        ok = False
    elif database_parent.exists():
        if os.access(database_parent, os.W_OK):
            lines.append(f"- DATABASE_PATH 부모 디렉터리: 쓰기 가능 ({database_parent})")
        else:
            lines.append(f"- DATABASE_PATH 부모 디렉터리: 쓰기 권한 없음 ({database_parent})")
            ok = False
    else:
        lines.append(f"- DATABASE_PATH 부모 디렉터리: 실행 시 생성 예정 ({database_parent})")

    lines.append("- Message Content Intent: Discord Developer Portal에서 직접 활성화해야 합니다")
    lines.append("점검 상태: 통과" if ok else "점검 상태: 보완 필요")
    return DoctorResult(ok=ok, lines=lines)


def is_example_secret_value(value: str) -> bool:
    normalized = value.strip().casefold()
    if not normalized:
        return False
    return normalized.startswith("your_") or normalized in {
        "your-discord-bot-token",
        "your-openai-api-key",
        "example",
        "changeme",
        "change-me",
    }


def build_invite_url(client_id: str) -> str:
    permissions = 397284656192
    query = urlencode(
        {
            "client_id": client_id,
            "permissions": str(permissions),
            "scope": "bot",
        }
    )
    return f"https://discord.com/api/oauth2/authorize?{query}"


CORE_TABLE_NAMES = [
    "user_memories",
    "documents",
    "document_chunks",
    "conversation_messages",
    "conversation_summaries",
    "agent_logs",
    "pending_attachment_requests",
    "pending_memory_deletions",
    "tasks",
]


def initialize_database(database_path: str) -> dict[str, object]:
    database = AppDatabase(database_path)
    connection = database.connection
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name ASC
        """
    ).fetchall()
    table_names = {str(row["name"]) for row in rows}
    missing_tables = [table for table in CORE_TABLE_NAMES if table not in table_names]
    journal_mode = connection.execute("PRAGMA journal_mode").fetchone()
    foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()
    database.connection.close()
    return {
        "ok": not missing_tables,
        "database_path": database_path,
        "tables": sorted(table_names),
        "missing_tables": missing_tables,
        "journal_mode": str(journal_mode[0]) if journal_mode else "-",
        "foreign_keys": bool(foreign_keys[0]) if foreign_keys else False,
    }


def format_initialize_database_result(result: dict[str, object]) -> str:
    lines = [
        f"SQLite 저장소 초기화 결과: {result['database_path']}",
        f"- 핵심 테이블: {'통과' if result['ok'] else '누락 있음'}",
        f"- journal_mode: {result['journal_mode']}",
        f"- foreign_keys: {'ON' if result['foreign_keys'] else 'OFF'}",
    ]
    missing_tables = result["missing_tables"]
    if isinstance(missing_tables, list) and missing_tables:
        lines.append("- 누락 테이블: " + ", ".join(str(table) for table in missing_tables))
    else:
        lines.append("- 누락 테이블: 없음")
    table_count = len(result["tables"]) if isinstance(result["tables"], list) else 0
    lines.append(f"- 전체 테이블 수: {table_count}개")
    return "\n".join(lines)


async def run_openai_checks(client: object, *, text_model: str, embedding_model: str) -> list[OpenAICheckResult]:
    results: list[OpenAICheckResult] = []
    try:
        response = await client.responses.create(  # type: ignore[attr-defined]
            model=text_model,
            instructions="연결 확인용 응답이다. OK만 출력한다.",
            input="OK",
            temperature=0,
        )
        output_text = str(getattr(response, "output_text", "")).strip()
        detail = f"`{text_model}` 응답 확인" if output_text else f"`{text_model}` 응답은 왔지만 출력 텍스트가 비어 있음"
        results.append(OpenAICheckResult("텍스트 응답", bool(output_text), detail))
    except Exception as error:
        results.append(OpenAICheckResult("텍스트 응답", False, format_check_error(error)))

    try:
        response = await client.embeddings.create(  # type: ignore[attr-defined]
            model=embedding_model,
            input="연결 확인",
        )
        vector = list(response.data[0].embedding) if getattr(response, "data", None) else []
        detail = (
            f"`{embedding_model}` embedding 차원 {len(vector)}"
            if vector
            else f"`{embedding_model}` embedding 결과가 비어 있음"
        )
        results.append(OpenAICheckResult("Embedding", bool(vector), detail))
    except Exception as error:
        results.append(OpenAICheckResult("Embedding", False, format_check_error(error)))

    return results


def format_openai_check_results(results: list[OpenAICheckResult]) -> str:
    lines = ["OpenAI 연결 점검 결과:"]
    for result in results:
        status = "통과" if result.ok else "실패"
        lines.append(f"- {result.name}: {status} · {result.detail}")
    lines.append("점검 상태: 통과" if all(result.ok for result in results) else "점검 상태: 보완 필요")
    return "\n".join(lines)


def format_check_error(error: Exception) -> str:
    message = str(error).strip()
    if len(message) > 160:
        message = message[:157].rstrip() + "..."
    return f"{type(error).__name__}: {message or '상세 메시지 없음'}"


def collect_database_stats(database_path: str) -> dict[str, int]:
    database = AppDatabase(database_path)
    connection = database.connection
    return {
        "memories": count_rows(connection, "user_memories", "deleted_at IS NULL"),
        "documents": count_rows(connection, "documents", "deleted_at IS NULL"),
        "document_chunks": count_rows(connection, "document_chunks"),
        "conversation_messages": count_rows(connection, "conversation_messages"),
        "conversation_summaries": count_rows(connection, "conversation_summaries"),
        "pending_attachments": count_rows(connection, "pending_attachment_requests", "resolved_at IS NULL"),
        "pending_memory_deletions": count_rows(connection, "pending_memory_deletions", "resolved_at IS NULL"),
        "open_tasks": count_rows(connection, "tasks", "deleted_at IS NULL AND status = 'open'"),
        "completed_tasks": count_rows(connection, "tasks", "deleted_at IS NULL AND status = 'completed'"),
        "agent_logs": count_rows(connection, "agent_logs"),
    }


def count_rows(connection: sqlite3.Connection, table: str, where: str | None = None) -> int:
    query = f"SELECT COUNT(*) AS count FROM {table}"
    if where:
        query += f" WHERE {where}"
    row = connection.execute(query).fetchone()
    return int(row["count"])


def format_database_stats(stats: dict[str, int], database_path: str) -> str:
    lines = [f"SQLite 저장소 상태: {database_path}"]
    labels = {
        "memories": "텍스트 기억",
        "documents": "문서",
        "document_chunks": "문서 chunk",
        "conversation_messages": "대화 메시지",
        "conversation_summaries": "대화 요약",
        "pending_attachments": "저장 확인 대기 첨부",
        "pending_memory_deletions": "삭제 확인 대기 기억",
        "open_tasks": "열린 할 일",
        "completed_tasks": "완료한 할 일",
        "agent_logs": "에이전트 로그",
    }
    for key, label in labels.items():
        lines.append(f"- {label}: {stats[key]}개")
    return "\n".join(lines)


def export_database(database_path: str, *, user_id: str | None = None) -> dict[str, object]:
    database = AppDatabase(database_path)
    connection = database.connection
    memory_where = ["deleted_at IS NULL"]
    memory_params: list[object] = []
    document_where = ["deleted_at IS NULL"]
    document_params: list[object] = []
    task_where: list[str] = []
    task_params: list[object] = []
    if user_id:
        memory_where.append("user_id = ?")
        memory_params.append(user_id)
        document_where.append("user_id = ?")
        document_params.append(user_id)
        task_where.append("user_id = ?")
        task_params.append(user_id)

    memories = [
        {
            "id": int(row["id"]),
            "user_id": str(row["user_id"]),
            "source_location": source_location(row["guild_id"]),
            "title": str(row["title"]),
            "text": str(row["text"]),
            "source_message_id": str(row["source_message_id"]) if row["source_message_id"] else None,
            "created_at": str(row["created_at"]),
        }
        for row in connection.execute(
            f"""
            SELECT id, user_id, guild_id, title, text, source_message_id, created_at
            FROM user_memories
            WHERE {" AND ".join(memory_where)}
            ORDER BY id ASC
            """,
            memory_params,
        ).fetchall()
    ]
    documents = []
    document_rows = connection.execute(
        f"""
        SELECT id, user_id, guild_id, filename, content_type, source_message_id, created_at
        FROM documents
        WHERE {" AND ".join(document_where)}
        ORDER BY id ASC
        """,
        document_params,
    ).fetchall()
    for document in document_rows:
        chunks = [
            {
                "chunk_index": int(chunk["chunk_index"]),
                "text": str(chunk["text"]),
            }
            for chunk in connection.execute(
                """
                SELECT chunk_index, text
                FROM document_chunks
                WHERE document_id = ?
                ORDER BY chunk_index ASC
                """,
                (document["id"],),
            ).fetchall()
        ]
        documents.append(
            {
                "id": int(document["id"]),
                "user_id": str(document["user_id"]),
                "source_location": source_location(document["guild_id"]),
                "filename": str(document["filename"]),
                "content_type": str(document["content_type"]) if document["content_type"] else None,
                "source_message_id": str(document["source_message_id"]) if document["source_message_id"] else None,
                "created_at": str(document["created_at"]),
                "chunks": chunks,
            }
        )
    task_query = """
        SELECT
          id, user_id, guild_id, channel_id, title, status, priority, due_at,
          conversation_id, source_message_id, created_at, completed_at, reminder_sent_at, deleted_at
        FROM tasks
    """
    if task_where:
        task_query += f" WHERE {' AND '.join(task_where)}"
    task_query += """
        ORDER BY
          CASE WHEN deleted_at IS NULL THEN 0 ELSE 1 END,
          CASE WHEN status = 'open' THEN 0 ELSE 1 END,
          id ASC
    """
    tasks = [
        {
            "id": int(row["id"]),
            "user_id": str(row["user_id"]),
            "source_location": source_location(row["guild_id"]),
            "conversation_id": str(row["conversation_id"]),
            "channel_id": str(row["channel_id"]) if row["channel_id"] else None,
            "title": str(row["title"]),
            "status": str(row["status"]),
            "priority": str(row["priority"]) if row["priority"] else "normal",
            "due_at": str(row["due_at"]) if row["due_at"] else None,
            "source_message_id": str(row["source_message_id"]) if row["source_message_id"] else None,
            "created_at": str(row["created_at"]),
            "completed_at": str(row["completed_at"]) if row["completed_at"] else None,
            "reminder_sent_at": str(row["reminder_sent_at"]) if row["reminder_sent_at"] else None,
            "deleted_at": str(row["deleted_at"]) if row["deleted_at"] else None,
        }
        for row in connection.execute(task_query, task_params).fetchall()
    ]
    return {
        "database_path": database_path,
        "user_id": user_id,
        "memories": memories,
        "documents": documents,
        "tasks": tasks,
    }


def list_users(database_path: str, *, limit: int = 20) -> list[dict[str, object]]:
    database = AppDatabase(database_path)
    connection = database.connection
    max_items = max(1, limit)
    rows = connection.execute(
        """
        WITH user_ids AS (
          SELECT user_id FROM user_memories
          UNION
          SELECT user_id FROM documents
          UNION
          SELECT user_id FROM tasks
        )
        SELECT
          user_ids.user_id AS user_id,
          COALESCE(active_memories.count, 0) AS memory_count,
          COALESCE(active_documents.count, 0) AS document_count,
          COALESCE(active_tasks.count, 0) AS task_count,
          COALESCE(deleted_memories.count, 0)
            + COALESCE(deleted_documents.count, 0)
            + COALESCE(deleted_tasks.count, 0) AS deleted_count,
          MAX(
            COALESCE(active_memories.latest_at, ''),
            COALESCE(active_documents.latest_at, ''),
            COALESCE(active_tasks.latest_at, '')
          ) AS latest_active_at
        FROM user_ids
        LEFT JOIN (
          SELECT user_id, COUNT(*) AS count, MAX(created_at) AS latest_at
          FROM user_memories
          WHERE deleted_at IS NULL
          GROUP BY user_id
        ) AS active_memories ON active_memories.user_id = user_ids.user_id
        LEFT JOIN (
          SELECT user_id, COUNT(*) AS count, MAX(created_at) AS latest_at
          FROM documents
          WHERE deleted_at IS NULL
          GROUP BY user_id
        ) AS active_documents ON active_documents.user_id = user_ids.user_id
        LEFT JOIN (
          SELECT user_id, COUNT(*) AS count, MAX(created_at) AS latest_at
          FROM tasks
          WHERE deleted_at IS NULL
          GROUP BY user_id
        ) AS active_tasks ON active_tasks.user_id = user_ids.user_id
        LEFT JOIN (
          SELECT user_id, COUNT(*) AS count
          FROM user_memories
          WHERE deleted_at IS NOT NULL
          GROUP BY user_id
        ) AS deleted_memories ON deleted_memories.user_id = user_ids.user_id
        LEFT JOIN (
          SELECT user_id, COUNT(*) AS count
          FROM documents
          WHERE deleted_at IS NOT NULL
          GROUP BY user_id
        ) AS deleted_documents ON deleted_documents.user_id = user_ids.user_id
        LEFT JOIN (
          SELECT user_id, COUNT(*) AS count
          FROM tasks
          WHERE deleted_at IS NOT NULL
          GROUP BY user_id
        ) AS deleted_tasks ON deleted_tasks.user_id = user_ids.user_id
        ORDER BY
          (
            COALESCE(active_memories.count, 0)
            + COALESCE(active_documents.count, 0)
            + COALESCE(active_tasks.count, 0)
          ) DESC,
          latest_active_at DESC,
          user_ids.user_id ASC
        LIMIT ?
        """,
        (max_items,),
    ).fetchall()
    return [
        {
            "user_id": str(row["user_id"]),
            "memory_count": int(row["memory_count"]),
            "document_count": int(row["document_count"]),
            "task_count": int(row["task_count"]),
            "deleted_count": int(row["deleted_count"]),
            "latest_active_at": str(row["latest_active_at"]) if row["latest_active_at"] else None,
        }
        for row in rows
    ]


def format_users(users: list[dict[str, object]]) -> str:
    if not users:
        return "저장된 사용자가 없습니다."
    lines = [f"사용자별 데이터 현황 {len(users)}명:"]
    for user in users:
        latest = user["latest_active_at"] or "-"
        lines.append(
            f"- user `{user['user_id']}` · 메모 {user['memory_count']}개 · "
            f"문서 {user['document_count']}개 · 할 일 {user['task_count']}개 · "
            f"삭제됨 {user['deleted_count']}개 · 최근 저장: {latest}"
        )
    return "\n".join(lines)


def list_recent_memories(
    database_path: str,
    *,
    limit: int = 20,
    user_id: str | None = None,
    kind: str = "all",
) -> list[dict[str, object]]:
    database = AppDatabase(database_path)
    connection = database.connection
    max_items = max(1, limit)
    items: list[dict[str, object]] = []

    if kind in {"all", "memory"}:
        memory_where = ["deleted_at IS NULL"]
        memory_params: list[object] = []
        if user_id:
            memory_where.append("user_id = ?")
            memory_params.append(user_id)
        memory_params.append(max_items)
        memory_rows = connection.execute(
            f"""
            SELECT id, user_id, guild_id, title, text, created_at
            FROM user_memories
            WHERE {" AND ".join(memory_where)}
            ORDER BY id DESC
            LIMIT ?
            """,
            memory_params,
        ).fetchall()
        items.extend(
            {
                "kind": "memory",
                "id": int(row["id"]),
                "user_id": str(row["user_id"]),
                "source_location": source_location(row["guild_id"]),
                "title": str(row["title"]),
                "preview": make_preview(str(row["text"]), ""),
                "created_at": str(row["created_at"]),
            }
            for row in memory_rows
        )

    if kind in {"all", "document"}:
        document_where = ["documents.deleted_at IS NULL"]
        document_params: list[object] = []
        if user_id:
            document_where.append("documents.user_id = ?")
            document_params.append(user_id)
        document_params.append(max_items)
        document_rows = connection.execute(
            f"""
            SELECT
              documents.id AS id,
              documents.user_id AS user_id,
              documents.guild_id AS guild_id,
              documents.filename AS title,
              documents.created_at AS created_at,
              COUNT(document_chunks.id) AS chunk_count,
              SUBSTR(COALESCE(GROUP_CONCAT(document_chunks.text, ' '), ''), 1, 240) AS preview
            FROM documents
            LEFT JOIN document_chunks ON document_chunks.document_id = documents.id
            WHERE {" AND ".join(document_where)}
            GROUP BY documents.id
            ORDER BY documents.id DESC
            LIMIT ?
            """,
            document_params,
        ).fetchall()
        items.extend(
            {
                "kind": "document",
                "id": int(row["id"]),
                "user_id": str(row["user_id"]),
                "source_location": source_location(row["guild_id"]),
                "title": str(row["title"]),
                "preview": make_preview(str(row["preview"] or ""), ""),
                "created_at": str(row["created_at"]),
                "chunk_count": int(row["chunk_count"]),
            }
            for row in document_rows
        )

    return sorted(items, key=lambda item: str(item["created_at"]), reverse=True)[:max_items]


def format_recent_memories(items: list[dict[str, object]]) -> str:
    if not items:
        return "저장된 기억이 없습니다."
    lines = [f"최근 저장 기억 {len(items)}개:"]
    for item in items:
        label = "메모" if item["kind"] == "memory" else "문서"
        chunk_text = f" · {item['chunk_count']} chunks" if item["kind"] == "document" else ""
        lines.append(
            f"- {label} `{item['id']}` · {item['title']}{chunk_text} · user `{item['user_id']}` · "
            f"저장 위치: {item['source_location']} · {item['created_at']}\n"
            f"  {item['preview']}"
        )
    return "\n".join(lines)


def list_deleted_memories(
    database_path: str,
    *,
    limit: int = 20,
    user_id: str | None = None,
    kind: str = "all",
) -> list[dict[str, object]]:
    database = AppDatabase(database_path)
    connection = database.connection
    max_items = max(1, limit)
    items: list[dict[str, object]] = []

    if kind in {"all", "memory"}:
        memory_where = ["deleted_at IS NOT NULL"]
        memory_params: list[object] = []
        if user_id:
            memory_where.append("user_id = ?")
            memory_params.append(user_id)
        memory_params.append(max_items)
        memory_rows = connection.execute(
            f"""
            SELECT id, user_id, guild_id, title, text, created_at, deleted_at
            FROM user_memories
            WHERE {" AND ".join(memory_where)}
            ORDER BY deleted_at DESC, id DESC
            LIMIT ?
            """,
            memory_params,
        ).fetchall()
        items.extend(
            {
                "kind": "memory",
                "id": int(row["id"]),
                "user_id": str(row["user_id"]),
                "source_location": source_location(row["guild_id"]),
                "title": str(row["title"]),
                "preview": make_preview(str(row["text"]), ""),
                "created_at": str(row["created_at"]),
                "deleted_at": str(row["deleted_at"]),
            }
            for row in memory_rows
        )

    if kind in {"all", "document"}:
        document_where = ["documents.deleted_at IS NOT NULL"]
        document_params: list[object] = []
        if user_id:
            document_where.append("documents.user_id = ?")
            document_params.append(user_id)
        document_params.append(max_items)
        document_rows = connection.execute(
            f"""
            SELECT
              documents.id AS id,
              documents.user_id AS user_id,
              documents.guild_id AS guild_id,
              documents.filename AS title,
              documents.created_at AS created_at,
              documents.deleted_at AS deleted_at,
              COUNT(document_chunks.id) AS chunk_count,
              SUBSTR(COALESCE(GROUP_CONCAT(document_chunks.text, ' '), ''), 1, 240) AS preview
            FROM documents
            LEFT JOIN document_chunks ON document_chunks.document_id = documents.id
            WHERE {" AND ".join(document_where)}
            GROUP BY documents.id
            ORDER BY documents.deleted_at DESC, documents.id DESC
            LIMIT ?
            """,
            document_params,
        ).fetchall()
        items.extend(
            {
                "kind": "document",
                "id": int(row["id"]),
                "user_id": str(row["user_id"]),
                "source_location": source_location(row["guild_id"]),
                "title": str(row["title"]),
                "preview": make_preview(str(row["preview"] or ""), ""),
                "created_at": str(row["created_at"]),
                "deleted_at": str(row["deleted_at"]),
                "chunk_count": int(row["chunk_count"]),
            }
            for row in document_rows
        )

    return sorted(items, key=lambda item: str(item["deleted_at"]), reverse=True)[:max_items]


def format_deleted_memories(items: list[dict[str, object]]) -> str:
    if not items:
        return "삭제된 기억이 없습니다."
    lines = [f"삭제된 기억 {len(items)}개:"]
    for item in items:
        label = "메모" if item["kind"] == "memory" else "문서"
        chunk_text = f" · {item['chunk_count']} chunks" if item["kind"] == "document" else ""
        lines.append(
            f"- {label} `{item['id']}` · {item['title']}{chunk_text} · user `{item['user_id']}` · "
            f"저장 위치: {item['source_location']} · 삭제 시각: {item['deleted_at']}\n"
            f"  {item['preview']}"
        )
    lines.append("대화에서 `메모 3 복구해줘` 또는 `문서 2 복구해줘`처럼 말하면 복구할 수 있습니다.")
    return "\n".join(lines)


def undelete_items(
    database_path: str,
    *,
    user_id: str,
    memory_ids: list[int],
    document_ids: list[int],
) -> dict[str, object]:
    if not memory_ids and not document_ids:
        raise ValueError("복구할 --memory-id 또는 --document-id를 하나 이상 지정해 주세요")
    database = AppDatabase(database_path)
    memories = MemoryStore(database.connection, openai=NullOpenAIService())  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id=f"admin:{user_id}",
        channel_id="admin-cli",
        user_id=user_id,
        guild_id=None,
    )
    restored_memories = memories.restore_memory_ids(scope=scope, memory_ids=memory_ids)
    restored_documents = memories.restore_document_ids(scope=scope, document_ids=document_ids)
    return {
        "user_id": user_id,
        "requested_memory_ids": memory_ids,
        "requested_document_ids": document_ids,
        "restored_memories": restored_memories,
        "restored_documents": restored_documents,
        "restored_total": restored_memories + restored_documents,
    }


def format_undelete_result(result: dict[str, object]) -> str:
    lines = [
        f"user `{result['user_id']}` 삭제 항목 복구 결과:",
        f"- 요청 메모 ID: {format_id_list(result['requested_memory_ids'])}",
        f"- 요청 문서 ID: {format_id_list(result['requested_document_ids'])}",
        f"- 복구된 메모: {result['restored_memories']}개",
        f"- 복구된 문서: {result['restored_documents']}개",
    ]
    if not result["restored_total"]:
        lines.append("복구된 항목이 없습니다. `assistant-admin deleted --user-id ...`로 삭제 항목 ID를 확인해 주세요.")
    return "\n".join(lines)


def format_id_list(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "-"
    return ", ".join(str(item) for item in value)


def search_database(
    database_path: str,
    keyword: str,
    limit: int = 10,
    *,
    user_id: str | None = None,
) -> list[dict[str, object]]:
    database = AppDatabase(database_path)
    connection = database.connection
    like = f"%{keyword.replace('%', '').replace('_', '')}%"
    memory_where = ["deleted_at IS NULL", "(title LIKE ? OR text LIKE ?)"]
    memory_params: list[object] = [like, like]
    document_where = ["documents.deleted_at IS NULL", "(documents.filename LIKE ? OR document_chunks.text LIKE ?)"]
    document_params: list[object] = [like, like]
    task_where = ["deleted_at IS NULL", "title LIKE ?"]
    task_params: list[object] = [like]
    if user_id:
        memory_where.append("user_id = ?")
        memory_params.append(user_id)
        document_where.append("documents.user_id = ?")
        document_params.append(user_id)
        task_where.append("user_id = ?")
        task_params.append(user_id)
    max_items = max(1, limit)
    memory_params.append(max_items)
    memory_rows = connection.execute(
        f"""
        SELECT id, user_id, guild_id, title, text, created_at
        FROM user_memories
        WHERE {" AND ".join(memory_where)}
        ORDER BY id DESC
        LIMIT ?
        """,
        memory_params,
    ).fetchall()
    document_params.append(max_items)
    document_rows = connection.execute(
        f"""
        SELECT DISTINCT
          documents.id AS id,
          documents.user_id AS user_id,
          documents.guild_id AS guild_id,
          documents.filename AS title,
          document_chunks.text AS text,
          documents.created_at AS created_at
        FROM documents
        LEFT JOIN document_chunks ON document_chunks.document_id = documents.id
        WHERE {" AND ".join(document_where)}
        ORDER BY documents.id DESC
        LIMIT ?
        """,
        document_params,
    ).fetchall()
    task_params.append(max_items)
    task_rows = connection.execute(
        f"""
        SELECT id, user_id, guild_id, title, status, priority, due_at, created_at, completed_at
        FROM tasks
        WHERE {" AND ".join(task_where)}
        ORDER BY id DESC
        LIMIT ?
        """,
        task_params,
    ).fetchall()
    results = [
        {
            "kind": "memory",
            "id": int(row["id"]),
            "user_id": str(row["user_id"]),
            "source_location": source_location(row["guild_id"]),
            "title": str(row["title"]),
            "preview": make_preview(str(row["text"]), keyword),
            "created_at": str(row["created_at"]),
        }
        for row in memory_rows
    ] + [
        {
            "kind": "document",
            "id": int(row["id"]),
            "user_id": str(row["user_id"]),
            "source_location": source_location(row["guild_id"]),
            "title": str(row["title"]),
            "preview": make_preview(str(row["text"] or ""), keyword),
            "created_at": str(row["created_at"]),
        }
        for row in document_rows
    ] + [
        {
            "kind": "task",
            "id": int(row["id"]),
            "user_id": str(row["user_id"]),
            "source_location": source_location(row["guild_id"]),
            "title": str(row["title"]),
            "preview": make_task_search_preview(row, keyword),
            "created_at": str(row["created_at"]),
            "status": str(row["status"]),
            "priority": str(row["priority"]) if row["priority"] else "normal",
            "due_at": str(row["due_at"]) if row["due_at"] else None,
            "completed_at": str(row["completed_at"]) if row["completed_at"] else None,
        }
        for row in task_rows
    ]
    return sorted(results, key=lambda item: str(item["created_at"]), reverse=True)[:max_items]


def make_task_search_preview(row: sqlite3.Row, keyword: str) -> str:
    due_text = f" · 기한: {row['due_at']}" if row["due_at"] else ""
    completed_text = f" · 완료: {row['completed_at']}" if row["completed_at"] else ""
    status_text = (
        f"상태: {row['status']} · 우선순위: {format_task_priority(str(row['priority']))}{due_text}{completed_text}"
    )
    return make_preview(status_text, keyword)


def format_search_results(results: list[dict[str, object]], keyword: str, *, user_id: str | None = None) -> str:
    if not results:
        scope = f" user `{user_id}`" if user_id else ""
        return f"{scope} `{keyword}` 검색 결과가 없습니다.".strip()
    scope = f" · user `{user_id}`" if user_id else ""
    lines = [f"`{keyword}` 검색 결과 {len(results)}개{scope}:"]
    for result in results:
        labels = {"memory": "메모", "document": "문서", "task": "할 일"}
        label = labels.get(str(result["kind"]), str(result["kind"]))
        lines.append(
            f"- {label} `{result['id']}` · {result['title']} · user `{result['user_id']}` · "
            f"저장 위치: {result['source_location']}\n"
            f"  {result['preview']}"
        )
    return "\n".join(lines)


def manage_tasks(
    database_path: str,
    *,
    user_id: str,
    guild_id: str | None = None,
    add_title: str | None = None,
    due_at: str | None = None,
    complete_ids: list[int] | None = None,
    show_ids: list[int] | None = None,
    reopen_ids: list[int] | None = None,
    restore_ids: list[int] | None = None,
    postpone_ids: list[int] | None = None,
    rename_ids: list[int] | None = None,
    new_title: str | None = None,
    priority_ids: list[int] | None = None,
    priority: str | None = None,
    delete_ids: list[int] | None = None,
    deleted: bool = False,
    status: str = "open",
    due_after: str | None = None,
    due_before: str | None = None,
    undated: bool = False,
    limit: int = 20,
) -> dict[str, object]:
    database = AppDatabase(database_path)
    tasks = TaskStore(database.connection)
    scope = ConversationScope(
        conversation_id=f"admin:{user_id}",
        channel_id="admin-cli",
        user_id=user_id,
        guild_id=guild_id,
    )
    complete_ids = complete_ids or []
    show_ids = show_ids or []
    reopen_ids = reopen_ids or []
    restore_ids = restore_ids or []
    postpone_ids = postpone_ids or []
    rename_ids = rename_ids or []
    priority_ids = priority_ids or []
    delete_ids = delete_ids or []

    if add_title:
        duplicate = tasks.find_open_duplicate(scope=scope, title=add_title)
        if duplicate is not None:
            return {
                "ok": True,
                "action": "duplicate",
                "user_id": user_id,
                "task_id": duplicate.id,
                "changed_count": 0,
                "items": tasks.list_recent(
                    user_id=user_id,
                    status=status,
                    due_after=due_after,
                    due_before=due_before,
                    undated=undated,
                    limit=limit,
                ),
            }
        task_id = tasks.add(
            scope=scope,
            title=add_title,
            priority=priority or "normal",
            due_at=due_at,
            source_message_id="admin-cli",
        )
        items = tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        )
        return {
            "ok": True,
            "action": "add",
            "user_id": user_id,
            "task_id": task_id,
            "changed_count": 1,
            "items": items,
        }

    if show_ids:
        items = []
        missing_ids = []
        for task_id in show_ids:
            item = tasks.get(scope=scope, task_id=task_id, include_deleted=True)
            if item is None:
                missing_ids.append(task_id)
            else:
                items.append(item)
        return {
            "ok": bool(items),
            "action": "show",
            "user_id": user_id,
            "requested_ids": show_ids,
            "missing_ids": missing_ids,
            "items": items,
        }

    if complete_ids:
        changed = tasks.complete(scope=scope, task_ids=complete_ids)
        items = tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        )
        return {
            "ok": changed > 0,
            "action": "complete",
            "user_id": user_id,
            "requested_ids": complete_ids,
            "changed_count": changed,
            "items": items,
        }

    if reopen_ids:
        changed = tasks.reopen(scope=scope, task_ids=reopen_ids)
        items = tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        )
        return {
            "ok": changed > 0,
            "action": "reopen",
            "user_id": user_id,
            "requested_ids": reopen_ids,
            "changed_count": changed,
            "items": items,
        }

    if restore_ids:
        changed = tasks.restore(scope=scope, task_ids=restore_ids)
        items = tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        )
        return {
            "ok": changed > 0,
            "action": "restore",
            "user_id": user_id,
            "requested_ids": restore_ids,
            "changed_count": changed,
            "items": items,
        }

    if postpone_ids:
        if not due_at:
            return {
                "ok": False,
                "action": "postpone",
                "user_id": user_id,
                "requested_ids": postpone_ids,
                "changed_count": 0,
                "items": tasks.list_recent(
                    user_id=user_id,
                    status=status,
                    due_after=due_after,
                    due_before=due_before,
                    undated=undated,
                    limit=limit,
                ),
                "error": "--postpone에는 --due가 필요합니다.",
            }
        changed = tasks.postpone(scope=scope, task_ids=postpone_ids, due_at=due_at)
        items = tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        )
        return {
            "ok": changed > 0,
            "action": "postpone",
            "user_id": user_id,
            "requested_ids": postpone_ids,
            "changed_count": changed,
            "due_at": due_at,
            "items": items,
        }

    if rename_ids:
        if not new_title:
            return {
                "ok": False,
                "action": "rename",
                "user_id": user_id,
                "requested_ids": rename_ids,
                "changed_count": 0,
                "items": tasks.list_recent(
                    user_id=user_id,
                    status=status,
                    due_after=due_after,
                    due_before=due_before,
                    undated=undated,
                    limit=limit,
                ),
                "error": "--rename에는 --title이 필요합니다.",
            }
        changed = tasks.rename(scope=scope, task_ids=rename_ids, title=new_title)
        items = tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        )
        return {
            "ok": changed > 0,
            "action": "rename",
            "user_id": user_id,
            "requested_ids": rename_ids,
            "changed_count": changed,
            "title": new_title,
            "items": items,
        }

    if priority_ids:
        if not priority:
            return {
                "ok": False,
                "action": "priority",
                "user_id": user_id,
                "requested_ids": priority_ids,
                "changed_count": 0,
                "items": tasks.list_recent(
                    user_id=user_id,
                    status=status,
                    due_after=due_after,
                    due_before=due_before,
                    undated=undated,
                    limit=limit,
                ),
                "error": "--set-priority에는 --priority가 필요합니다.",
            }
        changed = tasks.set_priority(scope=scope, task_ids=priority_ids, priority=priority)
        items = tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        )
        return {
            "ok": changed > 0,
            "action": "priority",
            "user_id": user_id,
            "requested_ids": priority_ids,
            "changed_count": changed,
            "priority": priority,
            "items": items,
        }

    if delete_ids:
        changed = tasks.delete(scope=scope, task_ids=delete_ids)
        items = tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        )
        return {
            "ok": changed > 0,
            "action": "delete",
            "user_id": user_id,
            "requested_ids": delete_ids,
            "changed_count": changed,
            "items": items,
        }

    if deleted:
        return {
            "ok": True,
            "action": "deleted",
            "user_id": user_id,
            "items": tasks.list_deleted(user_id=user_id, limit=limit),
        }

    return {
        "ok": True,
        "action": "list",
        "user_id": user_id,
        "due_after": due_after,
        "due_before": due_before,
        "undated": undated,
        "items": tasks.list_recent(
            user_id=user_id,
            status=status,
            due_after=due_after,
            due_before=due_before,
            undated=undated,
            limit=limit,
        ),
    }


def format_tasks_result(result: dict[str, object]) -> str:
    action = str(result["action"])
    lines: list[str] = []
    if action == "add":
        lines.append(f"user `{result['user_id']}` 할 일 `{result['task_id']}`를 추가했습니다.")
    elif action == "duplicate":
        lines.append(
            f"user `{result['user_id']}` 같은 열린 할 일이 이미 있습니다: `{result['task_id']}`"
        )
    elif action == "show":
        lines.append(f"user `{result['user_id']}` 할 일 상세:")
        missing_ids = result.get("missing_ids", [])
        if isinstance(missing_ids, list) and missing_ids:
            lines.append(f"찾지 못한 ID: {', '.join(str(task_id) for task_id in missing_ids)}")
        items = result.get("items", [])
        if isinstance(items, list) and items:
            lines.extend(format_task_detail(item) for item in items)
            return "\n\n".join(lines)
        lines.append("표시할 할 일을 찾지 못했습니다.")
        return "\n".join(lines)
    elif action == "complete":
        lines.append(
            f"user `{result['user_id']}` 할 일 완료 결과: {result['changed_count']}개"
        )
        if not result["ok"]:
            lines.append("완료된 항목이 없습니다. ID와 user_id를 확인해 주세요.")
    elif action == "reopen":
        lines.append(
            f"user `{result['user_id']}` 할 일 다시 열기 결과: {result['changed_count']}개"
        )
        if not result["ok"]:
            lines.append("다시 열린 항목이 없습니다. ID와 user_id를 확인해 주세요.")
    elif action == "restore":
        lines.append(
            f"user `{result['user_id']}` 삭제한 할 일 복구 결과: {result['changed_count']}개"
        )
        if not result["ok"]:
            lines.append("복구된 항목이 없습니다. ID와 user_id를 확인해 주세요.")
    elif action == "postpone":
        due_text = f" · 새 기한: {result['due_at']}" if result.get("due_at") else ""
        lines.append(
            f"user `{result['user_id']}` 할 일 미루기 결과: {result['changed_count']}개{due_text}"
        )
        if result.get("error"):
            lines.append(str(result["error"]))
        elif not result["ok"]:
            lines.append("미뤄진 항목이 없습니다. ID와 user_id를 확인해 주세요.")
    elif action == "rename":
        title_text = f" · 새 제목: {result['title']}" if result.get("title") else ""
        lines.append(
            f"user `{result['user_id']}` 할 일 제목 수정 결과: {result['changed_count']}개{title_text}"
        )
        if result.get("error"):
            lines.append(str(result["error"]))
        elif not result["ok"]:
            lines.append("수정된 항목이 없습니다. ID와 user_id를 확인해 주세요.")
    elif action == "priority":
        priority_text = (
            f" · 새 우선순위: {format_task_priority(str(result['priority']))}"
            if result.get("priority")
            else ""
        )
        lines.append(
            f"user `{result['user_id']}` 할 일 우선순위 수정 결과: {result['changed_count']}개{priority_text}"
        )
        if result.get("error"):
            lines.append(str(result["error"]))
        elif not result["ok"]:
            lines.append("수정된 항목이 없습니다. ID와 user_id를 확인해 주세요.")
    elif action == "delete":
        lines.append(
            f"user `{result['user_id']}` 할 일 삭제 결과: {result['changed_count']}개"
        )
        if not result["ok"]:
            lines.append("삭제된 항목이 없습니다. ID와 user_id를 확인해 주세요.")
    elif action == "deleted":
        lines.append(f"user `{result['user_id']}` 삭제한 할 일 목록:")
    else:
        if result.get("undated"):
            filter_text = " · 기한 없음"
        elif result.get("due_after") and result.get("due_before"):
            filter_text = f" · {result['due_after']}부터 {result['due_before']}까지"
        elif result.get("due_after"):
            filter_text = f" · {result['due_after']}부터"
        elif result.get("due_before"):
            filter_text = f" · {result['due_before']}까지"
        else:
            filter_text = ""
        lines.append(f"user `{result['user_id']}` 할 일 목록{filter_text}:")

    items = result.get("items", [])
    if not isinstance(items, list) or not items:
        lines.append("- 표시할 할 일이 없습니다.")
        return "\n".join(lines)

    for item in items:
        due_text = f" · 기한: {item.due_at}" if item.due_at else ""
        completed_text = f" · 완료: {item.completed_at}" if item.completed_at else ""
        deleted_text = f" · 삭제: {item.deleted_at}" if item.deleted_at else ""
        priority_text = f" · 우선순위: {format_task_priority(item.priority)}"
        metadata_text = f"상태: {item.status}{priority_text}{due_text}{completed_text}{deleted_text}"
        lines.append(
            f"- 할 일 `{item.id}` · {item.title} · {metadata_text} · "
            f"저장 위치: {item.source_location}"
        )
    return "\n".join(lines)


def generate_cli_briefing(database_path: str, *, user_id: str, guild_id: str | None = None) -> str:
    database = AppDatabase(database_path)
    logs = AgentLogStore(database.connection)
    tasks = TaskStore(database.connection)
    memories = MemoryStore(database.connection, openai=NullOpenAIService())  # type: ignore[arg-type]
    utility = UtilityAgent(
        config=make_cli_utility_config(database_path),
        memories=memories,
        tasks=tasks,
        logs=logs,
        conversations=ConversationStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id=f"admin:{user_id}",
        channel_id="admin-cli",
        user_id=user_id,
        guild_id=guild_id,
    )
    return utility.daily_briefing(scope=scope, location_label=local_location_label(guild_id))


def build_user_snapshot(
    database_path: str,
    *,
    user_id: str,
    limit: int = 5,
    timezone_name: str | None = None,
) -> dict[str, object]:
    database = AppDatabase(database_path)
    connection = database.connection
    max_items = max(1, limit)
    scope = ConversationScope(
        conversation_id=f"snapshot:{user_id}",
        channel_id="admin-cli",
        user_id=user_id,
        guild_id=None,
    )
    memories = MemoryStore(connection, openai=NullOpenAIService())  # type: ignore[arg-type]
    tasks = TaskStore(connection)
    conversations = ConversationStore(connection)
    today = today_string(timezone_name or os.getenv("ASSISTANT_TIMEZONE", "Asia/Seoul"))
    pending_attachments = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM pending_attachment_requests
        WHERE user_id = ? AND resolved_at IS NULL
        """,
        (user_id,),
    ).fetchone()
    pending_memory_deletions = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM pending_memory_deletions
        WHERE user_id = ? AND resolved_at IS NULL
        """,
        (user_id,),
    ).fetchone()
    return {
        "database_path": database_path,
        "user_id": user_id,
        "today": today,
        "memory_stats": memories.stats(scope=scope),
        "task_stats": tasks.stats(scope=scope),
        "due_tasks": tasks.list_due(scope=scope, due_before=today, limit=max_items),
        "open_tasks": tasks.list_recent(user_id=user_id, status="open", limit=max_items),
        "recent_memories": memories.recent_items(scope=scope, limit=max_items),
        "recent_conversations": conversations.recent_conversations_for_user(user_id=user_id, limit=max_items),
        "pending_attachments": int(pending_attachments["count"]) if pending_attachments else 0,
        "pending_memory_deletions": int(pending_memory_deletions["count"]) if pending_memory_deletions else 0,
    }


def format_user_snapshot(snapshot: dict[str, object]) -> str:
    memory_stats = snapshot["memory_stats"]
    task_stats = snapshot["task_stats"]
    if not isinstance(memory_stats, dict):
        memory_stats = {}
    if not isinstance(task_stats, dict):
        task_stats = {}

    lines = [
        f"user `{snapshot['user_id']}` 스냅샷:",
        f"- 기준 날짜: {snapshot['today']}",
        (
            f"- 기억: 메모 {memory_stats.get('memories', 0)}개 · "
            f"문서 {memory_stats.get('documents', 0)}개 · chunk {memory_stats.get('chunks', 0)}개"
        ),
        f"- 할 일: 열린 {task_stats.get('open', 0)}개 · 완료 {task_stats.get('completed', 0)}개",
        (
            f"- 대기 작업: 첨부 저장 확인 {snapshot['pending_attachments']}개 · "
            f"전체 기억 삭제 확인 {snapshot['pending_memory_deletions']}개"
        ),
    ]

    due_tasks = snapshot["due_tasks"]
    if isinstance(due_tasks, list) and due_tasks:
        lines.append("오늘까지 처리할 할 일:")
        for task in due_tasks:
            due_text = "오늘까지" if task.due_at == snapshot["today"] else f"{task.due_at}까지"
            lines.append(
                f"- 할 일 `{task.id}` · {task.title} · 우선순위: {format_task_priority(task.priority)} · {due_text}"
            )

    open_tasks = snapshot["open_tasks"]
    if isinstance(open_tasks, list) and open_tasks:
        lines.append("최근 열린 할 일:")
        for task in open_tasks:
            due_text = f" · 기한: {task.due_at}" if task.due_at else ""
            lines.append(
                f"- 할 일 `{task.id}` · {task.title} · 우선순위: {format_task_priority(task.priority)}"
                f"{due_text} · 저장 위치: {task.source_location}"
            )

    recent_memories = snapshot["recent_memories"]
    if isinstance(recent_memories, list) and recent_memories:
        lines.append("최근 기억:")
        for item in recent_memories:
            label = "메모" if item.kind == "memory" else "문서"
            lines.append(f"- {label} `{item.id}` · {item.title} · 저장 위치: {item.source_location}")

    recent_conversations = snapshot["recent_conversations"]
    if isinstance(recent_conversations, list) and recent_conversations:
        lines.append("최근 대화 위치:")
        for conversation in recent_conversations:
            preview = compact_preview(str(conversation["latest_content"]), limit=90)
            lines.append(
                f"- {format_conversation_location(str(conversation['conversation_id']))} · "
                f"사용자 메시지 {conversation['user_message_count']}개 · "
                f"요약 {conversation['summary_count']}개 · 최근: {conversation['latest_user_message_at']}\n"
                f"  {preview}"
            )

    if len(lines) == 5:
        lines.append("아직 저장된 기억, 할 일, 대화 기록이 없습니다.")
    return "\n".join(lines)


def list_conversations(database_path: str, *, limit: int = 20) -> list[dict[str, object]]:
    database = AppDatabase(database_path)
    connection = database.connection
    max_items = max(1, limit)
    rows = connection.execute(
        """
        WITH ids AS (
          SELECT conversation_id FROM conversation_messages
          UNION
          SELECT conversation_id FROM conversation_summaries
        ),
        latest_messages AS (
          SELECT
            conversation_id,
            COUNT(*) AS message_count,
            MAX(created_at) AS latest_message_at
          FROM conversation_messages
          GROUP BY conversation_id
        ),
        latest_message_rows AS (
          SELECT conversation_id, role, user_id, content, created_at
          FROM conversation_messages
          WHERE id IN (
            SELECT MAX(id)
            FROM conversation_messages
            GROUP BY conversation_id
          )
        ),
        summary_counts AS (
          SELECT
            conversation_id,
            COUNT(*) AS summary_count,
            MAX(created_at) AS latest_summary_at
          FROM conversation_summaries
          GROUP BY conversation_id
        )
        SELECT
          ids.conversation_id AS conversation_id,
          COALESCE(latest_messages.message_count, 0) AS message_count,
          COALESCE(summary_counts.summary_count, 0) AS summary_count,
          latest_messages.latest_message_at AS latest_message_at,
          summary_counts.latest_summary_at AS latest_summary_at,
          latest_message_rows.role AS latest_role,
          latest_message_rows.user_id AS latest_user_id,
          latest_message_rows.content AS latest_content
        FROM ids
        LEFT JOIN latest_messages ON latest_messages.conversation_id = ids.conversation_id
        LEFT JOIN latest_message_rows ON latest_message_rows.conversation_id = ids.conversation_id
        LEFT JOIN summary_counts ON summary_counts.conversation_id = ids.conversation_id
        ORDER BY COALESCE(latest_messages.latest_message_at, summary_counts.latest_summary_at) DESC,
                 ids.conversation_id ASC
        LIMIT ?
        """,
        (max_items,),
    ).fetchall()
    return [
        {
            "conversation_id": str(row["conversation_id"]),
            "message_count": int(row["message_count"]),
            "summary_count": int(row["summary_count"]),
            "latest_message_at": str(row["latest_message_at"]) if row["latest_message_at"] else None,
            "latest_summary_at": str(row["latest_summary_at"]) if row["latest_summary_at"] else None,
            "latest_role": str(row["latest_role"]) if row["latest_role"] else None,
            "latest_user_id": str(row["latest_user_id"]) if row["latest_user_id"] else None,
            "latest_preview": make_preview(str(row["latest_content"] or ""), ""),
        }
        for row in rows
    ]


def format_conversations(conversations: list[dict[str, object]]) -> str:
    if not conversations:
        return "저장된 대화 컨텍스트가 없습니다."
    lines = [f"대화 컨텍스트 {len(conversations)}개:"]
    for conversation in conversations:
        latest_message = conversation["latest_message_at"] or "-"
        latest_summary = conversation["latest_summary_at"] or "-"
        role = conversation["latest_role"] or "-"
        user_id = conversation["latest_user_id"] or "-"
        lines.append(
            f"- `{conversation['conversation_id']}` · 메시지 {conversation['message_count']}개 · "
            f"요약 {conversation['summary_count']}개\n"
            f"  최근 메시지: {latest_message} · role `{role}` · user `{user_id}`\n"
            f"  최근 요약: {latest_summary}\n"
            f"  미리보기: {conversation['latest_preview']}"
        )
    lines.append(
        "대화 맥락을 지우려면 해당 대화에서 `대화 맥락 초기화해줘`라고 말하거나 "
        "`assistant-admin clear-conversation --conversation-id <id>`를 실행하세요."
    )
    return "\n".join(lines)


def clear_conversation(database_path: str, *, conversation_id: str) -> dict[str, object]:
    database = AppDatabase(database_path)
    conversations = ConversationStore(database.connection)
    counts = conversations.clear_conversation(conversation_id)
    return {
        "database_path": database_path,
        "conversation_id": conversation_id,
        "messages": counts["messages"],
        "summaries": counts["summaries"],
    }


def format_clear_conversation_result(result: dict[str, object]) -> str:
    lines = [
        f"대화 컨텍스트 초기화: `{result['conversation_id']}`",
        f"- 삭제된 메시지: {result['messages']}개",
        f"- 삭제된 요약: {result['summaries']}개",
        "- 장기 기억과 문서는 삭제하지 않았습니다.",
    ]
    if result["messages"] == 0 and result["summaries"] == 0:
        lines.append("초기화할 대화 컨텍스트가 없었습니다.")
    return "\n".join(lines)


def fetch_agent_logs(
    database_path: str,
    *,
    limit: int = 20,
    agent: str | None = None,
    conversation_id: str | None = None,
) -> list[dict[str, object]]:
    database = AppDatabase(database_path)
    connection = database.connection
    where_clauses: list[str] = []
    params: list[object] = []
    if agent:
        where_clauses.append("agent = ?")
        params.append(agent)
    if conversation_id:
        where_clauses.append("conversation_id = ?")
        params.append(conversation_id)

    query = """
        SELECT id, conversation_id, agent, intent, difficulty, model, reason, created_at
        FROM agent_logs
    """
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(max(1, limit))

    rows = connection.execute(query, params).fetchall()
    return [
        {
            "id": int(row["id"]),
            "conversation_id": str(row["conversation_id"]),
            "agent": str(row["agent"]),
            "intent": str(row["intent"]) if row["intent"] else None,
            "difficulty": str(row["difficulty"]) if row["difficulty"] else None,
            "model": str(row["model"]) if row["model"] else None,
            "reason": str(row["reason"]) if row["reason"] else None,
            "created_at": str(row["created_at"]),
        }
        for row in rows
    ]


def format_agent_logs(logs: list[dict[str, object]]) -> str:
    if not logs:
        return "에이전트 로그가 없습니다."
    lines = [f"최근 에이전트 로그 {len(logs)}개:"]
    for log in logs:
        intent = log["intent"] or "-"
        difficulty = log["difficulty"] or "-"
        model = log["model"] or "-"
        reason = log["reason"] or "-"
        lines.append(
            f"- #{log['id']} · {log['created_at']} · {log['agent']} · intent `{intent}` · "
            f"difficulty `{difficulty}` · model `{model}`\n"
            f"  conversation: {log['conversation_id']}\n"
            f"  reason: {reason}"
        )
    return "\n".join(lines)


def list_due_reminders(
    database_path: str,
    *,
    limit: int = 20,
    user_id: str | None = None,
    as_of: str | None = None,
    timezone_name: str | None = None,
) -> dict[str, object]:
    database = AppDatabase(database_path)
    reminders = ReminderStore(database.connection)
    cutoff = normalize_reminder_as_of(as_of, timezone_name=timezone_name)
    items = reminders.due_for_delivery(as_of=cutoff, limit=limit, user_id=user_id)
    return {
        "database_path": database_path,
        "user_id": user_id,
        "as_of": cutoff,
        "items": items,
    }


def normalize_reminder_as_of(as_of: str | None, *, timezone_name: str | None = None) -> str:
    if as_of and as_of.strip():
        return as_of.strip()
    return now_in_timezone(timezone_name).strftime("%Y-%m-%d %H:%M")


def format_due_reminders(result: dict[str, object]) -> str:
    items = result["items"]
    if not isinstance(items, list) or not items:
        scope = f" user `{result['user_id']}`" if result.get("user_id") else ""
        return f"{result['as_of']} 기준{scope} 리마인더 발송 대상이 없습니다."
    scope = f" · user `{result['user_id']}`" if result.get("user_id") else ""
    lines = [f"{result['as_of']} 기준 리마인더 발송 대상 {len(items)}개{scope}:"]
    for item in items:
        channel_text = item.channel_id or "-"
        lines.append(
            f"- 알림 `{item.id}` · {item.text} · user `{item.user_id}` · "
            f"예약 시각: {item.remind_at} · 채널: {channel_text} · 저장 위치: {item.source_location}"
        )
    lines.append("실제 발송은 봇의 자동 리마인더 루프에서 수행됩니다.")
    return "\n".join(lines)


def cleanup_database(
    database_path: str,
    *,
    days: int = 30,
    target: str = "all",
    apply: bool = False,
) -> dict[str, object]:
    if days <= 0:
        raise ValueError("--days는 양의 정수여야 합니다")
    database = AppDatabase(database_path)
    connection = database.connection
    cutoff = datetime.now(UTC) - timedelta(days=days)
    cutoff_text = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    tables = cleanup_tables_for(target)
    counts: dict[str, int] = {}
    for table_key, where in tables.items():
        table = cleanup_actual_table_name(table_key)
        row = connection.execute(
            f"SELECT COUNT(*) AS count FROM {table} WHERE {where}",
            (cutoff_text,),
        ).fetchone()
        counts[table_key] = int(row["count"])
    if apply:
        for table_key, where in tables.items():
            table = cleanup_actual_table_name(table_key)
            connection.execute(f"DELETE FROM {table} WHERE {where}", (cutoff_text,))
        connection.commit()
    return {
        "database_path": database_path,
        "days": days,
        "target": target,
        "cutoff": cutoff_text,
        "applied": apply,
        "counts": counts,
    }


def cleanup_tables_for(target: str) -> dict[str, str]:
    table_map = {
        "conversation_messages": "created_at < ?",
        "conversation_summaries": "created_at < ?",
        "agent_logs": "created_at < ?",
        "pending_attachment_requests": "resolved_at IS NOT NULL AND created_at < ?",
        "deleted_document_chunks": (
            "document_id IN (SELECT id FROM documents WHERE deleted_at IS NOT NULL AND deleted_at < ?)"
        ),
        "deleted_user_memories": "deleted_at IS NOT NULL AND deleted_at < ?",
        "deleted_documents": "deleted_at IS NOT NULL AND deleted_at < ?",
        "deleted_tasks": "deleted_at IS NOT NULL AND deleted_at < ?",
    }
    if target == "all":
        return table_map
    if target == "conversations":
        return {
            "conversation_messages": table_map["conversation_messages"],
            "conversation_summaries": table_map["conversation_summaries"],
        }
    if target == "logs":
        return {"agent_logs": table_map["agent_logs"]}
    if target == "pending":
        return {"pending_attachment_requests": table_map["pending_attachment_requests"]}
    if target == "deleted":
        return {
            "deleted_document_chunks": table_map["deleted_document_chunks"],
            "deleted_user_memories": table_map["deleted_user_memories"],
            "deleted_documents": table_map["deleted_documents"],
            "deleted_tasks": table_map["deleted_tasks"],
        }
    raise ValueError(f"알 수 없는 정리 대상입니다: {target}")


def cleanup_actual_table_name(table_key: str) -> str:
    table_names = {
        "deleted_document_chunks": "document_chunks",
        "deleted_user_memories": "user_memories",
        "deleted_documents": "documents",
        "deleted_tasks": "tasks",
    }
    return table_names.get(table_key, table_key)


def format_cleanup_result(result: dict[str, object]) -> str:
    counts = result["counts"]
    if not isinstance(counts, dict):
        counts = {}
    mode = "삭제 완료" if result["applied"] else "미리보기"
    lines = [
        f"SQLite 정리 {mode}: {result['database_path']}",
        f"- 보존 기간: 최근 {result['days']}일",
        f"- 기준 시각: {result['cutoff']}",
        f"- 대상: {result['target']}",
    ]
    labels = {
        "conversation_messages": "대화 메시지",
        "conversation_summaries": "대화 요약",
        "agent_logs": "에이전트 로그",
        "pending_attachment_requests": "해결된 첨부 대기 요청",
        "deleted_document_chunks": "삭제된 문서 chunk",
        "deleted_user_memories": "삭제된 메모",
        "deleted_documents": "삭제된 문서",
        "deleted_tasks": "삭제된 할 일",
    }
    for table, count in counts.items():
        lines.append(f"- {labels.get(str(table), str(table))}: {count}개")
    if not result["applied"]:
        lines.append("실제로 삭제하려면 같은 명령에 `--force`를 붙여 주세요.")
    return "\n".join(lines)


def make_preview(text: str, keyword: str, radius: int = 48) -> str:
    compact = " ".join(text.split())
    if not compact:
        return "(미리보기 없음)"
    index = compact.lower().find(keyword.lower())
    if index < 0:
        return compact[: radius * 2].rstrip()
    start = max(0, index - radius)
    end = min(len(compact), index + len(keyword) + radius)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(compact) else ""
    return f"{prefix}{compact[start:end].strip()}{suffix}"


def backup_database(database_path: str, output_path: str, *, overwrite: bool = False) -> None:
    source_path = Path(database_path)
    destination_path = Path(output_path)
    if destination_path.exists() and not overwrite:
        raise FileExistsError(f"이미 존재하는 백업 파일입니다: {output_path}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    AppDatabase(database_path).connection.close()
    source = sqlite3.connect(source_path)
    try:
        destination = sqlite3.connect(destination_path)
        try:
            source.backup(destination)
        finally:
            destination.close()
    finally:
        source.close()


def restore_database(database_path: str, input_path: str) -> str:
    source_path = Path(input_path)
    destination_path = Path(database_path)
    if not source_path.exists():
        raise FileNotFoundError(f"복구할 백업 파일을 찾지 못했습니다: {input_path}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    safety_backup_path = make_restore_safety_backup_path(destination_path)
    if destination_path.exists():
        backup_database(str(destination_path), str(safety_backup_path), overwrite=False)

    restored_source = sqlite3.connect(source_path)
    try:
        restored_destination = sqlite3.connect(destination_path)
        try:
            restored_source.backup(restored_destination)
        finally:
            restored_destination.close()
    finally:
        restored_source.close()
    return str(safety_backup_path)


def make_restore_safety_backup_path(database_path: Path) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return database_path.with_name(f"{database_path.stem}.pre-restore-{timestamp}{database_path.suffix}")


def load_cli_config(env: Mapping[str, str]) -> Config:
    openai_api_key = env.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY가 필요합니다. .env.example을 참고해 설정해 주세요.")
    return Config(
        discord_token=env.get("DISCORD_TOKEN", "local-cli"),
        discord_client_id=env.get("DISCORD_CLIENT_ID"),
        openai_api_key=openai_api_key,
        router_model=env.get("OPENAI_ROUTER_MODEL", "gpt-5.4-mini"),
        easy_model=env.get("OPENAI_EASY_MODEL", "gpt-5.4-mini"),
        medium_model=env.get("OPENAI_MEDIUM_MODEL", "gpt-5.4"),
        hard_model=env.get("OPENAI_HARD_MODEL", "gpt-5.5"),
        embedding_model=env.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        database_path=env.get("DATABASE_PATH", DEFAULT_DATABASE_PATH),
        max_attachment_bytes=int(env.get("MAX_ATTACHMENT_BYTES", str(10 * 1024 * 1024))),
        context_compression_chars=int(env.get("CONTEXT_COMPRESSION_CHARS", "20000")),
        retrieval_limit=int(env.get("RETRIEVAL_LIMIT", "8")),
        openai_timeout_seconds=float(env.get("OPENAI_TIMEOUT_SECONDS", "30")),
        openai_max_retries=int(env.get("OPENAI_MAX_RETRIES", "2")),
        pending_confirmation_ttl_minutes=int(env.get("PENDING_CONFIRMATION_TTL_MINUTES", "10")),
        task_reminder_interval_minutes=int(env.get("TASK_REMINDER_INTERVAL_MINUTES", "1")),
        task_reminder_batch_size=int(env.get("TASK_REMINDER_BATCH_SIZE", "20")),
        timezone=env.get("ASSISTANT_TIMEZONE", "Asia/Seoul"),
        log_level=env.get("LOG_LEVEL", "INFO"),
        log_file=env.get("LOG_FILE"),
    )


async def run_local_text_interaction(
    *,
    config: Config,
    text: str,
    user_id: str,
    conversation_id: str | None = None,
    channel_id: str = "local-cli",
    guild_id: str | None = None,
    author_name: str = "local-user",
) -> str:
    database = AppDatabase(config.database_path)
    openai = OpenAIService(config)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    pending_attachments = PendingAttachmentStore(database.connection)
    pending_memory_deletions = PendingMemoryDeletionStore(database.connection)
    tasks = TaskStore(database.connection)
    reminders = ReminderStore(database.connection)
    memories = MemoryStore(database.connection, openai)
    memory_agent = MemoryAgent(
        config=config,
        openai=openai,
        memories=memories,
        logs=logs,
        conversations=conversations,
    )
    utility_agent = UtilityAgent(
        config=config,
        memories=memories,
        tasks=tasks,
        logs=logs,
        conversations=conversations,
    )
    task_agent = TaskAgent(config=config, tasks=tasks, conversations=conversations, logs=logs)
    reminder_agent = ReminderAgent(config=config, reminders=reminders, logs=logs)
    conversation_agent = ConversationAgent(
        config=config,
        openai=openai,
        conversations=conversations,
        memories=memories,
        tasks=tasks,
        logs=logs,
    )
    agent_registry = build_agent_registry(
        memory_agent=memory_agent,
        utility_agent=utility_agent,
        task_agent=task_agent,
        reminder_agent=reminder_agent,
        conversation_agent=conversation_agent,
        pending_attachments=pending_attachments,
        pending_memory_deletions=pending_memory_deletions,
        pending_confirmation_ttl_minutes=config.pending_confirmation_ttl_minutes,
    )
    router = RouterAgent(
        config,
        openai,
        logs,
        routing_prompt_block=agent_registry.routing_prompt_block(),
        allowed_intents=set(agent_registry.intents()),
    )
    scope = ConversationScope(
        conversation_id=conversation_id or f"local:{user_id}",
        channel_id=channel_id,
        user_id=user_id,
        guild_id=guild_id,
    )

    answer = handle_local_pending_memory_deletion(
        text=text,
        scope=scope,
        config=config,
        memories=memories,
        logs=logs,
        pending_memory_deletions=pending_memory_deletions,
    )
    if answer is None:
        route = await router.route(
            text=text,
            has_attachments=False,
            scope=scope,
            conversation_context=format_conversation_context(
                conversations.recent_messages(scope.conversation_id, limit=16)
            ),
        )
        if route.intent == "delete_memory":
            if asks_to_delete_all_memories(text):
                answer = request_local_memory_deletion_confirmation(
                    scope=scope,
                    config=config,
                    memories=memories,
                    pending_memory_deletions=pending_memory_deletions,
                )
            else:
                answer = await agent_registry.dispatch(
                    route.intent,
                    AgentContext(
                        text=text,
                        scope=scope,
                        message_id=make_local_message_id(),
                        author_name=author_name,
                        location_label=local_location_label(guild_id),
                    ),
                )
        else:
            answer = await agent_registry.dispatch(
                route.intent,
                AgentContext(
                    text=text,
                    scope=scope,
                    message_id=make_local_message_id(),
                    author_name=author_name,
                    location_label=local_location_label(guild_id),
                ),
            )

    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="user",
        user_id=user_id,
        content=text,
    )
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="assistant",
        user_id="assistant-cli",
        content=answer,
    )
    return answer


async def ingest_local_files(
    *,
    config: Config,
    paths: list[str],
    user_id: str,
    guild_id: str | None = None,
    openai: object | None = None,
) -> list[dict[str, object]]:
    database = AppDatabase(config.database_path)
    openai_service = openai or OpenAIService(config)
    logs = AgentLogStore(database.connection)
    memories = MemoryStore(database.connection, openai_service)  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id=f"local:{user_id}",
        channel_id="local-file",
        user_id=user_id,
        guild_id=guild_id,
    )
    results: list[dict[str, object]] = []

    for raw_path in paths:
        try:
            extracted = extract_local_file_text(raw_path, max_bytes=config.max_attachment_bytes)
            duplicate = memories.find_duplicate_document(scope=scope, text=extracted.text)
            if duplicate is not None:
                logs.add(
                    conversation_id=scope.conversation_id,
                    agent="memory",
                    intent="remember",
                    difficulty="easy",
                    model=config.easy_model,
                    reason="로컬 파일 동일 문서 중복 저장 방지",
                )
                results.append(
                    {
                        "ok": True,
                        "path": raw_path,
                        "status": "duplicate",
                        "filename": extracted.filename,
                        "document_id": duplicate.id,
                        "chunk_count": duplicate.chunk_count,
                        "detail": f"이미 같은 내용을 기억하고 있습니다. 기존 문서 ID `{duplicate.id}`",
                    }
                )
                continue

            document_id, chunk_count = await memories.save_document(
                scope=scope,
                filename=extracted.filename,
                content_type=extracted.content_type,
                text=extracted.text,
                source_message_id=f"local-file:{Path(raw_path).resolve()}",
            )
            logs.add(
                conversation_id=scope.conversation_id,
                agent="memory",
                intent="remember",
                difficulty="easy",
                model=config.easy_model,
                reason="로컬 파일 문서 기억 저장",
            )
            results.append(
                {
                    "ok": True,
                    "path": raw_path,
                    "status": "saved",
                    "filename": extracted.filename,
                    "document_id": document_id,
                    "chunk_count": chunk_count,
                    "detail": f"문서 ID `{document_id}`, chunk {chunk_count}개",
                }
            )
        except Exception as error:
            results.append(
                {
                    "ok": False,
                    "path": raw_path,
                    "status": "failed",
                    "detail": format_check_error(error),
                }
            )

    return results


def format_ingest_results(results: list[dict[str, object]]) -> str:
    if not results:
        return "저장할 로컬 파일이 없습니다."
    lines = [f"로컬 파일 기억 처리 결과 {len(results)}개:"]
    for result in results:
        if result["status"] == "saved":
            lines.append(
                f"- 저장: `{result['filename']}` · {result['detail']} · 원본: {result['path']}"
            )
        elif result["status"] == "duplicate":
            lines.append(
                f"- 중복: `{result['filename']}` · {result['detail']} · 원본: {result['path']}"
            )
        else:
            lines.append(f"- 실패: {result['path']} · {result['detail']}")
    return "\n".join(lines)


def handle_local_pending_memory_deletion(
    *,
    text: str,
    scope: ConversationScope,
    config: Config,
    memories: MemoryStore,
    logs: AgentLogStore,
    pending_memory_deletions: PendingMemoryDeletionStore,
) -> str | None:
    expired_count = pending_memory_deletions.resolve_expired(
        scope=scope,
        ttl_minutes=config.pending_confirmation_ttl_minutes,
    )
    pending = pending_memory_deletions.latest(scope=scope)
    if pending is None:
        if expired_count and (is_positive_confirmation(text) or is_negative_confirmation(text)):
            return "전체 기억 삭제 확인 시간이 만료됐어요. 삭제하려면 다시 `내 기억 전부 삭제해줘`라고 말해 주세요."
        return None
    if is_negative_confirmation(text):
        pending_memory_deletions.resolve(pending.id)
        return "전체 기억 삭제를 취소했어요."
    if not is_memory_deletion_confirmation(text):
        return None

    pending_memory_deletions.resolve(pending.id)
    deleted_count = memories.delete_all_for_user(scope=scope)
    logs.add(
        conversation_id=scope.conversation_id,
        agent="memory",
        intent="delete_memory",
        difficulty="easy",
        model=config.easy_model,
        reason="로컬 CLI에서 사용자 전체 장기 기억 삭제 확인 후 실행",
    )
    if deleted_count == 0:
        return "삭제할 저장 기억이 없어요."
    return f"확인했어요. 사용자 기준 저장 기억 {deleted_count}개를 모두 삭제 처리했어요."


def request_local_memory_deletion_confirmation(
    *,
    scope: ConversationScope,
    config: Config,
    memories: MemoryStore,
    pending_memory_deletions: PendingMemoryDeletionStore,
) -> str:
    stats = memories.stats(scope=scope)
    total = stats["memories"] + stats["documents"]
    if total == 0:
        return "삭제할 저장 기억이 없어요."
    pending_memory_deletions.add(
        scope=scope,
        message_id=make_local_message_id(),
        memory_count=stats["memories"],
        document_count=stats["documents"],
    )
    return (
        f"정말 사용자 기준 저장 기억 전체를 삭제할까요? "
        f"현재 텍스트 기억 {stats['memories']}개, 문서 {stats['documents']}개가 대상입니다. "
        f"{config.pending_confirmation_ttl_minutes}분 안에 `응, 전부 삭제해`라고 다시 실행해 주세요. "
        "취소하려면 `취소해`라고 실행하면 됩니다."
    )


def make_local_message_id() -> str:
    return f"local-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"


def local_location_label(guild_id: str | None) -> str:
    return "로컬 CLI 서버 대화" if guild_id else "로컬 CLI DM"


def make_cli_utility_config(database_path: str) -> Config:
    return Config(
        discord_token="admin-cli",
        discord_client_id=None,
        openai_api_key="admin-cli",
        router_model=os.getenv("OPENAI_ROUTER_MODEL", "gpt-5.4-mini"),
        easy_model=os.getenv("OPENAI_EASY_MODEL", "gpt-5.4-mini"),
        medium_model=os.getenv("OPENAI_MEDIUM_MODEL", "gpt-5.4"),
        hard_model=os.getenv("OPENAI_HARD_MODEL", "gpt-5.5"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        database_path=database_path,
        max_attachment_bytes=int(os.getenv("MAX_ATTACHMENT_BYTES", str(10 * 1024 * 1024))),
        context_compression_chars=int(os.getenv("CONTEXT_COMPRESSION_CHARS", "20000")),
        retrieval_limit=int(os.getenv("RETRIEVAL_LIMIT", "8")),
        openai_timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30")),
        openai_max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
        pending_confirmation_ttl_minutes=int(os.getenv("PENDING_CONFIRMATION_TTL_MINUTES", "10")),
        task_reminder_interval_minutes=int(os.getenv("TASK_REMINDER_INTERVAL_MINUTES", "1")),
        task_reminder_batch_size=int(os.getenv("TASK_REMINDER_BATCH_SIZE", "20")),
        timezone=os.getenv("ASSISTANT_TIMEZONE", "Asia/Seoul"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE"),
    )


def format_route_result(route: RoutingResult) -> str:
    return "\n".join(
        [
            "라우팅 미리보기:",
            f"- intent: `{route.intent}`",
            f"- confidence: {route.confidence:.2f}",
            f"- reason: {route.reason}",
        ]
    )


def source_location(guild_id: object) -> str:
    return "DM" if guild_id is None else "서버"


class NullOpenAIService:
    async def embedding(self, text: str) -> list[float]:
        raise RuntimeError("이 명령은 embedding을 생성하지 않습니다")


if __name__ == "__main__":
    main()
