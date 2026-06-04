from __future__ import annotations

from assistant_bot.agent_toolkits import build_conversation_read_tools
from assistant_bot.capabilities import capability_prompt_block
from assistant_bot.config import Config
from assistant_bot.model_selector import choose_model
from assistant_bot.models import ConversationScope
from assistant_bot.openai_service import OpenAIService
from assistant_bot.stores import AgentLogStore, ConversationStore, MemoryStore, TaskStore

from .common import format_conversation_context


class ConversationAgent:
    def __init__(
        self,
        *,
        config: Config,
        openai: OpenAIService,
        conversations: ConversationStore,
        memories: MemoryStore,
        tasks: TaskStore,
        logs: AgentLogStore,
    ) -> None:
        self.config = config
        self.openai = openai
        self.conversations = conversations
        self.memories = memories
        self.tasks = tasks
        self.logs = logs

    async def chat(
        self,
        *,
        text: str,
        scope: ConversationScope,
        author_name: str,
        location_label: str,
    ) -> str:
        recent = self.conversations.recent_messages(scope.conversation_id)
        summary = self.conversations.latest_summary(scope.conversation_id)
        conversation_context = format_conversation_context(recent)
        context = "\n\n".join(
            part
            for part in [
                f"이전 요약:\n{summary}" if summary else "",
                f"최근 대화:\n{conversation_context}" if conversation_context else "",
            ]
            if part
        )
        choice = choose_model(
            self.config,
            text,
            context_chars=len(context),
            result_count=0,
        )
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="conversation",
            intent="chat",
            difficulty=choice.difficulty,
            model=choice.model,
            reason=choice.reason,
        )

        instructions = f"""
너는 Discord에서 대화하는 개인 비서다.
말투는 자연스럽고 간결하게 유지한다.
사용자가 명시적으로 기억해달라고 하지 않은 정보는 장기 기억으로 저장했다고 말하지 않는다.
저장된 기억을 사용할 때는 자연스럽게 반영하되, 확실하지 않은 내용은 단정하지 않는다.
저장된 기억, 문서, 할 일 정보가 필요하면 제공된 read-only 도구를 사용한다.
도구 결과에 없는 내용은 추측하지 말고 모른다고 말한다.
아래 capability 목록을 기준으로, 현재 코드가 제공하지 않는 작업을 할 수 있다고 말하지 않는다.
사용자가 불가능한 작업을 요청하면 불가능하다고 짧게 말하고 가능한 대안을 안내한다.

{capability_prompt_block()}
"""
        tools = build_conversation_read_tools(
            config=self.config,
            memories=self.memories,
            tasks=self.tasks,
            scope=scope,
        )
        answer = await self.openai.tool_response(
            model=choice.model,
            instructions=instructions,
            input_text=(
                f"사용자 이름: {author_name}\n\n"
                f"현재 대화 위치: {location_label}\n"
                "저장된 기억은 같은 사용자 기준으로 DM과 서버 어디서든 이어진다. "
                "다만 답변할 때는 현재 대화 위치가 바뀌었음을 고려한다.\n\n"
                f"컨텍스트:\n{context}\n\n"
                f"사용자 메시지:\n{text}"
            ),
            tools=tools,
            temperature=0.4,
        )

        recent_chars = self.conversations.recent_char_count(scope.conversation_id)
        if recent_chars >= self.config.context_compression_chars:
            await self.compress_context(scope.conversation_id)

        return answer

    async def compress_context(self, conversation_id: str) -> None:
        recent = self.conversations.recent_messages(conversation_id, limit=80)
        context = format_conversation_context(recent)
        if not context:
            return
        summary = await self.openai.text_response(
            model=self.config.easy_model,
            instructions="대화의 핵심 맥락, 사용자 선호, 미해결 작업만 짧게 한글로 요약한다.",
            input_text=context,
            temperature=0.1,
        )
        self.conversations.add_summary(conversation_id, summary)
