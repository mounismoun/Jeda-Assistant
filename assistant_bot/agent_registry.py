from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from assistant_bot.capabilities import unsupported_message
from assistant_bot.models import ConversationScope, ExecutionContext
from assistant_bot.operation_result import AgentOutput, OperationResult

DEFAULT_AGENT_CATALOG_PATH = Path("agent_catalog.json")


@dataclass(frozen=True)
class AgentContext:
    text: str
    scope: ConversationScope
    message_id: str | None
    author_name: str
    location_label: str
    has_attachments: bool = False
    execution: ExecutionContext = field(default_factory=ExecutionContext)


AgentHandler = Callable[[AgentContext], Awaitable[AgentOutput] | AgentOutput]


@dataclass(frozen=True)
class AgentDefinition:
    intent: str
    name: str
    purpose: str
    description: str
    examples: tuple[str, ...]
    tool_names: tuple[str, ...]
    handler: AgentHandler


@dataclass
class AgentRegistry:
    definitions: dict[str, AgentDefinition] = field(default_factory=dict)

    def register(self, definition: AgentDefinition) -> None:
        if definition.intent in self.definitions:
            raise ValueError(f"중복 intent 등록: {definition.intent}")
        self.definitions[definition.intent] = definition

    def get(self, intent: str) -> AgentDefinition | None:
        return self.definitions.get(intent)

    def intents(self) -> list[str]:
        return sorted(self.definitions)

    def routing_prompt_block(self) -> str:
        lines: list[str] = []
        for definition in self.definitions.values():
            examples = ", ".join(f'"{example}"' for example in definition.examples)
            lines.extend(
                [
                    f"- {definition.intent}: {definition.name}",
                    f"  목적: {definition.purpose}",
                    f"  설명: {definition.description}",
                    f"  예시: {examples}",
                ]
            )
            if definition.tool_names:
                lines.append(f"  사용 가능 도구: {', '.join(definition.tool_names)}")
        return "\n".join(lines)

    async def dispatch(self, intent: str, context: AgentContext) -> OperationResult:
        definition = self.get(intent) or self.get("chat")
        if definition is None:
            return OperationResult(
                agent="registry",
                intent=intent,
                status="unsupported",
                summary="처리 가능한 에이전트를 찾지 못함",
                fallback_text="지금은 그 요청을 처리할 수 없어요.",
            )
        result = definition.handler(context)
        if inspect.isawaitable(result):
            result = await result
        if isinstance(result, OperationResult):
            return result
        return OperationResult.legacy(
            str(result),
            agent=definition.name,
            intent=definition.intent,
            status="success",
        )


def load_agent_catalog(path: str | Path = DEFAULT_AGENT_CATALOG_PATH) -> list[dict[str, Any]]:
    catalog_path = Path(path)
    if not catalog_path.exists():
        raise FileNotFoundError(f"에이전트 카탈로그 파일을 찾을 수 없습니다: {catalog_path}")
    with catalog_path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("에이전트 카탈로그는 JSON 배열이어야 합니다.")
    return data


def build_agent_definition(entry: dict[str, Any], handlers: dict[str, AgentHandler]) -> AgentDefinition:
    required_fields = ("intent", "name", "purpose", "description", "examples")
    missing = [field_name for field_name in required_fields if field_name not in entry]
    if missing:
        raise ValueError(f"에이전트 카탈로그 항목에 필수 필드가 없습니다: {', '.join(missing)}")

    intent = entry["intent"]
    examples = entry["examples"]
    tool_names = entry.get("tools", [])
    if not isinstance(intent, str) or not intent:
        raise ValueError("에이전트 intent는 비어 있지 않은 문자열이어야 합니다.")
    if intent not in handlers:
        raise ValueError(f"에이전트 intent에 연결된 handler가 없습니다: {intent}")
    if not isinstance(examples, list) or not all(isinstance(example, str) for example in examples):
        raise ValueError(f"{intent} 에이전트 examples는 문자열 배열이어야 합니다.")
    if not isinstance(tool_names, list) or not all(isinstance(tool_name, str) for tool_name in tool_names):
        raise ValueError(f"{intent} 에이전트 tools는 문자열 배열이어야 합니다.")

    return AgentDefinition(
        intent=intent,
        name=str(entry["name"]),
        purpose=str(entry["purpose"]),
        description=str(entry["description"]),
        examples=tuple(examples),
        tool_names=tuple(tool_names),
        handler=handlers[intent],
    )


def build_agent_registry(
    *,
    memory_agent,
    utility_agent,
    task_agent,
    reminder_agent,
    conversation_agent,
    document_analysis_agent,
    weather_agent,
    web_search_agent,
    pending_attachments,
    pending_memory_captures,
    pending_memory_deletions,
    pending_web_search_confirmations=None,
    pending_confirmation_ttl_minutes: int,
    catalog_path: str | Path = DEFAULT_AGENT_CATALOG_PATH,
) -> AgentRegistry:
    registry = AgentRegistry()

    async def remember(context: AgentContext) -> str:
        return await memory_agent.remember_text(
            text=context.text,
            scope=context.scope,
            message_id=context.message_id or "unknown",
        )

    async def recall(context: AgentContext) -> str:
        return await memory_agent.recall(
            text=context.text,
            scope=context.scope,
            execution_context=context.execution,
        )

    async def list_memory(context: AgentContext) -> str:
        return await memory_agent.list_memories(text=context.text, scope=context.scope)

    async def update_memory(context: AgentContext) -> str:
        return await memory_agent.update(
            text=context.text,
            scope=context.scope,
            execution_context=context.execution,
        )

    async def delete_memory(context: AgentContext) -> str:
        return await memory_agent.delete(
            text=context.text,
            scope=context.scope,
            execution_context=context.execution,
        )

    def restore_memory(context: AgentContext) -> str:
        return memory_agent.restore(text=context.text, scope=context.scope)

    def help_agent(context: AgentContext) -> str:
        return utility_agent.help(scope=context.scope)

    def status(context: AgentContext) -> str:
        return utility_agent.status(
            scope=context.scope,
            pending_count=pending_attachments.unresolved_count(
                scope=context.scope,
                ttl_minutes=pending_confirmation_ttl_minutes,
            )
            + pending_memory_captures.unresolved_count(
                scope=context.scope,
                ttl_minutes=pending_confirmation_ttl_minutes,
            )
            + (
                int(
                    pending_web_search_confirmations.latest(
                        scope=context.scope,
                        ttl_minutes=pending_confirmation_ttl_minutes,
                    )
                    is not None
                )
                if pending_web_search_confirmations is not None
                else 0
            ),
            pending_deletion_count=pending_memory_deletions.unresolved_count(
                scope=context.scope,
                ttl_minutes=pending_confirmation_ttl_minutes,
            ),
            location_label=context.location_label,
        )

    def current_time(context: AgentContext) -> str:
        return utility_agent.current_time(scope=context.scope)

    def daily_briefing(context: AgentContext) -> str:
        return utility_agent.daily_briefing(scope=context.scope, location_label=context.location_label)

    def reset_context(context: AgentContext) -> str:
        return utility_agent.reset_context(scope=context.scope, conversations=conversation_agent.conversations)

    def manage_task(context: AgentContext) -> str:
        return task_agent.handle(
            text=context.text,
            scope=context.scope,
            message_id=context.message_id,
            execution_context=context.execution,
        )

    def manage_reminder(context: AgentContext) -> str:
        return reminder_agent.handle(
            text=context.text,
            scope=context.scope,
            message_id=context.message_id,
            execution_context=context.execution,
        )

    async def chat(context: AgentContext) -> str:
        return await conversation_agent.chat(
            text=context.text,
            scope=context.scope,
            author_name=context.author_name,
            location_label=context.location_label,
            execution_context=context.execution,
        )

    async def analyze_document(context: AgentContext) -> str:
        return await document_analysis_agent.analyze(
            text=context.text,
            scope=context.scope,
            message_id=context.message_id or "unknown",
            attachments=[],
            execution_context=context.execution,
        )

    async def web_search(context: AgentContext) -> str:
        return await web_search_agent.search(
            text=context.text,
            scope=context.scope,
            execution_context=context.execution,
        )

    async def weather(context: AgentContext) -> str:
        return await weather_agent.handle(
            text=context.text,
            scope=context.scope,
            execution_context=context.execution,
        )

    async def web_url(context: AgentContext) -> str:
        return await web_search_agent.read_urls(
            text=context.text,
            scope=context.scope,
            execution_context=context.execution,
        )

    def confirm_web_search(_: AgentContext) -> str:
        return OperationResult(
            agent="registry",
            intent="confirm_web_search",
            status="confirm_required",
            summary="웹검색 확인 필요",
            fallback_text="정확히 답하려면 웹검색이 필요해 보입니다. 검색해볼까요?",
        )

    def cancel_pending(context: AgentContext) -> str:
        if pending_web_search_confirmations is not None:
            pending_search = pending_web_search_confirmations.latest(
                scope=context.scope,
                ttl_minutes=pending_confirmation_ttl_minutes,
            )
            if pending_search is not None:
                pending_web_search_confirmations.resolve(pending_search.id)
                return OperationResult(
                    agent="registry",
                    intent="cancel_pending",
                    status="success",
                    summary="웹검색 확인 대기 작업 취소",
                    fallback_text="웹검색 요청을 취소했어요.",
                )
        pending_deletion = pending_memory_deletions.resolve_latest(
            scope=context.scope,
            ttl_minutes=pending_confirmation_ttl_minutes,
        )
        if pending_deletion is not None:
            return OperationResult(
                agent="registry",
                intent="cancel_pending",
                status="success",
                summary="전체 기억 삭제 대기 작업 취소",
                fallback_text="전체 기억 삭제를 취소했어요.",
            )
        pending_capture = pending_memory_captures.resolve_latest(
            scope=context.scope,
            ttl_minutes=pending_confirmation_ttl_minutes,
        )
        if pending_capture is not None:
            return OperationResult(
                agent="registry",
                intent="cancel_pending",
                status="success",
                summary="메모 대기 작업 취소",
                fallback_text="알겠어요. 이번 메모 대기는 취소할게요.",
            )
        pending = pending_attachments.resolve_latest(
            scope=context.scope,
            ttl_minutes=pending_confirmation_ttl_minutes,
        )
        if pending is None:
            return OperationResult(
                agent="registry",
                intent="cancel_pending",
                status="not_found",
                summary="취소할 대기 작업 없음",
                fallback_text="취소할 대기 작업이 없어요.",
            )
        filenames = ", ".join(pending.filenames)
        return OperationResult(
            agent="registry",
            intent="cancel_pending",
            status="success",
            summary="첨부 저장 대기 작업 취소",
            facts={"filenames": list(pending.filenames)},
            preserve_values=tuple(pending.filenames),
            fallback_text=f"`{filenames}` 첨부 저장을 취소했어요.",
        )

    def unsupported(_: AgentContext) -> str:
        return unsupported_message()

    handlers: dict[str, AgentHandler] = {
        "cancel_pending": cancel_pending,
        "chat": chat,
        "confirm_web_search": confirm_web_search,
        "current_time": current_time,
        "daily_briefing": daily_briefing,
        "analyze_document": analyze_document,
        "delete_memory": delete_memory,
        "help": help_agent,
        "list_memory": list_memory,
        "manage_reminder": manage_reminder,
        "manage_task": manage_task,
        "recall": recall,
        "remember": remember,
        "reset_context": reset_context,
        "restore_memory": restore_memory,
        "status": status,
        "unsupported": unsupported,
        "update_memory": update_memory,
        "weather": weather,
        "web_search": web_search,
        "web_url": web_url,
    }

    for entry in load_agent_catalog(catalog_path):
        registry.register(build_agent_definition(entry, handlers))

    return registry
