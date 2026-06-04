from __future__ import annotations

import logging

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.openai_service import OpenAIService
from assistant_bot.time_utils import current_time_context

logger = logging.getLogger(__name__)


class ResponseComposer:
    def __init__(self, *, config: Config, openai: OpenAIService) -> None:
        self.config = config
        self.openai = openai

    async def compose(
        self,
        *,
        user_text: str,
        raw_response: str,
        scope: ConversationScope,
        location_label: str,
        conversation_context: str | None = None,
    ) -> str:
        if not raw_response.strip():
            return raw_response
        try:
            answer = await self.openai.text_response(
                model=self.config.easy_model,
                instructions="""
너는 Discord 대화형 비서의 최종 응답 작성자다.
아래 "실행 결과"는 이미 코드가 수행한 실제 결과다.
사용자에게 보이는 답변은 자연스럽고 대화체인 한국어로 다시 작성한다.

반드시 지킬 것:
- 실행 결과에 없는 사실, 성공, 실패, 저장, 삭제, 발송을 새로 만들지 않는다.
- ID, 날짜, 시간, 숫자, 상태, 파일명, 명령 예시는 바꾸지 않는다.
- 코드 블록이나 백틱 안의 값은 그대로 유지한다.
- 안전 확인, 삭제 확인, 불가능 안내, 지원 범위 제한은 의미를 약하게 만들지 않는다.
- 사용자의 말투와 최근 대화 흐름을 반영하되 장황하게 설명하지 않는다.
- 실행 결과가 목록이면 읽기 쉬운 목록 형태를 유지한다.
""",
                input_text=(
                    f"현재 날짜와 시간: {current_time_context(self.config.timezone)}\n"
                    f"대화 위치: {location_label}\n"
                    f"대화 ID: {scope.conversation_id}\n\n"
                    f"최근 대화:\n{conversation_context or '(없음)'}\n\n"
                    f"사용자 메시지:\n{user_text}\n\n"
                    f"실행 결과:\n{raw_response}"
                ),
                temperature=0.5,
            )
            return answer.strip() or raw_response
        except Exception:
            logger.exception("AI 응답 구성 실패")
            return raw_response
