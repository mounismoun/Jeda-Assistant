from __future__ import annotations

from typing import Any

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope, MemoryDetail, TaskItem
from assistant_bot.stores import MemoryStore, TaskStore
from assistant_bot.time_utils import today_string
from assistant_bot.tool_calling import ToolSpec


def build_conversation_read_tools(
    *,
    config: Config,
    memories: MemoryStore,
    tasks: TaskStore,
    scope: ConversationScope,
) -> list[ToolSpec]:
    return [
        *build_memory_read_tools(config=config, memories=memories, scope=scope),
        *build_task_read_tools(config=config, tasks=tasks, scope=scope),
    ]


def build_memory_read_tools(
    *,
    config: Config,
    memories: MemoryStore,
    scope: ConversationScope,
) -> list[ToolSpec]:
    async def search_memories(arguments: dict[str, Any]) -> dict[str, Any]:
        query = str(arguments.get("query", "")).strip()
        limit = _safe_limit(arguments.get("limit"), default=min(5, config.retrieval_limit), maximum=8)
        if not query:
            return {"ok": False, "error": "query가 비어 있습니다.", "results": []}
        results = await memories.search(scope=scope, query=query, limit=limit)
        useful_results = [result for result in results if result.score >= 0.18]
        return {
            "ok": True,
            "query": query,
            "results": [
                {
                    "kind": result.kind,
                    "id": result.id,
                    "title": result.title,
                    "preview": _compact_preview(result.text, limit=180),
                    "score": round(result.score, 3),
                    "source_location": result.source_location,
                    "created_at": result.created_at,
                }
                for result in useful_results
            ],
        }

    def list_recent_memories(arguments: dict[str, Any]) -> dict[str, Any]:
        limit = _safe_limit(arguments.get("limit"), default=5, maximum=10)
        items = memories.recent_items(scope=scope, limit=limit)
        return {
            "ok": True,
            "results": [
                {
                    "kind": item.kind,
                    "id": item.id,
                    "title": item.title,
                    "detail": item.detail,
                    "source_location": item.source_location,
                    "created_at": item.created_at,
                }
                for item in items
            ],
        }

    def get_memory_detail(arguments: dict[str, Any]) -> dict[str, Any]:
        memory_id = _safe_limit(arguments.get("memory_id"), default=0, maximum=1_000_000)
        detail = memories.get_memory_detail(scope=scope, memory_id=memory_id)
        if detail is None:
            return {"ok": False, "error": f"메모 {memory_id}를 찾지 못했습니다."}
        return {"ok": True, "result": _memory_detail_payload(detail)}

    def get_document_detail(arguments: dict[str, Any]) -> dict[str, Any]:
        document_id = _safe_limit(arguments.get("document_id"), default=0, maximum=1_000_000)
        detail = memories.get_document_detail(scope=scope, document_id=document_id)
        if detail is None:
            return {"ok": False, "error": f"문서 {document_id}를 찾지 못했습니다."}
        return {"ok": True, "result": _memory_detail_payload(detail)}

    return [
        ToolSpec(
            name="search_memories",
            description=(
                "사용자의 저장된 메모와 문서 chunk를 의미 검색한다. "
                "저장된 기억이나 문서 근거가 필요할 때 사용한다."
            ),
            parameters=_object_schema(
                {
                    "query": {"type": "string", "description": "검색할 자연어 질의"},
                    "limit": {"type": "integer", "description": "가져올 최대 결과 수. 1~8 권장"},
                },
                required=["query", "limit"],
            ),
            handler=search_memories,
            read_only=True,
        ),
        ToolSpec(
            name="list_recent_memories",
            description="사용자가 최근 저장한 기억과 문서 목록을 조회한다.",
            parameters=_object_schema(
                {"limit": {"type": "integer", "description": "가져올 최대 결과 수. 1~10 권장"}},
                required=["limit"],
            ),
            handler=list_recent_memories,
            read_only=True,
        ),
        ToolSpec(
            name="get_memory_detail",
            description="특정 텍스트 메모 ID의 상세 내용을 조회한다.",
            parameters=_object_schema(
                {"memory_id": {"type": "integer", "description": "조회할 메모 ID"}},
                required=["memory_id"],
            ),
            handler=get_memory_detail,
            read_only=True,
        ),
        ToolSpec(
            name="get_document_detail",
            description="특정 문서 ID의 추출 텍스트 상세 내용을 조회한다.",
            parameters=_object_schema(
                {"document_id": {"type": "integer", "description": "조회할 문서 ID"}},
                required=["document_id"],
            ),
            handler=get_document_detail,
            read_only=True,
        ),
    ]


def build_task_read_tools(
    *,
    config: Config,
    tasks: TaskStore,
    scope: ConversationScope,
) -> list[ToolSpec]:
    def search_tasks(arguments: dict[str, Any]) -> dict[str, Any]:
        query = str(arguments.get("query", "")).strip()
        limit = _safe_limit(arguments.get("limit"), default=8, maximum=10)
        if not query:
            return {"ok": False, "error": "query가 비어 있습니다.", "results": []}
        return {
            "ok": True,
            "query": query,
            "results": [_task_payload(item) for item in tasks.search(scope=scope, keyword=query, limit=limit)],
        }

    def list_tasks(arguments: dict[str, Any]) -> dict[str, Any]:
        status = str(arguments.get("status", "open")).strip()
        if status not in {"open", "completed", "all"}:
            status = "open"
        limit = _safe_limit(arguments.get("limit"), default=8, maximum=10)
        items = tasks.list_recent(user_id=scope.user_id, status=status, limit=limit)
        return {
            "ok": True,
            "status": status,
            "stats": tasks.stats(scope=scope),
            "results": [_task_payload(item) for item in items],
        }

    def list_due_tasks(arguments: dict[str, Any]) -> dict[str, Any]:
        due_before = str(arguments.get("due_before") or today_string(config.timezone)).strip()
        limit = _safe_limit(arguments.get("limit"), default=8, maximum=10)
        return {
            "ok": True,
            "due_before": due_before,
            "results": [
                _task_payload(item)
                for item in tasks.list_due(scope=scope, due_before=due_before, limit=limit)
            ],
        }

    return [
        ToolSpec(
            name="search_tasks",
            description="사용자의 할 일을 키워드로 검색한다. 특정 작업이나 제목을 찾을 때 사용한다.",
            parameters=_object_schema(
                {
                    "query": {"type": "string", "description": "검색할 할 일 키워드"},
                    "limit": {"type": "integer", "description": "가져올 최대 결과 수. 1~10 권장"},
                },
                required=["query", "limit"],
            ),
            handler=search_tasks,
            read_only=True,
        ),
        ToolSpec(
            name="list_tasks",
            description="사용자의 할 일 목록을 상태별로 조회한다.",
            parameters=_object_schema(
                {
                    "status": {
                        "type": "string",
                        "enum": ["open", "completed", "all"],
                        "description": "조회할 할 일 상태",
                    },
                    "limit": {"type": "integer", "description": "가져올 최대 결과 수. 1~10 권장"},
                },
                required=["status", "limit"],
            ),
            handler=list_tasks,
            read_only=True,
        ),
        ToolSpec(
            name="list_due_tasks",
            description="특정 날짜까지 기한이 도래한 열린 할 일을 조회한다.",
            parameters=_object_schema(
                {
                    "due_before": {
                        "type": "string",
                        "description": "YYYY-MM-DD 또는 날짜/시간 문자열. 비우지 말고 기준 날짜를 넣는다.",
                    },
                    "limit": {"type": "integer", "description": "가져올 최대 결과 수. 1~10 권장"},
                },
                required=["due_before", "limit"],
            ),
            handler=list_due_tasks,
            read_only=True,
        ),
    ]


def _object_schema(properties: dict[str, Any], *, required: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def _safe_limit(value: object, *, default: int, maximum: int) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(limit, maximum))


def _task_payload(item: TaskItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "title": item.title,
        "status": item.status,
        "priority": item.priority,
        "priority_label": _format_task_priority(item.priority),
        "due_at": item.due_at,
        "created_at": item.created_at,
        "completed_at": item.completed_at,
        "source_location": item.source_location,
    }


def _memory_detail_payload(detail: MemoryDetail) -> dict[str, Any]:
    return {
        "kind": detail.kind,
        "id": detail.id,
        "title": detail.title,
        "text": _compact_preview(detail.text, limit=2400),
        "created_at": detail.created_at,
        "source_location": detail.source_location,
    }


def _compact_preview(text: str, *, limit: int = 96) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 1)].rstrip() + "…"


def _format_task_priority(priority: str) -> str:
    labels = {"high": "높음", "normal": "보통", "low": "낮음"}
    return labels.get(priority, priority)
