from assistant_bot.cli import (
    OpenAICheckResult,
    backup_database,
    build_invite_url,
    build_user_snapshot,
    cleanup_database,
    clear_conversation,
    collect_database_stats,
    export_database,
    fetch_agent_logs,
    format_agent_logs,
    format_cleanup_result,
    format_clear_conversation_result,
    format_conversations,
    format_database_stats,
    format_deleted_memories,
    format_due_reminders,
    format_ingest_results,
    format_initialize_database_result,
    format_openai_check_results,
    format_recent_memories,
    format_route_result,
    format_search_results,
    format_tasks_result,
    format_undelete_result,
    format_user_snapshot,
    format_users,
    generate_cli_briefing,
    ingest_local_files,
    initialize_database,
    list_conversations,
    list_deleted_memories,
    list_due_reminders,
    list_recent_memories,
    list_users,
    load_cli_config,
    make_preview,
    manage_tasks,
    restore_database,
    run_doctor,
    run_local_text_interaction,
    run_openai_checks,
    search_database,
    undelete_items,
)
from assistant_bot.database import AppDatabase
from assistant_bot.models import RoutingResult


def test_run_doctor_reports_missing_required_values() -> None:
    result = run_doctor({})

    assert not result.ok
    assert "- DISCORD_TOKEN: 누락" in result.lines
    assert "- OPENAI_API_KEY: 누락" in result.lines


def test_run_doctor_rejects_example_secret_values_and_invalid_timezone() -> None:
    result = run_doctor(
        {
            "DISCORD_TOKEN": "your_discord_bot_token",
            "OPENAI_API_KEY": "your_openai_api_key",
            "ASSISTANT_TIMEZONE": "Not/A_Timezone",
        }
    )

    assert not result.ok
    assert "- DISCORD_TOKEN: 예시값으로 보입니다" in result.lines
    assert "- OPENAI_API_KEY: 예시값으로 보입니다" in result.lines
    assert "- ASSISTANT_TIMEZONE 유효성: 알 수 없는 타임존 `Not/A_Timezone`" in result.lines


def test_run_doctor_accepts_required_values_and_numeric_defaults() -> None:
    result = run_doctor(
        {
            "DISCORD_TOKEN": "token",
            "OPENAI_API_KEY": "key",
            "MAX_ATTACHMENT_BYTES": "1024",
            "CONTEXT_COMPRESSION_CHARS": "2000",
            "RETRIEVAL_LIMIT": "3",
        }
    )

    assert result.ok
    assert "점검 상태: 통과" in result.lines
    assert "- ASSISTANT_TIMEZONE 유효성: 통과 (Asia/Seoul)" in result.lines


def test_run_doctor_validates_openai_retry_settings() -> None:
    result = run_doctor(
        {
            "DISCORD_TOKEN": "token",
            "OPENAI_API_KEY": "key",
            "OPENAI_TIMEOUT_SECONDS": "0",
            "OPENAI_MAX_RETRIES": "-1",
            "PENDING_CONFIRMATION_TTL_MINUTES": "0",
        }
    )

    assert not result.ok
    assert "- OPENAI_TIMEOUT_SECONDS: 양의 숫자여야 합니다" in result.lines
    assert "- OPENAI_MAX_RETRIES: 양의 정수여야 합니다" in result.lines
    assert "- PENDING_CONFIRMATION_TTL_MINUTES: 양의 정수여야 합니다" in result.lines


def test_build_invite_url_contains_client_id_and_bot_scope() -> None:
    url = build_invite_url("client-123")

    assert "client_id=client-123" in url
    assert "scope=bot" in url
    assert "permissions=" in url


def test_load_cli_config_requires_only_openai_key_for_local_ask() -> None:
    config = load_cli_config(
        {
            "OPENAI_API_KEY": "openai-key",
            "DATABASE_PATH": "./tmp.sqlite",
            "OPENAI_TIMEOUT_SECONDS": "12.5",
        }
    )

    assert config.discord_token == "local-cli"
    assert config.openai_api_key == "openai-key"
    assert config.database_path == "./tmp.sqlite"
    assert config.openai_timeout_seconds == 12.5


def test_load_cli_config_requires_openai_key() -> None:
    try:
        load_cli_config({})
    except RuntimeError as error:
        assert "OPENAI_API_KEY" in str(error)
    else:
        raise AssertionError("로컬 ask 실행에는 OPENAI_API_KEY가 필요합니다")


def test_format_route_result() -> None:
    output = format_route_result(RoutingResult("remember", 0.96, "명시적 기억 요청 감지"))

    assert "라우팅 미리보기:" in output
    assert "intent: `remember`" in output
    assert "confidence: 0.96" in output
    assert "명시적 기억 요청 감지" in output


def test_format_openai_check_results() -> None:
    output = format_openai_check_results(
        [
            OpenAICheckResult("텍스트 응답", True, "`gpt-5.4-mini` 응답 확인"),
            OpenAICheckResult("Embedding", False, "인증 실패"),
        ]
    )

    assert "OpenAI 연결 점검 결과:" in output
    assert "- 텍스트 응답: 통과" in output
    assert "- Embedding: 실패" in output
    assert "점검 상태: 보완 필요" in output


def test_manage_tasks_adds_lists_renames_postpones_and_completes(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"

    added = manage_tasks(
        str(database_path),
        user_id="user-1",
        add_title="제안서 초안 작성",
        priority="high",
        due_at="2026-06-10",
    )
    added_output = format_tasks_result(added)

    assert added["ok"]
    assert added["task_id"] == 1
    assert "할 일 `1`를 추가했습니다" in added_output
    assert "우선순위: 높음" in added_output
    assert "기한: 2026-06-10" in added_output

    duplicate = manage_tasks(
        str(database_path),
        user_id="user-1",
        add_title="  제안서 초안 작성  ",
        priority="low",
        due_at="2026-06-12",
    )
    duplicate_output = format_tasks_result(duplicate)

    assert duplicate["ok"]
    assert duplicate["action"] == "duplicate"
    assert duplicate["task_id"] == 1
    assert "같은 열린 할 일이 이미 있습니다" in duplicate_output

    listed = manage_tasks(str(database_path), user_id="user-1")
    listed_output = format_tasks_result(listed)

    assert listed["ok"]
    assert "user `user-1` 할 일 목록" in listed_output
    assert "제안서 초안 작성" in listed_output
    assert len(listed["items"]) == 1

    shown = manage_tasks(
        str(database_path),
        user_id="user-1",
        show_ids=[1],
    )
    shown_output = format_tasks_result(shown)

    assert shown["ok"]
    assert "할 일 상세" in shown_output
    assert "할 일 `1` · 제안서 초안 작성" in shown_output
    assert "- 기한: 2026-06-10" in shown_output
    assert "- 원본 메시지 ID: admin-cli" in shown_output

    renamed = manage_tasks(
        str(database_path),
        user_id="user-1",
        rename_ids=[1],
        new_title="고객 미팅 준비",
    )
    renamed_output = format_tasks_result(renamed)

    assert renamed["ok"]
    assert "할 일 제목 수정 결과: 1개" in renamed_output
    assert "새 제목: 고객 미팅 준비" in renamed_output
    assert "고객 미팅 준비" in renamed_output

    prioritized = manage_tasks(
        str(database_path),
        user_id="user-1",
        priority_ids=[1],
        priority="low",
    )
    prioritized_output = format_tasks_result(prioritized)

    assert prioritized["ok"]
    assert "할 일 우선순위 수정 결과: 1개" in prioritized_output
    assert "새 우선순위: 낮음" in prioritized_output

    postponed = manage_tasks(
        str(database_path),
        user_id="user-1",
        postpone_ids=[1],
        due_at="2026-06-11",
    )
    postponed_output = format_tasks_result(postponed)

    assert postponed["ok"]
    assert "할 일 미루기 결과: 1개" in postponed_output
    assert "새 기한: 2026-06-11" in postponed_output
    assert "기한: 2026-06-11" in postponed_output

    completed = manage_tasks(
        str(database_path),
        user_id="user-1",
        complete_ids=[1],
        status="all",
    )
    completed_output = format_tasks_result(completed)

    assert completed["ok"]
    assert "할 일 완료 결과: 1개" in completed_output
    assert "상태: completed" in completed_output

    reopened = manage_tasks(
        str(database_path),
        user_id="user-1",
        reopen_ids=[1],
        status="all",
    )
    reopened_output = format_tasks_result(reopened)

    assert reopened["ok"]
    assert "할 일 다시 열기 결과: 1개" in reopened_output
    assert "상태: open" in reopened_output

    deleted = manage_tasks(
        str(database_path),
        user_id="user-1",
        delete_ids=[1],
    )
    deleted_output = format_tasks_result(deleted)

    assert deleted["ok"]
    assert "할 일 삭제 결과: 1개" in deleted_output

    deleted_list = manage_tasks(
        str(database_path),
        user_id="user-1",
        deleted=True,
    )
    deleted_list_output = format_tasks_result(deleted_list)

    assert deleted_list["ok"]
    assert "삭제한 할 일 목록" in deleted_list_output
    assert "제안서 초안 작성" not in deleted_list_output
    assert "고객 미팅 준비" in deleted_list_output
    assert "삭제:" in deleted_list_output

    restored = manage_tasks(
        str(database_path),
        user_id="user-1",
        restore_ids=[1],
        status="all",
    )
    restored_output = format_tasks_result(restored)

    assert restored["ok"]
    assert "삭제한 할 일 복구 결과: 1개" in restored_output
    assert "상태: open" in restored_output
    assert "삭제:" not in restored_output


def test_manage_tasks_filters_due_before(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    manage_tasks(str(database_path), user_id="user-1", add_title="오늘 할 일", due_at="2026-06-04")
    manage_tasks(str(database_path), user_id="user-1", add_title="내일 오전 할 일", due_at="2026-06-05 09:00")
    manage_tasks(str(database_path), user_id="user-1", add_title="나중 할 일", due_at="2026-06-10")
    manage_tasks(str(database_path), user_id="user-1", add_title="기한 없는 할 일")

    result = manage_tasks(str(database_path), user_id="user-1", due_before="2026-06-04")
    output = format_tasks_result(result)

    assert result["ok"]
    assert "2026-06-04까지" in output
    assert "오늘 할 일" in output
    assert "내일 오전 할 일" not in output
    assert "나중 할 일" not in output
    assert "기한 없는 할 일" not in output

    tomorrow = manage_tasks(
        str(database_path),
        user_id="user-1",
        due_after="2026-06-05",
        due_before="2026-06-05",
    )
    tomorrow_output = format_tasks_result(tomorrow)

    assert "2026-06-05부터 2026-06-05까지" in tomorrow_output
    assert "내일 오전 할 일" in tomorrow_output
    assert "오늘 할 일" not in tomorrow_output
    assert "나중 할 일" not in tomorrow_output

    undated = manage_tasks(str(database_path), user_id="user-1", undated=True)
    undated_output = format_tasks_result(undated)

    assert "기한 없음" in undated_output
    assert "기한 없는 할 일" in undated_output
    assert "오늘 할 일" not in undated_output


def test_generate_cli_briefing_includes_due_tasks_and_recent_memories(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO tasks (user_id, conversation_id, channel_id, title, due_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("user-1", "admin:user-1", "admin-cli", "오늘 할 일", "2000-01-01"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, conversation_id, channel_id, title, due_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("user-1", "admin:user-1", "admin-cli", "나중 할 일", "2999-01-01"),
    )
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "최근 메모", "브리핑에 보여줄 기억", "[0.1, 0.2]", "m1"),
    )
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("channel:777:user:user-1", "user", "user-1", "서버에서 이어간 대화", "2026-06-05 01:00:00"),
    )
    connection.commit()

    output = generate_cli_briefing(str(database_path), user_id="user-1")

    assert "오늘 브리핑입니다" in output
    assert "열린 할 일: 2개" in output
    assert "오늘 할 일" in output
    assert "나중 할 일" not in output
    assert "최근 메모" in output
    assert "최근 대화 위치" in output
    assert "채널 `777`" in output


def test_list_due_reminders_previews_unsent_due_reminders(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO reminders (user_id, conversation_id, channel_id, text, remind_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("user-1", "dm:user-1", "dm", "곧 보낼 리마인더", "2026-06-05 09:00"),
    )
    connection.execute(
        """
        INSERT INTO reminders (user_id, conversation_id, channel_id, text, remind_at, sent_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", "dm:user-1", "dm", "이미 보낸 리마인더", "2026-06-05 08:00", "2026-06-05 08:01"),
    )
    connection.execute(
        """
        INSERT INTO reminders (user_id, conversation_id, channel_id, text, remind_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("user-2", "dm:user-2", "dm", "다른 사용자 리마인더", "2026-06-05 09:00"),
    )
    connection.commit()

    result = list_due_reminders(
        str(database_path),
        user_id="user-1",
        as_of="2026-06-05 09:30",
    )
    output = format_due_reminders(result)

    assert result["as_of"] == "2026-06-05 09:30"
    assert [item.text for item in result["items"]] == ["곧 보낼 리마인더"]
    assert "리마인더 발송 대상 1개" in output
    assert "곧 보낼 리마인더" in output
    assert "이미 보낸 리마인더" not in output
    assert "다른 사용자 리마인더" not in output


def test_build_user_snapshot_combines_memory_tasks_and_conversation_locations(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "집중 시간", "오전 집중 선호", "[0.1, 0.2]", "m1"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, priority, due_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "dm:user-1", "dm", "제안서 초안", "high", "2026-06-05"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, priority, due_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-2", None, "dm:user-2", "dm", "다른 사용자 작업", "high", "2026-06-05"),
    )
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "user", "user-1", "DM에서 시작한 대화", "2026-06-05 01:00:00"),
    )
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("thread:888:user:user-1", "user", "user-1", "스레드에서 이어간 대화", "2026-06-05 02:00:00"),
    )
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("thread:888:user:user-1", "assistant", "bot", "스레드 응답", "2026-06-05 02:01:00"),
    )
    connection.execute(
        """
        INSERT INTO pending_attachment_requests (
          conversation_id, channel_id, message_id, user_id, guild_id, filenames_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "dm", "m2", "user-1", None, "[]"),
    )
    connection.commit()

    snapshot = build_user_snapshot(
        str(database_path),
        user_id="user-1",
        limit=3,
        timezone_name="Asia/Seoul",
    )
    output = format_user_snapshot(snapshot)

    assert snapshot["memory_stats"]["memories"] == 1
    assert snapshot["task_stats"]["open"] == 1
    assert snapshot["pending_attachments"] == 1
    assert "user `user-1` 스냅샷" in output
    assert "제안서 초안" in output
    assert "다른 사용자 작업" not in output
    assert "최근 기억" in output
    assert "집중 시간" in output
    assert "최근 대화 위치" in output
    assert "스레드 `888`" in output
    assert "DM" in output


def test_manage_tasks_postpone_requires_due_date(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    manage_tasks(str(database_path), user_id="user-1", add_title="제안서 초안 작성")

    postponed = manage_tasks(str(database_path), user_id="user-1", postpone_ids=[1])
    output = format_tasks_result(postponed)

    assert not postponed["ok"]
    assert "--postpone에는 --due가 필요합니다." in output


def test_manage_tasks_rename_requires_title(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    manage_tasks(str(database_path), user_id="user-1", add_title="제안서 초안 작성")

    renamed = manage_tasks(str(database_path), user_id="user-1", rename_ids=[1])
    output = format_tasks_result(renamed)

    assert not renamed["ok"]
    assert "--rename에는 --title이 필요합니다." in output


def test_manage_tasks_priority_requires_priority_value(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    manage_tasks(str(database_path), user_id="user-1", add_title="제안서 초안 작성")

    prioritized = manage_tasks(str(database_path), user_id="user-1", priority_ids=[1])
    output = format_tasks_result(prioritized)

    assert not prioritized["ok"]
    assert "--set-priority에는 --priority가 필요합니다." in output


def test_run_openai_checks_with_fake_client() -> None:
    results = run_async(
        run_openai_checks(
            FakeOpenAIClient(),
            text_model="gpt-test",
            embedding_model="embedding-test",
        )
    )

    assert [result.ok for result in results] == [True, True]
    assert "gpt-test" in results[0].detail
    assert "차원 3" in results[1].detail


def test_collect_and_format_database_stats(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"

    stats = collect_database_stats(str(database_path))
    output = format_database_stats(stats, str(database_path))

    assert stats["memories"] == 0
    assert stats["documents"] == 0
    assert stats["pending_memory_deletions"] == 0
    assert "SQLite 저장소 상태" in output
    assert "텍스트 기억: 0개" in output
    assert "삭제 확인 대기 기억: 0개" in output


def test_initialize_database_creates_sqlite_and_reports_core_tables(tmp_path) -> None:
    database_path = tmp_path / "nested" / "assistant.sqlite"

    result = initialize_database(str(database_path))
    output = format_initialize_database_result(result)

    assert result["ok"] is True
    assert database_path.exists()
    assert result["missing_tables"] == []
    assert "user_memories" in result["tables"]
    assert "tasks" in result["tables"]
    assert "SQLite 저장소 초기화 결과" in output
    assert "핵심 테이블: 통과" in output
    assert "누락 테이블: 없음" in output


def test_list_and_format_users(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "사용자 1 메모", "활성 메모", "[0.1, 0.2]", "m1", "2026-06-04 10:00:00"),
    )
    connection.execute(
        """
        INSERT INTO user_memories (
          user_id, guild_id, title, text, embedding_json, source_message_id, created_at, deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "user-1",
            None,
            "삭제된 메모",
            "삭제 내용",
            "[0.1, 0.2]",
            "m2",
            "2026-06-04 10:01:00",
            "2026-06-04 10:02:00",
        ),
    )
    document_cursor = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-2", "guild-1", "plan.md", "text/markdown", "m3", "2026-06-04 10:03:00"),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (document_cursor.lastrowid, 0, "문서 본문", "[0.3, 0.4]"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, status, priority, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-3", None, "dm:user-3", "dm", "할 일만 있는 사용자", "open", "normal", "2026-06-04 10:04:00"),
    )
    connection.execute(
        """
        INSERT INTO tasks (
          user_id, guild_id, conversation_id, channel_id, title, status, priority, created_at, deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "user-3",
            None,
            "dm:user-3",
            "dm",
            "삭제된 할 일",
            "completed",
            "low",
            "2026-06-04 10:05:00",
            "2026-06-04 10:06:00",
        ),
    )
    connection.commit()

    users = list_users(str(database_path), limit=10)
    output = format_users(users)

    assert len(users) == 3
    memory_user = next(user for user in users if user["user_id"] == "user-1")
    assert memory_user["memory_count"] == 1
    assert memory_user["document_count"] == 0
    assert memory_user["task_count"] == 0
    assert memory_user["deleted_count"] == 1
    task_only_user = next(user for user in users if user["user_id"] == "user-3")
    assert task_only_user["memory_count"] == 0
    assert task_only_user["document_count"] == 0
    assert task_only_user["task_count"] == 1
    assert task_only_user["deleted_count"] == 1
    assert "사용자별 데이터 현황 3명" in output
    assert "user `user-1`" in output
    assert "할 일 1개" in output
    assert "삭제됨 1개" in output
    assert "user `user-2`" in output
    assert "user `user-3`" in output


def test_format_users_handles_empty_results() -> None:
    assert format_users([]) == "저장된 사용자가 없습니다."


def test_export_database_excludes_embeddings_and_includes_text(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "아침 선호", "오전에 집중이 잘 된다", "[0.1, 0.2]", "m1"),
    )
    document_cursor = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("user-1", "guild-1", "plan.md", "text/markdown", "m2"),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (document_cursor.lastrowid, 0, "문서 본문", "[0.3, 0.4]"),
    )
    connection.execute(
        """
        INSERT INTO tasks (
          user_id, guild_id, conversation_id, channel_id, title, status, priority, due_at, source_message_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "dm:user-1", "dm", "제안서 초안 작성", "open", "high", "2026-06-10", "m3"),
    )
    connection.commit()

    exported = export_database(str(database_path))

    assert exported["memories"][0]["text"] == "오전에 집중이 잘 된다"
    assert exported["memories"][0]["source_location"] == "DM"
    assert "embedding_json" not in exported["memories"][0]
    assert exported["documents"][0]["source_location"] == "서버"
    assert exported["documents"][0]["chunks"][0]["text"] == "문서 본문"
    assert "embedding_json" not in exported["documents"][0]["chunks"][0]
    assert exported["tasks"][0]["title"] == "제안서 초안 작성"
    assert exported["tasks"][0]["conversation_id"] == "dm:user-1"
    assert exported["tasks"][0]["source_message_id"] == "m3"
    assert exported["tasks"][0]["priority"] == "high"
    assert exported["tasks"][0]["due_at"] == "2026-06-10"


def test_export_database_filters_by_user_id(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "사용자 1", "사용자 1 메모", "[0.1, 0.2]", "m1"),
    )
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-2", None, "사용자 2", "사용자 2 메모", "[0.3, 0.4]", "m2"),
    )
    document_cursor = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("user-1", None, "user-1.md", "text/markdown", "m3"),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (document_cursor.lastrowid, 0, "사용자 1 문서", "[0.5, 0.6]"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, status, priority, due_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "dm:user-1", "dm", "사용자 1 열린 할 일", "open", "normal", None),
    )
    connection.execute(
        """
        INSERT INTO tasks (
          user_id, guild_id, conversation_id, channel_id, title, status, priority, due_at, deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        ("user-1", None, "dm:user-1", "dm", "사용자 1 삭제한 할 일", "completed", "low", "2026-06-10"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, status, priority, due_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-2", None, "dm:user-2", "dm", "사용자 2 할 일", "open", "normal", None),
    )
    connection.commit()

    exported = export_database(str(database_path), user_id="user-1")

    assert exported["user_id"] == "user-1"
    assert len(exported["memories"]) == 1
    assert exported["memories"][0]["user_id"] == "user-1"
    assert len(exported["documents"]) == 1
    assert exported["documents"][0]["user_id"] == "user-1"
    assert len(exported["tasks"]) == 2
    assert {task["user_id"] for task in exported["tasks"]} == {"user-1"}
    assert {task["title"] for task in exported["tasks"]} == {"사용자 1 열린 할 일", "사용자 1 삭제한 할 일"}
    assert any(task["deleted_at"] is not None for task in exported["tasks"])


def test_search_database_finds_memory_and_document_text(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "운동 루틴", "월수금 저녁에 운동한다", "[0.1, 0.2]", "m1"),
    )
    document_cursor = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("user-1", "guild-1", "meeting.md", "text/markdown", "m2"),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (document_cursor.lastrowid, 0, "회의에서 운동 캠페인을 논의했다", "[0.3, 0.4]"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, status, priority, due_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "dm:user-1", "dm", "운동 캠페인 제안서 작성", "open", "high", "2026-06-10"),
    )
    connection.commit()

    results = search_database(str(database_path), "운동", limit=10)
    output = format_search_results(results, "운동")

    assert len(results) == 3
    assert "메모 `1`" in output
    assert "문서 `1`" in output
    assert "할 일 `1`" in output
    assert "상태: open" in output
    assert "user `user-1`" in output
    assert "저장 위치: DM" in output
    assert "저장 위치: 서버" in output


def test_search_database_filters_by_user_id(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "운동 루틴", "월수금 저녁에 운동한다", "[0.1, 0.2]", "m1"),
    )
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-2", None, "운동 루틴", "토요일 오전에 운동한다", "[0.3, 0.4]", "m2"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, status, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "dm:user-1", "dm", "운동 기록 정리", "open", "normal"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, status, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-2", None, "dm:user-2", "dm", "운동 장비 확인", "open", "normal"),
    )
    connection.commit()

    results = search_database(str(database_path), "운동", limit=10, user_id="user-1")
    output = format_search_results(results, "운동", user_id="user-1")

    assert len(results) == 2
    assert {result["user_id"] for result in results} == {"user-1"}
    assert "검색 결과 2개 · user `user-1`" in output
    assert "user `user-2`" not in output


def test_list_and_format_conversations(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "user", "user-1", "첫 메시지", "2026-06-04 10:00:00"),
    )
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "assistant", "bot", "최근 답변", "2026-06-04 10:05:00"),
    )
    connection.execute(
        """
        INSERT INTO conversation_summaries (conversation_id, summary, created_at)
        VALUES (?, ?, ?)
        """,
        ("dm:user-1", "요약", "2026-06-04 10:06:00"),
    )
    connection.execute(
        """
        INSERT INTO conversation_summaries (conversation_id, summary, created_at)
        VALUES (?, ?, ?)
        """,
        ("dm:user-2", "요약만 있는 대화", "2026-06-04 10:07:00"),
    )
    connection.commit()

    conversations = list_conversations(str(database_path), limit=10)
    output = format_conversations(conversations)

    assert len(conversations) == 2
    assert conversations[0]["conversation_id"] == "dm:user-2"
    assert conversations[1]["conversation_id"] == "dm:user-1"
    assert conversations[1]["message_count"] == 2
    assert conversations[1]["summary_count"] == 1
    assert "대화 컨텍스트 2개" in output
    assert "`dm:user-1`" in output
    assert "미리보기: 최근 답변" in output


def test_format_conversations_handles_empty_results() -> None:
    assert format_conversations([]) == "저장된 대화 컨텍스트가 없습니다."


def test_clear_conversation_removes_messages_and_summaries_only(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content)
        VALUES (?, ?, ?, ?)
        """,
        ("dm:user-1", "user", "user-1", "지울 대화"),
    )
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content)
        VALUES (?, ?, ?, ?)
        """,
        ("dm:user-2", "user", "user-2", "남길 대화"),
    )
    connection.execute(
        """
        INSERT INTO conversation_summaries (conversation_id, summary)
        VALUES (?, ?)
        """,
        ("dm:user-1", "지울 요약"),
    )
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "장기 기억", "유지할 기억", "[0.1, 0.2]", "m1"),
    )
    connection.commit()

    result = clear_conversation(str(database_path), conversation_id="dm:user-1")
    output = format_clear_conversation_result(result)

    assert result["messages"] == 1
    assert result["summaries"] == 1
    assert "삭제된 메시지: 1개" in output
    assert "장기 기억과 문서는 삭제하지 않았습니다." in output
    assert count_table(connection, "conversation_messages") == 1
    assert count_table(connection, "conversation_summaries") == 0
    assert count_table(connection, "user_memories") == 1


def test_format_clear_conversation_result_handles_empty_context() -> None:
    output = format_clear_conversation_result(
        {
            "database_path": "assistant.sqlite",
            "conversation_id": "dm:missing",
            "messages": 0,
            "summaries": 0,
        }
    )

    assert "삭제된 메시지: 0개" in output
    assert "초기화할 대화 컨텍스트가 없었습니다." in output


def test_format_ingest_results() -> None:
    output = format_ingest_results(
        [
            {
                "ok": True,
                "path": "note.md",
                "status": "saved",
                "filename": "note.md",
                "document_id": 1,
                "chunk_count": 1,
                "detail": "문서 ID `1`, chunk 1개",
            },
            {
                "ok": False,
                "path": "broken.txt",
                "status": "failed",
                "detail": "ValueError: 실패",
            },
        ]
    )

    assert "로컬 파일 기억 처리 결과 2개" in output
    assert "저장: `note.md`" in output
    assert "실패: broken.txt" in output


def test_ingest_local_files_saves_documents_and_skips_duplicates(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    note_path = tmp_path / "note.md"
    note_path.write_text("회의 메모\n\n배포 일정은 금요일", encoding="utf-8")
    config = load_cli_config(
        {
            "OPENAI_API_KEY": "openai-key",
            "DATABASE_PATH": str(database_path),
        }
    )

    first = run_async(
        ingest_local_files(
            config=config,
            paths=[str(note_path)],
            user_id="user-1",
            openai=FakeEmbeddingService(),
        )
    )
    second = run_async(
        ingest_local_files(
            config=config,
            paths=[str(note_path)],
            user_id="user-1",
            openai=FakeEmbeddingService(),
        )
    )

    assert first[0]["status"] == "saved"
    assert first[0]["document_id"] == 1
    assert second[0]["status"] == "duplicate"
    assert second[0]["document_id"] == 1

    database = AppDatabase(str(database_path))
    row = database.connection.execute("SELECT filename FROM documents WHERE deleted_at IS NULL").fetchone()
    assert row["filename"] == "note.md"


def test_local_ask_extracts_recent_conversation_tasks(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    config = load_cli_config(
        {
            "OPENAI_API_KEY": "openai-key",
            "DATABASE_PATH": str(database_path),
        }
    )
    database = AppDatabase(str(database_path))
    database.connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content)
        VALUES (?, ?, ?, ?)
        """,
        ("local:user-1", "user", "user-1", "금요일까지 제안서 초안 작성해야 해. 팀에 일정 공유도 필요해."),
    )
    database.connection.commit()

    answer = run_async(
        run_local_text_interaction(
            config=config,
            text="최근 대화에서 할 일 뽑아서 추가해줘",
            user_id="user-1",
            conversation_id="local:user-1",
        )
    )

    assert "할 일 2개를 추가했어요" in answer
    task_rows = database.connection.execute(
        """
        SELECT title
        FROM tasks
        WHERE user_id = ?
        ORDER BY id ASC
        """,
        ("user-1",),
    ).fetchall()
    assert [row["title"] for row in task_rows] == [
        "금요일까지 제안서 초안 작성",
        "팀에 일정 공유도 필요해",
    ]


def test_list_and_format_recent_memories(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "운동 루틴", "월수금 저녁에 운동한다", "[0.1, 0.2]", "m1"),
    )
    document_cursor = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("user-1", "guild-1", "meeting.md", "text/markdown", "m2"),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (document_cursor.lastrowid, 0, "회의에서 배포 일정을 논의했다", "[0.3, 0.4]"),
    )
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-2", None, "다른 사용자", "다른 사용자 기억", "[0.5, 0.6]", "m3"),
    )
    connection.commit()

    all_items = list_recent_memories(str(database_path), limit=10)
    user_items = list_recent_memories(str(database_path), user_id="user-1", limit=10)
    document_items = list_recent_memories(str(database_path), user_id="user-1", kind="document", limit=10)
    output = format_recent_memories(user_items)

    assert len(all_items) == 3
    assert len(user_items) == 2
    assert len(document_items) == 1
    assert document_items[0]["kind"] == "document"
    assert "최근 저장 기억 2개" in output
    assert "메모 `1`" in output
    assert "문서 `1`" in output
    assert "user `user-1`" in output


def test_list_and_format_deleted_memories(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (
          user_id, guild_id, title, text, embedding_json, source_message_id, deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "삭제된 운동", "월수금 저녁 운동", "[0.1, 0.2]", "m1", "2026-06-04 10:00:00"),
    )
    document_cursor = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", "guild-1", "deleted.md", "text/markdown", "m2", "2026-06-04 10:05:00"),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (document_cursor.lastrowid, 0, "삭제된 문서 본문", "[0.3, 0.4]"),
    )
    connection.execute(
        """
        INSERT INTO user_memories (
          user_id, guild_id, title, text, embedding_json, source_message_id, deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-2", None, "다른 사용자", "다른 삭제", "[0.5, 0.6]", "m3", "2026-06-04 10:10:00"),
    )
    connection.commit()

    all_items = list_deleted_memories(str(database_path), limit=10)
    user_items = list_deleted_memories(str(database_path), user_id="user-1", limit=10)
    documents = list_deleted_memories(str(database_path), user_id="user-1", kind="document", limit=10)
    output = format_deleted_memories(user_items)

    assert len(all_items) == 3
    assert len(user_items) == 2
    assert len(documents) == 1
    assert documents[0]["kind"] == "document"
    assert "삭제된 기억 2개" in output
    assert "메모 `1`" in output
    assert "문서 `1`" in output
    assert "user `user-1`" in output
    assert "복구할 수 있습니다" in output


def test_format_deleted_memories_handles_empty_results() -> None:
    assert format_deleted_memories([]) == "삭제된 기억이 없습니다."


def test_undelete_items_restores_deleted_memory_and_document(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO user_memories (
          user_id, guild_id, title, text, embedding_json, source_message_id, deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "삭제된 메모", "복구할 메모", "[0.1, 0.2]", "m1", "2026-06-04 10:00:00"),
    )
    document_cursor = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "deleted.md", "text/markdown", "m2", "2026-06-04 10:05:00"),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (document_cursor.lastrowid, 0, "삭제된 문서", "[0.3, 0.4]"),
    )
    connection.commit()

    result = undelete_items(
        str(database_path),
        user_id="user-1",
        memory_ids=[1],
        document_ids=[1],
    )
    output = format_undelete_result(result)

    assert result["restored_total"] == 2
    assert "복구된 메모: 1개" in output
    assert "복구된 문서: 1개" in output
    assert list_deleted_memories(str(database_path), user_id="user-1") == []


def test_undelete_items_requires_at_least_one_id(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"

    try:
        undelete_items(str(database_path), user_id="user-1", memory_ids=[], document_ids=[])
    except ValueError as error:
        assert "--memory-id" in str(error)
    else:
        raise AssertionError("복구할 ID 없이 undelete가 실행되면 안 됩니다")


def test_format_recent_memories_handles_empty_results() -> None:
    assert format_recent_memories([]) == "저장된 기억이 없습니다."


def test_make_preview_centers_keyword() -> None:
    preview = make_preview("앞" * 80 + "키워드" + "뒤" * 80, "키워드", radius=4)

    assert preview.startswith("...")
    assert "키워드" in preview
    assert preview.endswith("...")


def test_fetch_and_format_agent_logs(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    connection.execute(
        """
        INSERT INTO agent_logs (conversation_id, agent, intent, difficulty, model, reason)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "router", "remember", None, "gpt-5.4-mini", "명시적 기억 요청"),
    )
    connection.execute(
        """
        INSERT INTO agent_logs (conversation_id, agent, intent, difficulty, model, reason)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "memory", "remember", "easy", "gpt-5.4-mini", "짧은 저장 확인"),
    )
    connection.commit()

    logs = fetch_agent_logs(str(database_path), agent="memory", limit=10)
    output = format_agent_logs(logs)

    assert len(logs) == 1
    assert logs[0]["agent"] == "memory"
    assert logs[0]["intent"] == "remember"
    assert "최근 에이전트 로그 1개" in output
    assert "difficulty `easy`" in output
    assert "conversation: dm:user-1" in output


def test_format_agent_logs_handles_empty_results() -> None:
    assert format_agent_logs([]) == "에이전트 로그가 없습니다."


def test_cleanup_database_previews_and_deletes_old_operational_rows(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    old_time = "2000-01-01 00:00:00"
    new_time = "2999-01-01 00:00:00"
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "user", "user-1", "오래된 대화", old_time),
    )
    connection.execute(
        """
        INSERT INTO conversation_messages (conversation_id, role, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "user", "user-1", "최근 대화", new_time),
    )
    connection.execute(
        """
        INSERT INTO conversation_summaries (conversation_id, summary, created_at)
        VALUES (?, ?, ?)
        """,
        ("dm:user-1", "오래된 요약", old_time),
    )
    connection.execute(
        """
        INSERT INTO agent_logs (conversation_id, agent, intent, created_at)
        VALUES (?, ?, ?, ?)
        """,
        ("dm:user-1", "router", "chat", old_time),
    )
    connection.execute(
        """
        INSERT INTO pending_attachment_requests (
          conversation_id, channel_id, message_id, user_id, guild_id, filenames_json, created_at, resolved_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "dm", "m1", "user-1", None, "[]", old_time, old_time),
    )
    connection.execute(
        """
        INSERT INTO pending_attachment_requests (
          conversation_id, channel_id, message_id, user_id, guild_id, filenames_json, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("dm:user-1", "dm", "m2", "user-1", None, "[]", old_time),
    )
    connection.commit()

    preview = cleanup_database(str(database_path), days=30, target="all", apply=False)
    preview_output = format_cleanup_result(preview)

    assert preview["applied"] is False
    assert preview["counts"]["conversation_messages"] == 1
    assert preview["counts"]["conversation_summaries"] == 1
    assert preview["counts"]["agent_logs"] == 1
    assert preview["counts"]["pending_attachment_requests"] == 1
    assert "실제로 삭제하려면" in preview_output
    assert count_table(connection, "conversation_messages") == 2

    applied = cleanup_database(str(database_path), days=30, target="all", apply=True)

    assert applied["applied"] is True
    assert count_table(connection, "conversation_messages") == 1
    assert count_table(connection, "conversation_summaries") == 0
    assert count_table(connection, "agent_logs") == 0
    assert count_table(connection, "pending_attachment_requests") == 1


def test_cleanup_database_deletes_old_soft_deleted_items(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    database = AppDatabase(str(database_path))
    connection = database.connection
    old_time = "2000-01-01 00:00:00"
    new_time = "2999-01-01 00:00:00"
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "오래된 삭제 메모", "삭제됨", "[0.1]", "m1", old_time),
    )
    connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "최근 삭제 메모", "최근 삭제됨", "[0.2]", "m2", new_time),
    )
    old_document = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "old.md", "text/markdown", "m3", old_time),
    )
    recent_document = connection.execute(
        """
        INSERT INTO documents (user_id, guild_id, filename, content_type, source_message_id, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "recent.md", "text/markdown", "m4", new_time),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (old_document.lastrowid, 0, "오래된 chunk", "[0.3]"),
    )
    connection.execute(
        """
        INSERT INTO document_chunks (document_id, chunk_index, text, embedding_json)
        VALUES (?, ?, ?, ?)
        """,
        (recent_document.lastrowid, 0, "최근 chunk", "[0.4]"),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "dm:user-1", "dm", "오래된 삭제 할 일", old_time),
    )
    connection.execute(
        """
        INSERT INTO tasks (user_id, guild_id, conversation_id, channel_id, title, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "dm:user-1", "dm", "최근 삭제 할 일", new_time),
    )
    connection.commit()

    preview = cleanup_database(str(database_path), days=30, target="deleted", apply=False)
    preview_output = format_cleanup_result(preview)

    assert preview["counts"]["deleted_user_memories"] == 1
    assert preview["counts"]["deleted_document_chunks"] == 1
    assert preview["counts"]["deleted_documents"] == 1
    assert preview["counts"]["deleted_tasks"] == 1
    assert "삭제된 메모: 1개" in preview_output
    assert count_table(connection, "user_memories") == 2
    assert count_table(connection, "documents") == 2
    assert count_table(connection, "document_chunks") == 2
    assert count_table(connection, "tasks") == 2

    applied = cleanup_database(str(database_path), days=30, target="deleted", apply=True)

    assert applied["applied"] is True
    assert count_table(connection, "user_memories") == 1
    assert count_table(connection, "documents") == 1
    assert count_table(connection, "document_chunks") == 1
    assert count_table(connection, "tasks") == 1


def test_backup_database_copies_sqlite_file_and_protects_existing_output(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    backup_path = tmp_path / "backup.sqlite"
    database = AppDatabase(str(database_path))
    database.connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "백업 테스트", "백업할 내용", "[0.1, 0.2]", "m1"),
    )
    database.connection.commit()
    database.connection.close()

    backup_database(str(database_path), str(backup_path))

    backup = AppDatabase(str(backup_path))
    row = backup.connection.execute("SELECT title, text FROM user_memories").fetchone()
    assert row["title"] == "백업 테스트"
    assert row["text"] == "백업할 내용"

    try:
        backup_database(str(database_path), str(backup_path))
    except FileExistsError:
        pass
    else:
        raise AssertionError("기존 백업 파일을 기본값으로 덮어쓰면 안 됩니다")


def test_restore_database_replaces_target_and_creates_safety_backup(tmp_path) -> None:
    database_path = tmp_path / "assistant.sqlite"
    restore_source_path = tmp_path / "restore-source.sqlite"

    database = AppDatabase(str(database_path))
    database.connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "복구 전", "기존 내용", "[0.1, 0.2]", "m1"),
    )
    database.connection.commit()
    database.connection.close()

    restore_source = AppDatabase(str(restore_source_path))
    restore_source.connection.execute(
        """
        INSERT INTO user_memories (user_id, guild_id, title, text, embedding_json, source_message_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("user-1", None, "복구 후", "복구된 내용", "[0.3, 0.4]", "m2"),
    )
    restore_source.connection.commit()
    restore_source.connection.close()

    safety_backup = restore_database(str(database_path), str(restore_source_path))

    restored = AppDatabase(str(database_path))
    row = restored.connection.execute("SELECT title, text FROM user_memories").fetchone()
    assert row["title"] == "복구 후"
    assert row["text"] == "복구된 내용"

    safety = AppDatabase(safety_backup)
    safety_row = safety.connection.execute("SELECT title, text FROM user_memories").fetchone()
    assert safety_row["title"] == "복구 전"
    assert safety_row["text"] == "기존 내용"


def run_async(coro):
    import asyncio

    return asyncio.run(coro)


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()
        self.embeddings = FakeEmbeddings()


class FakeResponses:
    async def create(self, **kwargs):
        return FakeTextResponse()


class FakeTextResponse:
    output_text = "OK"


class FakeEmbeddings:
    async def create(self, **kwargs):
        return FakeEmbeddingResponse()


class FakeEmbeddingResponse:
    data = [type("EmbeddingData", (), {"embedding": [0.1, 0.2, 0.3]})()]


class FakeEmbeddingService:
    async def embedding(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.5]


def count_table(connection, table: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
    return int(row["count"])
