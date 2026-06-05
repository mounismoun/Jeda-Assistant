from __future__ import annotations

from assistant_bot.capabilities import capability_prompt_block
from assistant_bot.config import Config
from assistant_bot.models import ConversationScope, RoutingResult
from assistant_bot.openai_service import OpenAIService
from assistant_bot.persona import ASSISTANT_KOREAN_NAME, ASSISTANT_NAME
from assistant_bot.stores import AgentLogStore
from assistant_bot.time_utils import current_time_context

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
        conversation_context: str | None = None,
    ) -> RoutingResult:
        instructions = f"""
너는 Discord 대화형 비서의 라우터다.
사용자 메시지와 최근 대화 맥락을 읽고 아래 intent 중 하나로만 분류한다.
단어 하나에 기계적으로 반응하지 말고, 사용자의 실제 의도를 우선 판단한다.
기능이 있는지, 무엇을 할 수 있는지 묻는 질문은 작업 실행이 아니라 help로 분류한다.
현재 코드로 제공되지 않는 기능을 실제 실행하라는 요청은 unsupported로 분류한다.
OpenAI 모델이 일반적으로 할 수 있어 보이는 일이라도 아래 "현재 코드로 제공되는 기능"에 없으면
가능한 것처럼 분류하지 않는다.

{capability_prompt_block()}

{self.routing_prompt_block}

JSON만 반환한다. 형식: {{"intent":"chat","confidence":0.0,"reason":"짧은 이유"}}
"""
        try:
            output = await self.openai.text_response(
                model=self.config.router_model,
                instructions=instructions,
                input_text=(
                    f"대화 ID: {scope.conversation_id}\n"
                    f"비서 이름: {ASSISTANT_NAME} (한국어 표기: {ASSISTANT_KOREAN_NAME})\n"
                    f"첨부 파일 있음: {has_attachments}\n\n"
                    f"현재 날짜와 시간:\n{current_time_context(self.config.timezone)}\n\n"
                    f"최근 대화 맥락:\n{conversation_context or '(없음)'}\n\n"
                    f"현재 사용자 메시지:\n{text}"
                ),
                temperature=0,
            )
            route = parse_routing_result(output, allowed_intents=self.allowed_intents)
            if route.reason == "라우터 JSON 파싱 실패":
                raise ValueError(route.reason)
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="router",
                intent=route.intent,
                model=self.config.router_model,
                reason=f"모델 라우팅: {route.reason}",
            )
            return route
        except Exception as error:
            heuristic = heuristic_route(text, has_attachments)
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="router",
                intent=heuristic.intent,
                model=self.config.router_model,
                reason=f"모델 라우팅 실패 후 휴리스틱 fallback: {error}; {heuristic.reason}",
            )
            return heuristic
