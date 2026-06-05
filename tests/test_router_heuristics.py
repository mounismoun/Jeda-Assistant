from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from assistant_bot.agents import (
    asks_current_time,
    asks_to_clear_task_due,
    asks_to_complete_task,
    asks_to_complete_task_batch,
    asks_to_create_reminder,
    asks_to_create_task_from_recent_message,
    asks_to_delete_all_memories,
    asks_to_delete_latest_memory,
    asks_to_delete_latest_task,
    asks_to_extract_tasks,
    asks_to_list_deleted_memories,
    asks_to_list_deleted_tasks,
    asks_to_list_due_tasks,
    asks_to_list_reminders,
    asks_to_reference_latest_added_task,
    asks_to_remember_recent_message,
    asks_to_reopen_latest_completed_task,
    asks_to_restore_task,
    asks_to_search_memories,
    asks_to_search_tasks,
    asks_to_show_latest_memory,
    asks_to_show_latest_task_detail,
    asks_to_show_recent_reminder,
    asks_to_show_task_detail,
    asks_to_snooze_latest_reminded_task,
    asks_to_update_latest_memory,
    extract_due_date,
    extract_memory_search_query,
    extract_recall_ids,
    extract_restore_ids,
    extract_task_action_query,
    extract_task_candidates_from_messages,
    extract_task_creation,
    extract_task_ids,
    extract_task_list_status,
    extract_task_priority,
    extract_task_rename_title,
    extract_task_search_query,
    extract_update_ids,
    extract_update_query,
    extract_update_text,
    has_substantive_memory_text,
    heuristic_route,
    is_reminder_request,
    is_task_request,
)


def test_heuristic_route_remember() -> None:
    route = heuristic_route("이거 기억해줘: 오전에 집중이 잘 돼", False)

    assert route.intent == "remember"


def test_heuristic_route_help() -> None:
    route = heuristic_route("도움말 보여줘", False)

    assert route.intent == "help"


def test_heuristic_route_reminder_capability_question_is_help() -> None:
    route = heuristic_route("리마인드 기능은 없나?", False)

    assert route.intent == "help"


def test_heuristic_route_status() -> None:
    route = heuristic_route("상태 확인해줘", False)

    assert route.intent == "status"


def test_heuristic_route_current_time() -> None:
    route = heuristic_route("지금 몇시야?", False)

    assert route.intent == "current_time"
    assert asks_current_time("오늘 날짜가 뭐야?")


def test_heuristic_route_daily_briefing() -> None:
    route = heuristic_route("오늘 브리핑 해줘", False)

    assert route.intent == "daily_briefing"


def test_heuristic_route_cancel_pending() -> None:
    route = heuristic_route("아니 저장하지 마 취소해", False)

    assert route.intent == "cancel_pending"


def test_heuristic_route_reset_context() -> None:
    route = heuristic_route("대화 맥락 초기화해줘", False)

    assert route.intent == "reset_context"


def test_heuristic_route_manage_task() -> None:
    route = heuristic_route("할 일 추가: 금요일까지 제안서 초안 작성", False)

    assert route.intent == "manage_task"


def test_heuristic_route_manage_reminder() -> None:
    route = heuristic_route("30분 뒤 물 마시라고 알려줘", False)

    assert route.intent == "manage_reminder"


def test_heuristic_route_reminder_lookup() -> None:
    assert heuristic_route("현재 등록되어 있는 알림 목록", False).intent == "manage_reminder"
    assert heuristic_route("내가 아까 몇시에 알림 보내달라고 했지?", False).intent == "manage_reminder"
    assert asks_to_list_reminders("현재 등록되어 있는 알림 목록")
    assert asks_to_show_recent_reminder("내가 아까 몇시에 알림 보내달라고 했지?")


def test_heuristic_route_delete() -> None:
    route = heuristic_route("운동 관련 기억 삭제해줘", False)

    assert route.intent == "delete_memory"


def test_heuristic_route_restore() -> None:
    route = heuristic_route("방금 지운 거 복구해줘", False)

    assert route.intent == "restore_memory"


def test_heuristic_route_deleted_memory_list() -> None:
    route = heuristic_route("삭제한 기억 목록 보여줘", False)

    assert route.intent == "restore_memory"


def test_asks_to_delete_all_memories() -> None:
    assert asks_to_delete_all_memories("내 기억 전부 삭제해줘")
    assert asks_to_delete_all_memories("모든 문서와 메모를 지워줘")
    assert not asks_to_delete_all_memories("운동 관련 기억 삭제해줘")


def test_asks_to_delete_latest_memory() -> None:
    assert asks_to_delete_latest_memory("방금 저장한 거 지워줘")
    assert asks_to_delete_latest_memory("최근 기억 삭제해줘")
    assert asks_to_delete_latest_memory("delete last memory")
    assert not asks_to_delete_latest_memory("운동 관련 기억 삭제해줘")
    assert not asks_to_delete_latest_memory("최근 기억 보여줘")


def test_asks_to_list_deleted_memories() -> None:
    assert asks_to_list_deleted_memories("삭제한 기억 목록 보여줘")
    assert asks_to_list_deleted_memories("지운 메모 뭐 있어?")
    assert asks_to_list_deleted_memories("show deleted memories")
    assert not asks_to_list_deleted_memories("방금 지운 거 복구해줘")


def test_heuristic_route_update() -> None:
    route = heuristic_route("메모 3을 오전 운동 선호로 수정해줘", False)

    assert route.intent == "update_memory"


def test_heuristic_route_recall() -> None:
    route = heuristic_route("전에 저장한 문서 기준으로 알려줘", False)

    assert route.intent == "recall"


def test_heuristic_route_document_analysis_with_attachment() -> None:
    route = heuristic_route("이 이미지 분석해줘", True)

    assert route.intent == "analyze_document"


def test_heuristic_route_vision_quota_status() -> None:
    route = heuristic_route("오늘 남은 OCR 분석 용량 알려줘", False)

    assert route.intent == "analyze_document"


def test_heuristic_route_latest_memory_detail() -> None:
    route = heuristic_route("방금 저장한 거 보여줘", False)

    assert route.intent == "recall"
    assert asks_to_show_latest_memory("방금 저장한 거 보여줘")


def test_heuristic_route_list_memory() -> None:
    route = heuristic_route("지금 뭘 기억하고 있어?", False)

    assert route.intent == "list_memory"


def test_heuristic_route_memory_search() -> None:
    route = heuristic_route("운동 관련 기억 찾아줘", False)

    assert route.intent == "list_memory"
    assert asks_to_search_memories("운동 관련 기억 찾아줘")
    assert extract_memory_search_query("운동 관련 기억 찾아줘") == "운동"
    assert extract_memory_search_query("계약 문서 검색해줘") == "계약"


def test_substantive_memory_text_ignores_file_only_instruction() -> None:
    assert not has_substantive_memory_text("이 파일 기억해줘")
    assert has_substantive_memory_text("이거 기억해줘: 나는 오전에 집중이 잘 돼")
    assert not has_substantive_memory_text("메모 하나 할게")
    assert not has_substantive_memory_text("메모할게")
    assert asks_to_remember_recent_message("방금 말한 거 기억해줘")
    assert asks_to_remember_recent_message("그거 기억해줘")
    assert asks_to_remember_recent_message("이것도 저장해줘")
    assert not has_substantive_memory_text("방금 말한 거 기억해줘")
    assert not has_substantive_memory_text("그거 기억해줘")


def test_extract_recall_ids() -> None:
    assert extract_recall_ids("메모 3이랑 문서 2 보여줘") == ([3], [2])
    assert extract_recall_ids("메모 3 삭제해줘") == ([], [])


def test_extract_restore_ids() -> None:
    assert extract_restore_ids("메모 3이랑 문서 2 복구해줘") == ([3], [2])
    assert extract_restore_ids("memory 4 restore") == ([4], [])


def test_extract_update_request_parts() -> None:
    text = "메모 3을 나는 오전 운동을 선호한다로 수정해줘"

    assert extract_update_ids(text) == ([3], [])
    assert extract_update_text(text) == "나는 오전 운동을 선호한다"
    assert "메모 3" in extract_update_query(text)


def test_extract_update_request_without_id() -> None:
    text = "운동 관련 기억을 나는 저녁 운동을 선호한다로 바꿔줘"

    assert extract_update_ids(text) == ([], [])
    assert extract_update_text(text) == "나는 저녁 운동을 선호한다"
    assert "운동 관련 기억" in extract_update_query(text)


def test_extract_update_latest_memory_request() -> None:
    text = "방금 저장한 메모를 나는 저녁 운동을 선호한다로 바꿔줘"

    assert asks_to_update_latest_memory(text)
    assert extract_update_text(text) == "나는 저녁 운동을 선호한다"


def test_task_request_helpers() -> None:
    assert is_task_request("할 일 목록 보여줘")
    assert is_task_request("todo add review proposal")
    assert extract_task_list_status("완료한 할 일 보여줘") == "completed"
    assert extract_task_list_status("전체 할 일 목록 보여줘") == "all"
    assert extract_task_list_status("남은 할 일 목록 보여줘") == "open"
    assert extract_task_ids("할 일 3 완료했어") == [3]
    assert extract_task_ids("3번 내일 다시 알려줘") == [3]
    assert extract_task_ids("할 일 3을 고객 미팅 준비로 바꿔줘") == [3]
    assert extract_task_rename_title("할 일 3을 고객 미팅 준비로 바꿔줘") == "고객 미팅 준비"
    assert extract_task_ids("할 일 3 중요하게 표시해줘") == [3]
    assert extract_task_priority("할 일 3 중요하게 표시해줘") == "high"
    assert extract_task_ids("할 일 3 다시 열어줘") == [3]
    assert extract_task_ids("할 일 3 기한 없애줘") == [3]
    assert extract_task_ids("제안서 할 일 3일 뒤 다시 알려줘") == []
    assert asks_to_list_deleted_tasks("삭제한 할 일 목록 보여줘")
    assert asks_to_clear_task_due("할 일 3 기한 없애줘")
    assert asks_to_clear_task_due("방금 추가한 할 일 리마인더 제거해줘")
    assert asks_to_create_reminder("내일 오전 9시에 물 마시라고 알려줘")
    assert is_reminder_request("내일 오전 9시에 물 마시라고 알려줘")
    assert not is_task_request("내일 오전 9시에 물 마시라고 알려줘")
    assert asks_to_complete_task("오늘 할 일 다 했어")
    assert asks_to_complete_task_batch("오늘 할 일 다 했어")
    assert asks_to_complete_task_batch("모든 할 일 완료했어")
    assert asks_to_reopen_latest_completed_task("방금 완료한 할 일 되돌려줘")
    assert asks_to_delete_latest_task("방금 추가한 할 일 삭제해줘")
    assert asks_to_reference_latest_added_task("방금 추가한 할 일 내일 다시 알려줘")
    assert asks_to_reference_latest_added_task("방금 추가한 할 일 중요하게 표시해줘")
    assert asks_to_reference_latest_added_task("방금 추가한 할 일을 고객 미팅 준비로 바꿔줘")
    assert asks_to_create_task_from_recent_message("그거 할 일로 추가해줘")
    assert asks_to_create_task_from_recent_message("방금 말한 거 할 일로 등록해줘")
    assert asks_to_create_task_from_recent_message("this as a task add")
    assert not asks_to_create_task_from_recent_message("방금 추가한 할 일 보여줘")
    assert not asks_to_create_task_from_recent_message("할 일 추가: 제안서 작성")
    assert not asks_to_snooze_latest_reminded_task("30분 뒤 다시 알려줘")
    assert not asks_to_snooze_latest_reminded_task("2시간 후 나중에 알려줘")
    assert not asks_to_snooze_latest_reminded_task("할 일 3 30분 뒤 다시 알려줘")
    assert not asks_to_snooze_latest_reminded_task("방금 추가한 할 일 30분 뒤 다시 알려줘")
    assert extract_task_rename_title("방금 추가한 할 일을 고객 미팅 준비로 바꿔줘") == "고객 미팅 준비"
    assert asks_to_search_tasks("제안서 할 일 찾아줘")
    assert extract_task_search_query("제안서 관련 할 일 찾아줘") == "제안서"
    assert extract_task_action_query("제안서 할 일 완료했어") == "제안서"
    assert extract_task_action_query("3일 뒤까지 제안서 할 일 다시 알려줘") == "제안서"
    assert asks_to_show_task_detail("할 일 3 자세히 보여줘")
    assert asks_to_show_task_detail("방금 추가한 할 일 보여줘")
    assert asks_to_show_latest_task_detail("방금 추가한 할 일 보여줘")
    assert asks_to_restore_task("할 일 3 복구해줘")
    assert extract_task_ids("할 일 3 복구해줘") == [3]
    assert heuristic_route("오늘 할 일 뭐야?", False).intent == "manage_task"
    assert heuristic_route("내일 할 일 뭐야?", False).intent == "manage_task"
    assert heuristic_route("이번 주 할 일 보여줘", False).intent == "manage_task"
    assert heuristic_route("기한 없는 할 일 보여줘", False).intent == "manage_task"
    assert heuristic_route("할 일 추가: 내일 오전 9시까지 제안서 작성", False).intent == "manage_task"
    assert asks_to_list_due_tasks("내일 할 일 뭐야?")
    assert asks_to_list_due_tasks("이번 주 할 일 보여줘")
    assert asks_to_list_due_tasks("기한 없는 할 일 보여줘")
    assert not asks_to_list_due_tasks("할 일 추가: 내일 오전 9시까지 제안서 작성")
    assert not asks_to_list_due_tasks("제안서 할 일 내일 오전 9시 다시 알려줘")
    assert heuristic_route("삭제한 할 일 목록 보여줘", False).intent == "manage_task"
    assert heuristic_route("최근 대화에서 할 일 뽑아줘", False).intent == "manage_task"
    assert not asks_to_extract_tasks("할 일 추가: 회의록 정리")
    title, due_at = extract_task_creation("할 일 추가: 2026-06-10까지 제안서 초안 작성")
    assert title == "제안서 초안 작성"
    assert due_at == "2026-06-10"
    local_now = datetime.now(ZoneInfo("Asia/Seoul"))
    title, due_at = extract_task_creation("할 일 추가: 3일 뒤까지 제안서 초안 작성")
    assert title == "제안서 초안 작성"
    assert due_at == (local_now + timedelta(days=3)).strftime("%Y-%m-%d")
    title, due_at = extract_task_creation("내일 오전 9시에 물 마시라고 알려줘")
    assert title == "물 마시"
    assert due_at == (local_now + timedelta(days=1)).strftime("%Y-%m-%d") + " 09:00"


def test_extract_due_date_relative_expressions() -> None:
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    next_friday_days = 7 - now.weekday() + 4
    this_friday_days = 4 - now.weekday()
    if this_friday_days < 0:
        this_friday_days += 7

    assert extract_due_date("3일 뒤까지 제안서 초안 작성") == (now + timedelta(days=3)).strftime("%Y-%m-%d")
    assert extract_due_date("2주 후 운동 계획 정리") == (now + timedelta(days=14)).strftime("%Y-%m-%d")
    assert extract_due_date("다음 주 금요일까지 제안서 초안 작성") == (
        now + timedelta(days=next_friday_days)
    ).strftime("%Y-%m-%d")
    assert extract_due_date("이번 주 금요일까지 제안서 초안 작성") == (
        now + timedelta(days=this_friday_days)
    ).strftime("%Y-%m-%d")
    assert extract_due_date("다음주까지 정리") == (now + timedelta(days=7)).strftime("%Y-%m-%d")


def test_extract_due_date_uses_configured_timezone() -> None:
    fixed_utc_now = datetime(2026, 6, 4, 16, 0, tzinfo=UTC)

    assert extract_due_date("오늘까지 정리", timezone_name="Asia/Seoul", now=fixed_utc_now) == "2026-06-05"
    assert extract_due_date("오늘까지 정리", timezone_name="UTC", now=fixed_utc_now) == "2026-06-04"
    title, due_at = extract_task_creation(
        "할 일 추가: 오늘까지 제안서 초안 작성",
        timezone_name="Asia/Seoul",
        now=fixed_utc_now,
    )
    assert title == "제안서 초안 작성"
    assert due_at == "2026-06-05"


def test_extract_due_date_and_title_with_time_expressions() -> None:
    fixed_now = datetime(2026, 6, 5, 8, 30, tzinfo=ZoneInfo("Asia/Seoul"))

    title, due_at = extract_task_creation(
        "할 일 추가: 내일 오전 9시 30분까지 제안서 초안 작성",
        timezone_name="Asia/Seoul",
        now=fixed_now,
    )

    assert title == "제안서 초안 작성"
    assert due_at == "2026-06-06 09:30"
    assert extract_due_date("오늘 18:30까지 정리", timezone_name="Asia/Seoul", now=fixed_now) == "2026-06-05"
    assert extract_task_creation(
        "할 일 추가: 오후 3시에 고객에게 답장",
        timezone_name="Asia/Seoul",
        now=fixed_now,
    ) == ("고객에게 답장", "2026-06-05 15:00")
    assert extract_task_creation(
        "할 일 추가: 오전 7시에 운동",
        timezone_name="Asia/Seoul",
        now=fixed_now,
    ) == ("운동", "2026-06-06 07:00")
    assert extract_task_creation(
        "30분 뒤 물 마시라고 알려줘",
        timezone_name="Asia/Seoul",
        now=fixed_now,
    ) == ("물 마시", "2026-06-05 09:00")
    assert extract_task_creation(
        "2시간 후 스트레칭하라고 알려줘",
        timezone_name="Asia/Seoul",
        now=fixed_now,
    ) == ("스트레칭", "2026-06-05 10:30")


def test_extract_task_candidates_from_messages() -> None:
    rows = [
        {"role": "user", "content": "금요일까지 제안서 초안 작성해야 해. 팀에 일정 공유도 필요해."},
        {"role": "assistant", "content": "제가 정리해볼게요."},
        {"role": "user", "content": "금요일까지 제안서 초안 작성해야 해."},
    ]

    candidates = extract_task_candidates_from_messages(rows)

    assert len(candidates) == 2
    assert candidates[0][0] == "금요일까지 제안서 초안 작성"
    assert candidates[0][1] is not None
    assert candidates[1] == ("팀에 일정 공유도 필요해", None)
