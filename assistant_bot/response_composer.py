from __future__ import annotations

import hashlib
import logging

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.openai_service import OpenAIService
from assistant_bot.operation_result import AgentOutput, OperationResult
from assistant_bot.persona import ASSISTANT_PERSONA
from assistant_bot.time_utils import current_time_context, human_current_time_context

logger = logging.getLogger(__name__)


class ResponseComposer:
    def __init__(self, *, config: Config, openai: OpenAIService) -> None:
        self.config = config
        self.openai = openai

    async def compose(
        self,
        *,
        user_text: str,
        raw_response: AgentOutput,
        scope: ConversationScope,
        location_label: str,
        conversation_context: str | None = None,
    ) -> str:
        operation_result = _coerce_operation_result(raw_response)
        fallback_text = str(operation_result)
        if not fallback_text.strip():
            return fallback_text
        recent_assistant_lines = _recent_assistant_lines(conversation_context or "")
        style_seed = _style_seed(
            user_text=user_text,
            raw_response=operation_result.to_prompt_text(),
            conversation_context=conversation_context or "",
        )
        try:
            answer = await self.openai.text_response(
                model=self.config.easy_model,
                instructions=f"""
{ASSISTANT_PERSONA}

너는 Discord 대화형 비서의 최종 응답 작성자다.
아래 "구조화된 실행 결과"는 이미 코드가 수행한 실제 결과다.
사용자에게 보이는 답변은 이 결과를 바탕으로 자연스럽게 새로 작성한다.

반드시 지킬 것:
- 실행 결과에 없는 사실, 성공, 실패, 저장, 삭제, 발송을 새로 만들지 않는다.
- ID, 숫자, 상태, 파일명, 명령 예시는 바꾸지 않는다.
- 날짜와 시간은 의미를 보존하되 사람이 읽기 편한 한국어 표현으로 바꾼다.
- 예: `2026-06-05 07:04`는 `오늘 오전 7시 4분`, `2026년 6월 5일 오전 7시 4분`처럼 쓴다.
- 사용자가 정확한 원문 시각을 확인해야 하는 맥락이면 자연어 뒤에 원문을 괄호로 함께 적는다.
- 코드 블록이나 백틱 안의 값은 그대로 유지한다.
- 안전 확인, 삭제 확인, 불가능 안내, 지원 범위 제한은 의미를 약하게 만들지 않는다.
- 사용자의 말투와 최근 대화 흐름을 반영하되 장황하게 설명하지 않는다.
- 실행 결과가 목록이면 읽기 쉬운 목록 형태를 유지한다.
- fallback_text나 기존 문장을 그대로 복사하지 않는다. facts/items를 우선 참고하고 표현은 새로 만든다.
- 최근 봇 답변과 같은 첫 문장, 같은 문장 구조, 같은 마무리를 반복하지 않는다.
- 같은 요청이 반복되어도 매번 약간 다른 자연스러운 표현을 사용한다.
- 단, 확인번호, ID, 숫자, 상태명은 절대 변형하지 않는다.
""",
                input_text=(
                    f"현재 날짜와 시간: {human_current_time_context(self.config.timezone)}\n"
                    f"시스템 기준 시각: {current_time_context(self.config.timezone)}\n"
                    f"대화 위치: {location_label}\n"
                    f"대화 ID: {scope.conversation_id}\n\n"
                    f"최근 대화:\n{conversation_context or '(없음)'}\n\n"
                    f"최근 봇 답변 중 반복을 피해야 할 표현:\n{recent_assistant_lines or '(없음)'}\n\n"
                    f"표현 변주 힌트: {style_seed}\n\n"
                    f"사용자 메시지:\n{user_text}\n\n"
                    f"구조화된 실행 결과:\n{operation_result.to_prompt_text()}"
                ),
                temperature=0.8,
            )
            return answer.strip() or fallback_text
        except Exception:
            logger.exception("AI 응답 구성 실패")
            return fallback_text


def _coerce_operation_result(raw_response: AgentOutput) -> OperationResult:
    if isinstance(raw_response, OperationResult):
        return raw_response
    return OperationResult.legacy(str(raw_response))


def _recent_assistant_lines(conversation_context: str) -> str:
    lines = []
    for line in conversation_context.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        if normalized.startswith("assistant:") or normalized.startswith("봇:"):
            lines.append(normalized)
    return "\n".join(lines[-4:])


def _style_seed(*, user_text: str, raw_response: str, conversation_context: str) -> str:
    digest = hashlib.sha256(
        f"{user_text}\n{raw_response}\n{conversation_context}".encode()
    ).hexdigest()
    styles = (
        "짧고 담백하게 답하되 딱딱한 안내문처럼 시작하지 않는다",
        "사용자의 질문에 바로 반응하고 필요한 사실만 이어서 말한다",
        "부드러운 대화체로 말하되 같은 문장 패턴을 피한다",
        "확인한 사실을 먼저 말하고 다음 행동이 필요하면 한 문장으로 덧붙인다",
    )
    return styles[int(digest[:2], 16) % len(styles)]
