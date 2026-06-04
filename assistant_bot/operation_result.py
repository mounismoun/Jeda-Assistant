from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OperationResult:
    agent: str
    intent: str
    status: str
    summary: str
    facts: dict[str, Any] = field(default_factory=dict)
    items: tuple[dict[str, Any], ...] = ()
    warnings: tuple[str, ...] = ()
    next_actions: tuple[str, ...] = ()
    preserve_values: tuple[str, ...] = ()
    fallback_text: str = ""

    @classmethod
    def legacy(
        cls,
        text: str,
        *,
        agent: str = "legacy",
        intent: str = "legacy",
        status: str = "success",
    ) -> OperationResult:
        return cls(
            agent=agent,
            intent=intent,
            status=status,
            summary=text,
            fallback_text=text,
        )

    def to_prompt_text(self) -> str:
        payload = {
            "agent": self.agent,
            "intent": self.intent,
            "status": self.status,
            "summary": self.summary,
            "facts": self.facts,
            "items": list(self.items),
            "warnings": list(self.warnings),
            "next_actions": list(self.next_actions),
            "preserve_values": list(self.preserve_values),
            "fallback_text": self.fallback_text,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def __str__(self) -> str:
        return self.fallback_text or self.summary

    def __contains__(self, value: str) -> bool:
        return value in str(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return str(self) == other
        return super().__eq__(other)


AgentOutput = OperationResult | str
