from __future__ import annotations

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope, RoutingResult
from assistant_bot.openai_service import OpenAIService
from assistant_bot.stores import AgentLogStore

from .common import DEFAULT_ALLOWED_INTENTS, DEFAULT_ROUTING_PROMPT_BLOCK, heuristic_route, parse_routing_result


class RouterAgent:
    def __init__(
        self,
        config: Config,
        openai: OpenAIService,
        logs: AgentLogStore,
        *,
        routing_prompt_block: str | None = None,
        allowed_intents: set[str] | None = None,
    ) -> None:
        self.config = config
        self.openai = openai
        self.logs = logs
        self.routing_prompt_block = routing_prompt_block or DEFAULT_ROUTING_PROMPT_BLOCK
        self.allowed_intents = allowed_intents or DEFAULT_ALLOWED_INTENTS

    async def route(
        self,
        *,
        text: str,
        has_attachments: bool,
        scope: ConversationScope,
    ) -> RoutingResult:
        heuristic = heuristic_route(text, has_attachments)
        if heuristic.confidence >= 0.92:
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="router",
                intent=heuristic.intent,
                model=self.config.router_model,
                reason=f"휴리스틱 라우팅: {heuristic.reason}",
            )
            return heuristic

        instructions = f"""
너는 Discord 대화형 비서의 라우터다.
사용자 메시지를 아래 intent 중 하나로만 분류한다.

{self.routing_prompt_block}

JSON만 반환한다. 형식: {{"intent":"chat","confidence":0.0,"reason":"짧은 이유"}}
"""
        output = await self.openai.text_response(
            model=self.config.router_model,
            instructions=instructions,
            input_text=f"첨부 파일 있음: {has_attachments}\n메시지: {text}",
            temperature=0,
        )
        route = parse_routing_result(output, allowed_intents=self.allowed_intents)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="router",
            intent=route.intent,
            model=self.config.router_model,
            reason=route.reason,
        )
        return route


