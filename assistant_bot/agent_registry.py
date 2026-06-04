from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from assistant_bot.models import ConversationScope

DEFAULT_AGENT_CATALOG_PATH = Path("agent_catalog.json")


@dataclass(frozen=True)
class AgentContext:
    text: str
    scope: ConversationScope
    message_id: str | None
    author_name: str
    location_label: str
    has_attachments: bool = False


AgentHandler = Callable[[AgentContext], Awaitable[str] | str]


@dataclass(frozen=True)
class AgentDefinition:
    intent: str
    name: str
    purpose: str
    description: str
    examples: tuple[str, ...]
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
        return "\n".join(lines)

    async def dispatch(self, intent: str, context: AgentContext) -> str:
        definition = self.get(intent) or self.get("chat")
        if definition is None:
            return "지금은 그 요청을 처리할 수 없어요."
        result = definition.handler(context)
        if inspect.isawaitable(result):
            return await result
        return result


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
    if not isinstance(intent, str) or not intent:
        raise ValueError("에이전트 intent는 비어 있지 않은 문자열이어야 합니다.")
    if intent not in handlers:
        raise ValueError(f"에이전트 intent에 연결된 handler가 없습니다: {intent}")
    if not isinstance(examples, list) or not all(isinstance(example, str) for example in examples):
        raise ValueError(f"{intent} 에이전트 examples는 문자열 배열이어야 합니다.")

    return AgentDefinition(
        intent=intent,
        name=str(entry["name"]),
        purpose=str(entry["purpose"]),
        description=str(entry["description"]),
        examples=tuple(examples),
        handler=handlers[intent],
    )


def build_agent_registry(
    *,
    memory_agent,
    utility_agent,
    task_agent,
    conversation_agent,
    pending_attachments,
    pending_memory_deletions,
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
        return await memory_agent.recall(text=context.text, scope=context.scope)

    async def list_memory(context: AgentContext) -> str:
        return await memory_agent.list_memories(text=context.text, scope=context.scope)

    async def update_memory(context: AgentContext) -> str:
        return await memory_agent.update(text=context.text, scope=context.scope)

    async def delete_memory(context: AgentContext) -> str:
        return await memory_agent.delete(text=context.text, scope=context.scope)

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
            ),
            pending_deletion_count=pending_memory_deletions.unresolved_count(
                scope=context.scope,
                ttl_minutes=pending_confirmation_ttl_minutes,
            ),
            location_label=context.location_label,
        )

    def daily_briefing(context: AgentContext) -> str:
        return utility_agent.daily_briefing(scope=context.scope, location_label=context.location_label)

    def reset_context(context: AgentContext) -> str:
        return utility_agent.reset_context(scope=context.scope, conversations=conversation_agent.conversations)

    def manage_task(context: AgentContext) -> str:
        return task_agent.handle(text=context.text, scope=context.scope, message_id=context.message_id)

    async def chat(context: AgentContext) -> str:
        return await conversation_agent.chat(
            text=context.text,
            scope=context.scope,
            author_name=context.author_name,
            location_label=context.location_label,
        )

    def cancel_pending(context: AgentContext) -> str:
        pending_deletion = pending_memory_deletions.resolve_latest(
            scope=context.scope,
            ttl_minutes=pending_confirmation_ttl_minutes,
        )
        if pending_deletion is not None:
            return "전체 기억 삭제를 취소했어요."
        pending = pending_attachments.resolve_latest(
            scope=context.scope,
            ttl_minutes=pending_confirmation_ttl_minutes,
        )
        if pending is None:
            return "취소할 대기 작업이 없어요."
        return f"`{', '.join(pending.filenames)}` 첨부 저장을 취소했어요."

    def unsupported(_: AgentContext) -> str:
        return "지금은 그 요청을 처리할 수 없어요. 메모/파일 기억, 회상, 삭제부터 도와드릴 수 있습니다."

    handlers: dict[str, AgentHandler] = {
        "cancel_pending": cancel_pending,
        "chat": chat,
        "daily_briefing": daily_briefing,
        "delete_memory": delete_memory,
        "help": help_agent,
        "list_memory": list_memory,
        "manage_task": manage_task,
        "recall": recall,
        "remember": remember,
        "reset_context": reset_context,
        "restore_memory": restore_memory,
        "status": status,
        "unsupported": unsupported,
        "update_memory": update_memory,
    }

    for entry in load_agent_catalog(catalog_path):
        registry.register(build_agent_definition(entry, handlers))

    return registry
