from __future__ import annotations

import json
import re
from datetime import datetime, timedelta

from assistant_bot.models import RoutingResult, TaskItem
from assistant_bot.stores import normalize_task_priority
from assistant_bot.time_utils import now_in_timezone, resolve_timezone

DEFAULT_ALLOWED_INTENTS = {
    "chat",
    "help",
    "status",
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
}

DEFAULT_ROUTING_PROMPT_BLOCK = "\n".join(
    [
        "- chat: 일반 대화, 도움 요청, 저장된 기억이 필요 없는 질문",
        "- help: 사용법, 할 수 있는 일, 예시를 묻는 요청",
        "- status: 봇 상태, 설정 모델, 저장소 상태, 현재 동작 상태를 묻는 요청",
        "- cancel_pending: 직전 첨부 저장 확인이나 대기 중인 저장 요청을 취소하는 요청",
        "- remember: 사용자가 무언가를 기억/저장하라고 명시적으로 요청",
        "- recall: 저장된 기억이나 문서에 근거해 답해야 하는 질문",
        "- list_memory: 저장된 기억 목록, 상태, 개수, 무엇을 기억하는지 묻는 요청",
        "- update_memory: 저장된 텍스트 메모를 수정하거나 바꾸라는 요청",
        "- delete_memory: 저장된 기억이나 문서를 삭제/잊으라고 요청",
        "- restore_memory: 삭제한 기억이나 문서를 복구하거나, 삭제한 기억 목록을 보려는 요청",
        "- reset_context: 현재 대화의 최근 메시지와 압축 요약을 초기화하라는 요청. 장기 기억 삭제가 아님",
        "- manage_task: 할 일 추가, 조회, 완료, 삭제 요청",
        "- manage_reminder: 특정 시각에 사용자 DM으로 알림을 보내 달라는 요청",
        "- daily_briefing: 오늘 브리핑, 오늘 할 일과 최근 기억 요약 요청",
        "- unsupported: 처리할 수 없는 요청",
    ]
)



def heuristic_route(text: str, has_attachments: bool) -> RoutingResult:
    normalized = text.strip().lower()
    help_markers = ["도움말", "사용법", "뭘 할 수", "무엇을 할 수", "help", "how to use"]
    status_markers = ["상태", "정상", "status", "health", "설정", "모델 뭐", "어떤 모델"]
    cancel_markers = ["취소", "저장하지마", "저장하지 마", "기억하지마", "기억하지 마", "cancel", "never mind"]
    reset_context_markers = [
        "대화 맥락 초기화",
        "대화맥락초기화",
        "대화 초기화",
        "맥락 초기화",
        "컨텍스트 초기화",
        "대화 기록 초기화",
        "reset context",
        "clear context",
    ]
    remember_markers = ["기억해", "저장해", "기억해줘", "저장해줘", "remember", "save this"]
    update_markers = ["수정해", "고쳐", "바꿔", "업데이트", "update", "change"]
    delete_markers = ["삭제해", "지워", "잊어", "forget", "delete"]
    restore_markers = ["복구", "되돌려", "되살려", "restore", "undo delete"]
    list_markers = ["목록", "리스트", "뭘 기억", "무엇을 기억", "기억 상태", "저장 상태", "list memories"]
    recall_markers = ["기억", "저장한", "전에", "문서", "파일", "회의록", "recall"]

    if asks_for_daily_briefing(text):
        return RoutingResult("daily_briefing", 0.96, "오늘 브리핑 요청 감지")
    if any(marker in normalized for marker in help_markers):
        return RoutingResult("help", 0.96, "도움말 요청 감지")
    if asks_about_capability(text):
        return RoutingResult("help", 0.95, "기능 문의 감지")
    if is_reminder_request(text):
        return RoutingResult("manage_reminder", 0.95, "사용자 알림 예약 요청 감지")
    if is_task_request(text):
        return RoutingResult("manage_task", 0.95, "할 일 관리 요청 감지")
    if any(marker in normalized for marker in status_markers):
        return RoutingResult("status", 0.94, "상태 조회 요청 감지")
    if any(marker in normalized for marker in cancel_markers):
        return RoutingResult("cancel_pending", 0.95, "대기 작업 취소 의도 감지")
    if any(marker in normalized for marker in reset_context_markers):
        return RoutingResult("reset_context", 0.95, "현재 대화 맥락 초기화 요청 감지")
    if any(marker in normalized for marker in update_markers):
        return RoutingResult("update_memory", 0.95, "기억 수정 의도 표현 감지")
    if asks_to_list_deleted_memories(text):
        return RoutingResult("restore_memory", 0.95, "삭제 기억 목록 조회 의도 감지")
    if any(marker in normalized for marker in restore_markers):
        return RoutingResult("restore_memory", 0.95, "삭제 기억 복구 의도 표현 감지")
    if any(marker in normalized for marker in delete_markers):
        return RoutingResult("delete_memory", 0.95, "삭제 의도 표현 감지")
    if any(marker in normalized for marker in remember_markers):
        return RoutingResult("remember", 0.96, "명시적 기억 요청 감지")
    if asks_to_show_latest_memory(text):
        return RoutingResult("recall", 0.95, "최근 저장 기억 상세 조회 요청 감지")
    if asks_to_search_memories(text):
        return RoutingResult("list_memory", 0.95, "저장 기억 검색 요청 감지")
    if any(marker in normalized for marker in list_markers):
        return RoutingResult("list_memory", 0.95, "기억 목록 조회 의도 감지")
    if has_attachments and not normalized:
        return RoutingResult("chat", 0.95, "첨부만 있어 저장 확인 필요")
    if any(marker in normalized for marker in recall_markers):
        return RoutingResult("recall", 0.78, "저장 정보 회상 가능성 감지")
    return RoutingResult("chat", 0.7, "일반 대화로 판단")


def parse_routing_result(output: str, *, allowed_intents: set[str] | None = None) -> RoutingResult:
    try:
        match = re.search(r"\{.*\}", output, flags=re.DOTALL)
        data = json.loads(match.group(0) if match else output)
        intent = data.get("intent", "chat")
        if intent not in (allowed_intents or DEFAULT_ALLOWED_INTENTS):
            intent = "chat"
        return RoutingResult(
            intent=intent,
            confidence=float(data.get("confidence", 0.5)),
            reason=str(data.get("reason", "라우터 응답")),
        )
    except Exception:
        return RoutingResult("chat", 0.3, "라우터 JSON 파싱 실패")


def extract_memory_text(text: str) -> str:
    cleaned = re.sub(
        r"(이거|이 내용|내용|메모)?\s*(기억해줘|기억해|저장해줘|저장해|remember|save this)[:：]?",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    return cleaned or text.strip()


def asks_to_remember_recent_message(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    pronoun_pattern = (
        r"^\s*(?:그거|그것|이거|이것|that|it)\s*(?:도|을|를)?\s*"
        r"(?:기억해줘|기억해|저장해줘|저장해|remember|save)\s*\.?\s*$"
    )
    if re.search(pronoun_pattern, normalized, flags=re.IGNORECASE):
        return True
    recent_markers = ["방금", "직전", "위에", "아까", "latest", "last", "previous"]
    content_markers = ["말한", "얘기한", "내용", "메시지", "대화", "that", "it"]
    remember_markers = ["기억", "저장", "remember", "save"]
    return (
        any(marker in normalized or marker in compact for marker in recent_markers)
        and any(marker in normalized or marker in compact for marker in content_markers)
        and any(marker in normalized or marker in compact for marker in remember_markers)
    )


def asks_to_show_latest_memory(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    memory_markers = ["저장", "기억", "메모", "문서", "파일", "memory", "document", "doc"]
    show_markers = ["보여", "확인", "뭐", "무엇", "알려", "show", "what"]
    return (
        any(marker in normalized or marker in compact for marker in latest_markers)
        and any(marker in normalized or marker in compact for marker in memory_markers)
        and any(marker in normalized or marker in compact for marker in show_markers)
    )


def has_substantive_memory_text(text: str) -> bool:
    if asks_to_remember_recent_message(text):
        return False
    cleaned = extract_memory_text(text)
    instruction_words = [
        "이 파일",
        "파일",
        "첨부",
        "문서",
        "내용",
        "this file",
        "attachment",
        "document",
    ]
    normalized = cleaned.strip().lower()
    return bool(normalized) and normalized not in instruction_words and len(normalized) >= 4


def extract_delete_query(text: str) -> str:
    cleaned = re.sub(
        r"(기억|메모|문서|파일)?\s*(삭제해줘|삭제해|지워줘|지워|잊어줘|잊어|forget|delete)[:：]?",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    return cleaned or text.strip()


def asks_to_delete_all_memories(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text.casefold())
    delete_markers = ["삭제", "지워", "잊어", "forget", "delete"]
    all_markers = ["전부", "전체", "모두", "다", "모든", "all"]
    memory_markers = ["기억", "메모", "문서", "파일", "memory", "memories", "document"]
    return (
        any(marker in normalized for marker in delete_markers)
        and any(marker in normalized for marker in all_markers)
        and any(marker in normalized for marker in memory_markers)
    )


def asks_to_delete_latest_memory(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text.casefold())
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    delete_markers = ["삭제", "지워", "잊어", "forget", "delete", "remove"]
    return any(marker in normalized for marker in latest_markers) and any(
        marker in normalized for marker in delete_markers
    )


def asks_to_update_latest_memory(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    memory_markers = ["저장", "기억", "메모", "memory"]
    update_markers = ["수정", "고쳐", "바꿔", "변경", "업데이트", "update", "change"]
    return (
        any(marker in normalized or marker in compact for marker in latest_markers)
        and any(marker in normalized or marker in compact for marker in memory_markers)
        and any(marker in normalized or marker in compact for marker in update_markers)
    )


def asks_to_list_deleted_memories(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text.casefold())
    deleted_markers = ["삭제한", "지운", "잊은", "deleted", "trash"]
    list_markers = ["목록", "리스트", "보여", "뭐", "무엇", "list", "show"]
    return any(marker in normalized for marker in deleted_markers) and any(
        marker in normalized for marker in list_markers
    )


def asks_to_search_memories(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    memory_markers = ["기억", "메모", "문서", "파일", "memory", "memories", "document", "doc"]
    search_markers = ["검색", "찾아", "찾아줘", "관련", "search", "find"]
    return any(marker in normalized or marker in compact for marker in memory_markers) and any(
        marker in normalized or marker in compact for marker in search_markers
    )


def extract_memory_search_query(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(
        r"(?:기억|메모|문서|파일|memory|memories|document|doc)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:관련|검색해줘|검색해|검색|찾아줘|찾아|보여줘|보여|알려줘|알려|search|find|show)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" :：,，")
    return cleaned


def extract_delete_ids(text: str) -> tuple[list[int], list[int]]:
    memory_ids = [int(match) for match in re.findall(r"(?:메모|기억|memory)\s*#?(\d+)", text, re.I)]
    document_ids = [int(match) for match in re.findall(r"(?:문서|파일|document|doc)\s*#?(\d+)", text, re.I)]
    return memory_ids, document_ids


def extract_restore_ids(text: str) -> tuple[list[int], list[int]]:
    memory_ids = [int(match) for match in re.findall(r"(?:메모|기억|memory)\s*#?(\d+)", text, re.I)]
    document_ids = [int(match) for match in re.findall(r"(?:문서|파일|document|doc)\s*#?(\d+)", text, re.I)]
    return memory_ids, document_ids


def extract_update_ids(text: str) -> tuple[list[int], list[int]]:
    memory_ids = [int(match) for match in re.findall(r"(?:메모|기억|memory)\s*#?(\d+)", text, re.I)]
    document_ids = [int(match) for match in re.findall(r"(?:문서|파일|document|doc)\s*#?(\d+)", text, re.I)]
    return memory_ids, document_ids


def extract_update_text(text: str) -> str:
    patterns = [
        r"(?:메모|기억|memory)\s*#?\d+\s*(?:을|를)?\s*(?P<value>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|고쳐줘|고쳐|업데이트해줘|업데이트해|update|change)\.?$",
        r"(?:방금|최근|마지막|직전).+?(?:저장한\s*)?(?:메모|기억|memory)\s*(?:을|를)?\s*(?P<value>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|고쳐줘|고쳐|변경해줘|변경해|업데이트해줘|업데이트해|update|change)\.?$",
        r".+?(?:을|를)\s*(?P<value>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|고쳐줘|고쳐|업데이트해줘|업데이트해)\.?$",
        r"(?:수정|변경|업데이트)\s*(?:내용)?\s*[:：]\s*(?P<value>.+)$",
        r"(?:to|as)\s+['\"]?(?P<value>.+?)['\"]?\s*(?:update|change)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.strip(), flags=re.IGNORECASE)
        if match:
            return match.group("value").strip(" '\"")
    return ""


def extract_update_query(text: str) -> str:
    cleaned = re.sub(
        r"(?:수정해줘|수정해|바꿔줘|바꿔|고쳐줘|고쳐|업데이트해줘|업데이트해|update|change)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?:로|으로)\s*$", "", cleaned.strip())
    replacement = extract_update_text(text)
    if replacement:
        cleaned = cleaned.replace(replacement, "")
    return cleaned.strip()


def extract_recall_ids(text: str) -> tuple[list[int], list[int]]:
    if any(marker in text.lower() for marker in ["삭제", "지워", "delete", "forget"]):
        return [], []
    memory_ids = [int(match) for match in re.findall(r"(?:메모|기억|memory)\s*#?(\d+)", text, re.I)]
    document_ids = [int(match) for match in re.findall(r"(?:문서|파일|document|doc)\s*#?(\d+)", text, re.I)]
    return memory_ids, document_ids


def is_task_request(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    task_markers = ["할 일", "할일", "태스크", "task", "todo", "to-do", "체크리스트"]
    reminder_markers = ["리마인드", "remind", "나중에 알려", "다시 알려", "챙겨"]
    reminder_action_markers = ["알려", "말해", "챙겨", "remind me"]
    if asks_about_capability(text):
        return False
    if any(marker in normalized for marker in task_markers) or any(marker in compact for marker in ["할일"]):
        return True
    if is_reminder_request(text):
        return False
    return any(marker in normalized for marker in reminder_markers) and any(
        marker in normalized or marker in compact for marker in reminder_action_markers
    )


def is_reminder_request(text: str) -> bool:
    if not asks_to_create_reminder(text):
        return False
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    if any(marker in normalized or marker in compact for marker in ["방금 추가한", "최근 추가한", "latest task"]):
        return False
    if re.search(r"(?:할\s*일|할일|태스크|task|todo|to-do)\s*#?\d+", normalized):
        return False
    if re.search(r"#?\d+\s*번", normalized):
        return False
    task_markers = ["할 일", "할일", "태스크", "task", "todo", "to-do", "체크리스트"]
    if any(marker in normalized or marker in compact for marker in task_markers):
        return False
    return True


def asks_about_capability(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    capability_markers = [
        "기능",
        "지원",
        "가능",
        "할수",
        "할 수",
        "되나",
        "돼",
        "되냐",
        "없나",
        "있나",
        "되나요",
        "가능해",
        "can you",
        "do you support",
    ]
    question_markers = ["?", "뭐", "무엇", "어떻게", "있", "없", "되", "가능", "can", "support"]
    return any(marker in normalized or marker in compact for marker in capability_markers) and any(
        marker in normalized or marker in compact for marker in question_markers
    )


def asks_to_create_reminder(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    notify_markers = ["알려줘", "알려 줘", "말해줘", "말해 줘", "챙겨줘", "챙겨 줘", "remind me"]
    return extract_due_at(text) is not None and any(
        marker in normalized or marker in compact for marker in notify_markers
    )


def asks_for_daily_briefing(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    briefing_markers = ["브리핑", "요약", "briefing", "brief", "daily"]
    today_markers = ["오늘", "일일", "daily", "today"]
    return any(marker in normalized or marker in compact for marker in briefing_markers) and any(
        marker in normalized or marker in compact for marker in today_markers
    )


def asks_to_list_tasks(text: str) -> bool:
    normalized = text.casefold()
    list_markers = ["목록", "리스트", "보여", "뭐", "무엇", "남은", "조회", "list", "show"]
    return is_task_request(text) and any(marker in normalized for marker in list_markers)


def extract_task_list_status(text: str) -> str:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    completed_markers = ["완료한", "완료된", "끝낸", "처리한", "completed", "done", "finished"]
    all_markers = ["전체", "모든", "전부", "all"]
    open_markers = ["열린", "남은", "미완료", "open", "remaining"]
    if any(marker in normalized or marker in compact for marker in completed_markers):
        return "completed"
    if any(marker in normalized or marker in compact for marker in all_markers):
        return "all"
    if any(marker in normalized or marker in compact for marker in open_markers):
        return "open"
    return "open"


def asks_to_search_tasks(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    search_markers = ["검색", "찾아", "찾아줘", "관련", "search", "find"]
    return is_task_request(text) and any(marker in normalized or marker in compact for marker in search_markers)


def asks_to_show_task_detail(text: str) -> bool:
    normalized = text.casefold()
    detail_markers = ["상세", "자세", "보여", "확인", "정보", "detail", "show"]
    return is_task_request(text) and (
        asks_to_show_latest_task_detail(text)
        or (bool(extract_task_ids(text)) and any(marker in normalized for marker in detail_markers))
    )


def asks_to_show_latest_task_detail(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    show_markers = ["보여", "확인", "뭐", "무엇", "show", "what"]
    return (
        asks_to_reference_latest_added_task(text)
        and not asks_to_postpone_task(text)
        and not asks_to_delete_task(text)
        and any(marker in normalized or marker in compact for marker in show_markers)
    )


def asks_to_list_deleted_tasks(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    deleted_markers = ["삭제한", "삭제된", "지운", "deleted", "trash"]
    list_markers = ["목록", "리스트", "보여", "뭐", "무엇", "조회", "list", "show"]
    return is_task_request(text) and any(
        marker in normalized or marker in compact for marker in deleted_markers
    ) and any(marker in normalized or marker in compact for marker in list_markers)


def asks_to_list_due_tasks(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    if asks_to_create_reminder(text):
        return False
    if any(marker in normalized or marker in compact for marker in ["추가", "등록", "만들어", "add", "create"]):
        return False
    postpone_markers = ["미뤄", "미루", "연기", "다시 알려", "나중에 알려", "snooze", "postpone", "remind later"]
    if any(marker in normalized or marker in compact for marker in postpone_markers):
        return False
    list_markers = ["뭐", "무엇", "목록", "리스트", "보여", "조회", "알려", "list", "show"]
    due_markers = [
        "오늘",
        "내일",
        "이번 주",
        "이번주",
        "기한",
        "마감",
        "급한",
        "늦은",
        "지난",
        "없는",
        "overdue",
        "due",
        "today",
        "tomorrow",
        "week",
        "undated",
    ]
    return (
        is_task_request(text)
        and any(marker in normalized or marker in compact for marker in due_markers)
        and any(marker in normalized or marker in compact for marker in list_markers)
    )


def asks_to_extract_tasks(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    extraction_action_markers = ["뽑아", "추출", "extract"]
    conversation_markers = ["최근 대화", "최근대화", "대화에서", "from conversation"]
    return is_task_request(text) and (
        any(marker in normalized or marker in compact for marker in extraction_action_markers)
        or any(marker in normalized or marker in compact for marker in conversation_markers)
    )


def extract_task_due_filter(text: str, timezone_name: str | None) -> dict[str, str | bool | None]:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    now = now_in_timezone(timezone_name)
    today = now.strftime("%Y-%m-%d")

    if any(marker in normalized or marker in compact for marker in ["기한 없는", "마감 없는", "undated", "no due"]):
        return {
            "heading": "기한 없는 할 일",
            "empty_label": "기한 없는",
            "due_after": None,
            "due_before": None,
            "undated": True,
        }

    if any(marker in normalized or marker in compact for marker in ["늦은", "지난", "overdue"]):
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        return {
            "heading": "기한이 지난 할 일",
            "empty_label": "기한이 지난",
            "due_after": None,
            "due_before": yesterday,
            "undated": False,
        }

    if any(marker in normalized or marker in compact for marker in ["내일", "tomorrow"]):
        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        return {
            "heading": "내일 처리할 할 일",
            "empty_label": "내일 처리할",
            "due_after": tomorrow,
            "due_before": tomorrow,
            "undated": False,
        }

    if any(marker in normalized or marker in compact for marker in ["이번 주", "이번주", "this week", "week"]):
        days_until_sunday = 6 - now.weekday()
        sunday = (now + timedelta(days=days_until_sunday)).strftime("%Y-%m-%d")
        return {
            "heading": "이번 주 처리할 할 일",
            "empty_label": "이번 주 처리할",
            "due_after": today,
            "due_before": sunday,
            "undated": False,
        }

    return {
        "heading": "오늘까지 처리할 할 일",
        "empty_label": "오늘까지 처리해야 하는",
        "due_after": None,
        "due_before": today,
        "undated": False,
    }


def asks_to_save_extracted_tasks(text: str) -> bool:
    normalized = text.casefold()
    save_markers = ["추가", "등록", "저장", "만들어", "add", "save", "create"]
    return any(marker in normalized for marker in save_markers)


def asks_to_complete_task(text: str) -> bool:
    normalized = text.casefold()
    complete_markers = [
        "완료",
        "끝냈",
        "끝났",
        "처리했",
        "끝남",
        "다 했",
        "다했",
        "done",
        "finish",
        "finished",
        "complete",
    ]
    return is_task_request(text) and any(marker in normalized for marker in complete_markers)


def asks_to_complete_task_batch(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    batch_markers = ["다", "모두", "전체", "전부", "모든", "all"]
    return asks_to_complete_task(text) and any(marker in normalized or marker in compact for marker in batch_markers)


def has_task_due_filter_marker(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    due_markers = [
        "오늘",
        "내일",
        "이번 주",
        "이번주",
        "기한 없는",
        "마감 없는",
        "늦은",
        "지난",
        "overdue",
        "today",
        "tomorrow",
        "week",
        "undated",
    ]
    return any(marker in normalized or marker in compact for marker in due_markers)


def asks_to_reopen_task(text: str) -> bool:
    normalized = text.casefold()
    reopen_markers = ["다시 열", "완료 취소", "되돌려", "미완료", "reopen", "undo complete"]
    return is_task_request(text) and any(marker in normalized for marker in reopen_markers)


def asks_to_reopen_latest_completed_task(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    completed_markers = ["완료", "끝낸", "끝낸거", "끝낸 것", "done", "completed"]
    return asks_to_reopen_task(text) and any(
        marker in normalized or marker in compact for marker in latest_markers
    ) and any(marker in normalized or marker in compact for marker in completed_markers)


def asks_to_restore_task(text: str) -> bool:
    normalized = text.casefold()
    restore_markers = ["복구", "삭제 취소", "지운 거 취소", "restore", "undo delete"]
    return is_task_request(text) and any(marker in normalized for marker in restore_markers)


def asks_to_postpone_task(text: str) -> bool:
    normalized = text.casefold()
    postpone_markers = ["미뤄", "미루", "연기", "다시 알려", "나중에 알려", "snooze", "postpone", "remind later"]
    return is_task_request(text) and any(marker in normalized for marker in postpone_markers)


def asks_to_snooze_latest_reminded_task(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    snooze_markers = ["다시 알려", "나중에 알려", "snooze", "remind later"]
    id_markers = extract_task_ids(text)
    return (
        asks_to_postpone_task(text)
        and not id_markers
        and not asks_to_reference_latest_added_task(text)
        and not extract_task_action_query(text)
        and any(marker in normalized or marker in compact for marker in snooze_markers)
    )


def asks_to_clear_task_due(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    due_markers = ["기한", "마감", "리마인더", "리마인드", "due", "deadline", "reminder"]
    clear_markers = ["없애", "지워", "삭제", "빼", "제거", "취소", "clear", "remove"]
    return is_task_request(text) and any(
        marker in normalized or marker in compact for marker in due_markers
    ) and any(marker in normalized or marker in compact for marker in clear_markers)


def asks_to_rename_task(text: str) -> bool:
    normalized = text.casefold()
    rename_markers = ["수정", "변경", "바꿔", "이름", "제목", "rename", "change"]
    return is_task_request(text) and any(marker in normalized for marker in rename_markers)


def asks_to_set_task_priority(text: str) -> bool:
    normalized = text.casefold()
    priority_markers = ["우선순위", "중요", "긴급", "높음", "낮음", "priority", "important", "urgent"]
    return is_task_request(text) and any(marker in normalized for marker in priority_markers)


def asks_to_delete_task(text: str) -> bool:
    normalized = text.casefold()
    delete_markers = ["삭제", "지워", "취소", "delete", "remove"]
    return is_task_request(text) and any(marker in normalized for marker in delete_markers)


def asks_to_delete_latest_task(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    delete_markers = ["삭제", "지워", "취소", "delete", "remove"]
    return asks_to_reference_latest_added_task(text) and any(
        marker in normalized or marker in compact for marker in delete_markers
    )


def asks_to_reference_latest_added_task(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    create_markers = ["추가", "등록", "만든", "만들", "저장", "add", "created"]
    return (
        is_task_request(text)
        and any(marker in normalized or marker in compact for marker in latest_markers)
        and any(marker in normalized or marker in compact for marker in create_markers)
    )


def asks_to_create_task_from_recent_message(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    reference_markers = [
        "그거",
        "그것",
        "이거",
        "이것",
        "방금 말한",
        "방금말한",
        "방금 얘기한",
        "방금얘기한",
        "직전에 말한",
        "직전말한",
        "위 내용",
        "위내용",
        "this",
        "that",
    ]
    create_markers = ["추가", "등록", "만들", "저장", "add", "create", "save"]
    return is_task_request(text) and any(
        marker in normalized or marker in compact for marker in reference_markers
    ) and any(marker in normalized or marker in compact for marker in create_markers)


def extract_task_search_query(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(
        r"(?:할\s*일|할일|태스크|task|todo|to-do)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:검색해줘|검색해|검색|찾아줘|찾아|관련|조회해줘|조회해|search|find)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?:중|에서|관련된|관련한|관련)\s*", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" '\"`.,:：")
    return cleaned


def extract_task_action_query(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"(?:할\s*일|할일|태스크|task|todo|to-do)", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\d{4}-\d{1,2}-\d{1,2}(?:까지|에|까지는)?", " ", cleaned)
    cleaned = re.sub(r"\d{1,2}\s*월\s*\d{1,2}\s*일(?:까지|에|까지는)?", " ", cleaned)
    cleaned = re.sub(r"\d+\s*(?:일|주)\s*(?:뒤|후)(?:까지|에|까지는)?", " ", cleaned)
    cleaned = re.sub(r"\d+\s*(?:분|시간)\s*(?:뒤|후)(?:까지|에|까지는)?", " ", cleaned)
    cleaned = remove_due_time_text(cleaned)
    cleaned = re.sub(r"#?\d+", " ", cleaned)
    cleaned = re.sub(
        r"(?:오늘|내일|모레|이번 주|이번주|다음 주|다음주|"
        r"월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:까지|에|까지는)?",
        " ",
        cleaned,
    )
    cleaned = re.sub(
        r"(?:완료했어|완료해줘|완료|끝냈어|끝냈|처리했어|처리했|끝남|done|finish|finished|complete)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:삭제해줘|삭제해|삭제|지워줘|지워|취소|delete|remove)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:미뤄줘|미뤄|미루|연기|다시 알려줘|다시 알려|나중에 알려줘|나중에 알려|"
        r"snooze|postpone|remind later)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:다시 열어줘|다시 열|완료 취소|되돌려|미완료|reopen|undo complete)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:우선순위\s*)?(?:높음|높게|중요|긴급|보통|낮음|낮게|나중|천천히|"
        r"high|urgent|important|normal|low|priority)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" '\"`.,:：")
    return cleaned


def extract_task_ids(text: str) -> list[int]:
    ids = [
        int(match)
        for match in re.findall(r"(?:할\s*일|태스크|task|todo)\s*#?(\d+)(?!\s*(?:일|주|시|분))", text, re.I)
    ]
    if ids:
        return ids
    if (
        asks_to_complete_task(text)
        or asks_to_reopen_task(text)
        or asks_to_postpone_task(text)
        or asks_to_clear_task_due(text)
        or asks_to_rename_task(text)
        or asks_to_set_task_priority(text)
        or asks_to_restore_task(text)
        or asks_to_delete_task(text)
    ):
        return [int(match) for match in re.findall(r"(?<!\d)#?(\d+)(?!\d|\s*(?:일|주|시|분))", text)]
    return []


def extract_task_rename_title(text: str) -> str:
    patterns = [
        r"(?:할\s*일|태스크|task|todo)\s*#?\d+\s*(?:을|를)?\s*(?P<title>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|변경해줘|변경해|rename|change)\.?$",
        r"(?:할\s*일|태스크|task|todo)\s*#?\d+\s*(?:제목|이름)\s*(?:을|를)?\s*(?P<title>.+?)\s*(?:로|으로)?\s*(?:해줘|바꿔줘|변경해줘|수정해줘)?\.?$",
        r"(?:방금|최근|마지막|직전).+?(?:할\s*일|할일|태스크|task|todo).+?(?:을|를)?\s*(?P<title>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|변경해줘|변경해|rename|change)\.?$",
        r"(?:방금|최근|마지막|직전).+?(?:할\s*일|할일|태스크|task|todo).+?(?:제목|이름)\s*(?:을|를)?\s*(?P<title>.+?)\s*(?:로|으로)?\s*(?:해줘|바꿔줘|변경해줘|수정해줘)?\.?$",
        r"(?:rename|change)\s+(?:task|todo)\s*#?\d+\s+(?:to|as)\s+(?P<title>.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.strip(), flags=re.IGNORECASE)
        if match:
            return match.group("title").strip(" '\"`.,")
    return ""


def extract_task_priority(text: str) -> str | None:
    normalized = text.casefold()
    if any(marker in normalized for marker in ["긴급", "중요", "높음", "높게", "high", "urgent", "important"]):
        return "high"
    if any(marker in normalized for marker in ["낮음", "낮게", "나중", "천천히", "low"]):
        return "low"
    if any(marker in normalized for marker in ["보통", "normal", "medium"]):
        return "normal"
    return None


def format_task_priority(priority: str) -> str:
    normalized = normalize_task_priority(priority)
    labels = {
        "high": "높음",
        "normal": "보통",
        "low": "낮음",
    }
    return labels[normalized]


def format_task_detail(item: TaskItem) -> str:
    due_text = item.due_at or "-"
    completed_text = item.completed_at or "-"
    reminder_text = item.reminder_sent_at or "-"
    deleted_text = item.deleted_at or "-"
    channel_text = item.channel_id or "-"
    message_text = item.source_message_id or "-"
    return "\n".join(
        [
            f"할 일 `{item.id}` · {item.title}",
            f"- 상태: {item.status}",
            f"- 우선순위: {format_task_priority(item.priority)}",
            f"- 기한: {due_text}",
            f"- 저장 위치: {item.source_location}",
            f"- 대화 ID: {item.conversation_id}",
            f"- 채널 ID: {channel_text}",
            f"- 원본 메시지 ID: {message_text}",
            f"- 생성: {item.created_at}",
            f"- 완료: {completed_text}",
            f"- 리마인드 발송: {reminder_text}",
            f"- 삭제: {deleted_text}",
        ]
    )


def extract_task_creation(
    text: str,
    *,
    timezone_name: str | None = None,
    now: datetime | None = None,
) -> tuple[str, str | None]:
    due_at = extract_due_at(text, timezone_name=timezone_name, now=now)
    cleaned = text.strip()
    cleaned = re.sub(
        r"^(?:할\s*일|할일|태스크|task|todo|to-do)\s*(?:추가|등록|만들어줘|만들어|add|create)?\s*[:：-]?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:을|를)?\s*(?:할\s*일|할일|태스크|task|todo|to-do)(?:로)?\s*(?:추가|등록|만들어줘|만들어|add|create)\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:리마인드|remind|remind me|알려줘|알려 줘|말해줘|말해 줘|챙겨줘|챙겨 줘|챙겨)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?:하라고|라고)\s*$", "", cleaned)
    cleaned = re.sub(
        r"(?:우선순위\s*)?(?:높음|높게|중요|긴급|보통|낮음|낮게|나중|천천히|high|urgent|important|normal|low)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\d{4}-\d{1,2}-\d{1,2}(?:까지|에|까지는)?", "", cleaned)
    weekday_pattern = (
        r"(?:오늘|내일|모레|이번 주|이번주|다음 주|다음주|"
        r"월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:까지|에|까지는)?"
    )
    cleaned = re.sub(weekday_pattern, "", cleaned)
    cleaned = re.sub(r"\d{1,2}\s*월\s*\d{1,2}\s*일(?:까지|에|까지는)?", "", cleaned)
    cleaned = re.sub(r"\d+\s*(?:일|주)\s*(?:뒤|후)(?:까지|에|까지는)?", "", cleaned)
    cleaned = re.sub(r"\d+\s*(?:분|시간)\s*(?:뒤|후)(?:까지|에|까지는)?", "", cleaned)
    cleaned = remove_due_time_text(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" :：-.,")
    return cleaned, due_at


def extract_reminder_text(
    text: str,
    *,
    timezone_name: str | None = None,
    now: datetime | None = None,
) -> tuple[str, str | None]:
    reminder_text, remind_at = extract_task_creation(text, timezone_name=timezone_name, now=now)
    if not reminder_text:
        reminder_text = "요청하신 알림"
    return reminder_text, remind_at


def normalize_context_task_title(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(
        r"(?:해야겠다|해야겠어|해야 해|해야함|해야 함|해야돼|해야 돼|해야됨|해야 됨|할게|할 것|할거야)\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" '\"`.,:：-")
    return cleaned


def extract_due_at(text: str, *, timezone_name: str | None = None, now: datetime | None = None) -> str | None:
    relative_due_at = extract_relative_due_at(text, timezone_name=timezone_name, now=now)
    if relative_due_at:
        return relative_due_at
    due_date = extract_due_date(text, timezone_name=timezone_name, now=now)
    due_time = extract_due_time(text)
    if due_date and due_time and len(due_date) == 10:
        return f"{due_date} {due_time}"
    return due_date


def extract_relative_due_at(text: str, *, timezone_name: str | None = None, now: datetime | None = None) -> str | None:
    normalized = text.strip()
    current = now.astimezone(resolve_timezone(timezone_name)) if now else now_in_timezone(timezone_name)
    minute_match = re.search(r"(\d+)\s*분\s*(?:뒤|후)", normalized)
    if minute_match:
        minutes = int(minute_match.group(1))
        return (current + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M")
    hour_match = re.search(r"(\d+)\s*시간\s*(?:뒤|후)", normalized)
    if hour_match:
        hours = int(hour_match.group(1))
        return (current + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")
    return None


def extract_due_date(text: str, *, timezone_name: str | None = None, now: datetime | None = None) -> str | None:
    normalized = text.strip()
    now = now.astimezone(resolve_timezone(timezone_name)) if now else now_in_timezone(timezone_name)
    iso_match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", normalized)
    if iso_match:
        year, month, day = (int(part) for part in iso_match.groups())
        return f"{year:04d}-{month:02d}-{day:02d}"

    month_day_match = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", normalized)
    if month_day_match:
        month, day = (int(part) for part in month_day_match.groups())
        year = now.year
        candidate = datetime(year, month, day, tzinfo=now.tzinfo)
        if candidate.date() < now.date():
            year += 1
        return f"{year:04d}-{month:02d}-{day:02d}"

    compact = re.sub(r"\s+", "", normalized)
    relative_days = {
        "오늘": 0,
        "내일": 1,
        "모레": 2,
    }
    for marker, days in relative_days.items():
        if marker in compact:
            return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    relative_day_match = re.search(r"(\d+)\s*일\s*(?:뒤|후)", normalized)
    if relative_day_match:
        days = int(relative_day_match.group(1))
        return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    relative_week_match = re.search(r"(\d+)\s*주\s*(?:뒤|후)", normalized)
    if relative_week_match:
        weeks = int(relative_week_match.group(1))
        return (now + timedelta(days=weeks * 7)).strftime("%Y-%m-%d")

    weekday_offsets = {
        "월요일": 0,
        "화요일": 1,
        "수요일": 2,
        "목요일": 3,
        "금요일": 4,
        "토요일": 5,
        "일요일": 6,
    }
    for marker, weekday in weekday_offsets.items():
        if f"다음주{marker}" in compact:
            days = 7 - now.weekday() + weekday
            return (now + timedelta(days=days)).strftime("%Y-%m-%d")
        if f"이번주{marker}" in compact:
            days = weekday - now.weekday()
            if days < 0:
                days += 7
            return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    if "다음주" in compact:
        return (now + timedelta(days=7)).strftime("%Y-%m-%d")

    for marker, weekday in weekday_offsets.items():
        if marker in compact:
            days = (weekday - now.weekday()) % 7
            if days == 0:
                days = 7
            return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    due_time = extract_due_time(normalized)
    if due_time:
        hour, minute = (int(part) for part in due_time.split(":"))
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate.strftime("%Y-%m-%d")

    return None


def extract_due_time(text: str) -> str | None:
    normalized = text.strip()
    meridiem_match = re.search(
        r"(오전|오후|아침|저녁|밤)\s*(\d{1,2})\s*시(?:\s*(\d{1,2})\s*분?)?",
        normalized,
    )
    if meridiem_match:
        marker, hour_text, minute_text = meridiem_match.groups()
        hour = int(hour_text)
        minute = int(minute_text or "0")
        if marker in {"오후", "저녁", "밤"} and hour < 12:
            hour += 12
        if marker in {"오전", "아침"} and hour == 12:
            hour = 0
        return normalize_hour_minute(hour, minute)

    colon_match = re.search(r"\b(\d{1,2}):(\d{2})\b", normalized)
    if colon_match:
        hour, minute = (int(part) for part in colon_match.groups())
        return normalize_hour_minute(hour, minute)

    hour_match = re.search(r"(?<!\d)(\d{1,2})\s*시(?:\s*(\d{1,2})\s*분?)?", normalized)
    if hour_match:
        hour = int(hour_match.group(1))
        minute = int(hour_match.group(2) or "0")
        return normalize_hour_minute(hour, minute)

    english_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", normalized, re.IGNORECASE)
    if english_match:
        hour = int(english_match.group(1))
        minute = int(english_match.group(2) or "0")
        marker = english_match.group(3).casefold()
        if marker == "pm" and hour < 12:
            hour += 12
        if marker == "am" and hour == 12:
            hour = 0
        return normalize_hour_minute(hour, minute)

    return None


def normalize_hour_minute(hour: int, minute: int) -> str | None:
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour:02d}:{minute:02d}"


def remove_due_time_text(text: str) -> str:
    cleaned = re.sub(
        r"(오전|오후|아침|저녁|밤)\s*\d{1,2}\s*시(?:\s*\d{1,2}\s*분?)?(?:까지|에|까지는)?",
        "",
        text,
    )
    cleaned = re.sub(r"\b\d{1,2}:\d{2}\b(?:까지|에|까지는)?", "", cleaned)
    cleaned = re.sub(r"(?<!\d)\d{1,2}\s*시(?:\s*\d{1,2}\s*분?)?(?:까지|에|까지는)?", "", cleaned)
    cleaned = re.sub(r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b(?:까지|에|까지는)?", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def extract_task_candidates_from_messages(rows: list) -> list[tuple[str, str | None]]:
    candidates: list[tuple[str, str | None]] = []
    seen: set[str] = set()
    for row in rows:
        if row["role"] == "assistant":
            continue
        for sentence in split_task_candidate_sentences(str(row["content"])):
            title = normalize_task_candidate(sentence)
            if not title:
                continue
            key = re.sub(r"\s+", " ", title.casefold()).strip()
            if key in seen:
                continue
            seen.add(key)
            candidates.append((title, extract_due_at(sentence)))
    return candidates


def split_task_candidate_sentences(text: str) -> list[str]:
    pieces = re.split(r"[\n.!?。]+", text)
    return [piece.strip(" -•\t") for piece in pieces if piece.strip(" -•\t")]


def normalize_task_candidate(sentence: str) -> str:
    cleaned = re.sub(r"^@\S+\s*", "", sentence.strip())
    lowered = cleaned.casefold()
    task_markers = [
        "해야",
        "할게",
        "하자",
        "해주세요",
        "해줘",
        "필요",
        "챙겨",
        "작성",
        "검토",
        "공유",
        "확인",
        "todo",
        "follow up",
    ]
    if not any(marker in lowered for marker in task_markers):
        return ""
    cleaned = re.sub(
        r"^(?:내가|제가|우리가|우리|너가|네가|봇이|assistant가)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?:해야\s*해|해야\s*합니다|할게요|할게|하자|해주세요|해줘)\s*$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" :：-.,")
    if len(cleaned) < 4:
        return ""
    return cleaned[:120]


def compact_preview(text: str, *, limit: int = 96) -> str:
    compact = " ".join(text.split())
    if not compact:
        return "(내용 없음)"
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def format_conversation_location(conversation_id: str) -> str:
    if conversation_id.startswith("dm:"):
        return "DM"
    if conversation_id.startswith("thread:"):
        parts = conversation_id.split(":")
        return f"스레드 `{parts[1]}`" if len(parts) > 1 and parts[1] else "스레드"
    if conversation_id.startswith("channel:"):
        parts = conversation_id.split(":")
        return f"채널 `{parts[1]}`" if len(parts) > 1 and parts[1] else "채널"
    if conversation_id.startswith("local:"):
        return "로컬 CLI"
    if conversation_id.startswith("admin:"):
        return "관리 CLI"
    return f"`{conversation_id}`"


def format_detail(
    title: str,
    text: str,
    label: str,
    created_at: str,
    source_location: str,
    max_chars: int = 1400,
) -> str:
    body = text.strip()
    suffix = ""
    if len(body) > max_chars:
        body = body[:max_chars].rstrip()
        suffix = "\n...내용이 길어 앞부분만 보여줬어요. 구체적으로 질문하면 해당 내용 기준으로 답할게요."
    return f"{label}\n- 제목: {title}\n- 저장 위치: {source_location}\n- 저장 시각: {created_at}\n\n{body}{suffix}"


def format_memory_context(results: list) -> str:
    lines = []
    for index, result in enumerate(results, start=1):
        lines.append(
            f"[{index}] 종류: {result.kind}, 제목: {result.title}, 점수: {result.score:.3f}\n{result.text}"
        )
    return "\n\n".join(lines)


def format_conversation_context(rows: list) -> str:
    return "\n".join(f"{row['role']}: {row['content']}" for row in rows)
