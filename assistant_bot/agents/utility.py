from __future__ import annotations

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.stores import AgentLogStore, ConversationStore, MemoryStore, TaskStore
from assistant_bot.time_utils import today_string

from .common import compact_preview, format_conversation_location, format_task_priority


class UtilityAgent:
    def __init__(
        self,
        *,
        config: Config,
        memories: MemoryStore,
        tasks: TaskStore,
        logs: AgentLogStore,
        conversations: ConversationStore | None = None,
    ) -> None:
        self.config = config
        self.memories = memories
        self.tasks = tasks
        self.logs = logs
        self.conversations = conversations

    def help(self, *, scope: ConversationScope) -> str:
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="help",
            difficulty="easy",
            model=self.config.easy_model,
            reason="도움말 조회",
        )
        return "\n".join(
            [
                "제가 지금 도와드릴 수 있는 일은 이렇습니다.",
                "- `이거 기억해줘: ...`로 메모를 장기 기억에 저장",
                "- `.txt`, `.md`, `.pdf`를 첨부하고 `이 파일 기억해줘`로 문서 저장",
                "- 첨부만 보낸 뒤 제 확인 메시지에 `응, 기억해줘`라고 답장해서 저장",
                "- `전에 저장한 회의 문서 기준으로 정리해줘`처럼 기억 기반 질문",
                "- `지금 뭘 기억하고 있어?`로 기억 목록 확인",
                "- `메모 3 보여줘`, `문서 2 보여줘`로 저장 항목 상세 확인",
                "- `메모 3을 새 내용으로 수정해줘`로 텍스트 메모 수정",
                "- `운동 관련 기억 삭제해줘`, `메모 3 삭제해줘`, `문서 2 삭제해줘`로 삭제",
                "- `방금 저장한 거 지워줘`로 가장 최근 저장 항목 삭제",
                "- `방금 지운 거 복구해줘`로 가장 최근 삭제 항목 복구",
                "- `대화 맥락 초기화해줘`로 현재 대화 기록과 요약 초기화",
                "- `오늘 브리핑 해줘`로 오늘까지 할 일과 최근 기억 확인",
                "- `할 일 추가: 금요일까지 제안서 초안 작성`으로 개인 할 일 저장",
                "- `할 일 목록 보여줘`, `할 일 3 완료했어`로 작업 관리",
                "- `내 기억 전부 삭제해줘`로 사용자 기준 장기 기억 전체 삭제",
                "",
                "같은 사용자의 장기 기억은 DM, 서버, 스레드 어디서든 이어집니다.",
                "저는 멘션, 제 메시지에 대한 답글, DM에서만 반응합니다.",
            ]
        )

    def status(
        self,
        *,
        scope: ConversationScope,
        pending_count: int,
        pending_deletion_count: int,
        location_label: str,
    ) -> str:
        stats = self.memories.stats(scope=scope)
        task_stats = self.tasks.stats(scope=scope)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="status",
            difficulty="easy",
            model=self.config.easy_model,
            reason="상태 조회",
        )
        return "\n".join(
            [
                "현재 상태입니다.",
                f"- 현재 대화 위치: {location_label}",
                f"- 기억: 메모 {stats['memories']}개, 문서 {stats['documents']}개, chunk {stats['chunks']}개",
                f"- 할 일: 열린 작업 {task_stats['open']}개, 완료 {task_stats['completed']}개",
                f"- 저장 확인 대기 첨부: {pending_count}개",
                f"- 삭제 확인 대기 기억: {pending_deletion_count}개",
                f"- 라우터 모델: `{self.config.router_model}`",
                (
                    "- 답변 모델: "
                    f"easy `{self.config.easy_model}`, "
                    f"medium `{self.config.medium_model}`, "
                    f"hard `{self.config.hard_model}`"
                ),
                f"- embedding 모델: `{self.config.embedding_model}`",
            ]
        )

    def daily_briefing(self, *, scope: ConversationScope, location_label: str) -> str:
        today = today_string(self.config.timezone)
        memory_stats = self.memories.stats(scope=scope)
        task_stats = self.tasks.stats(scope=scope)
        due_tasks = self.tasks.list_due(scope=scope, due_before=today, limit=8)
        recent_memories = self.memories.recent_items(scope=scope, limit=5)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="daily_briefing",
            difficulty="easy",
            model=self.config.easy_model,
            reason="일일 브리핑 조회",
        )

        lines = [
            f"오늘 브리핑입니다. 현재 위치: {location_label}",
            f"- 열린 할 일: {task_stats['open']}개 · 완료한 할 일: {task_stats['completed']}개",
        ]
        if due_tasks:
            lines.append("오늘까지 처리할 할 일:")
            for task in due_tasks:
                due_text = "오늘까지" if task.due_at == today else f"{task.due_at}까지"
                lines.append(
                    f"- 할 일 `{task.id}` · {task.title} · 우선순위: {format_task_priority(task.priority)} · {due_text}"
                )
        else:
            lines.append("오늘까지 처리해야 하는 열린 할 일은 없어요.")

        lines.append(
            f"저장 기억: 메모 {memory_stats['memories']}개, 문서 {memory_stats['documents']}개"
            f"({memory_stats['chunks']} chunks)"
        )
        if recent_memories:
            lines.append("최근 기억:")
            for item in recent_memories[:3]:
                label = "메모" if item.kind == "memory" else "문서"
                lines.append(f"- {label} `{item.id}` · {item.title} · 저장 위치: {item.source_location}")
        else:
            lines.append("최근 기억은 아직 없어요.")

        if self.conversations is not None:
            recent_conversations = self.conversations.recent_conversations_for_user(user_id=scope.user_id, limit=3)
            if recent_conversations:
                lines.append("최근 대화 위치:")
                for conversation in recent_conversations:
                    preview = compact_preview(str(conversation["latest_content"]), limit=72)
                    lines.append(
                        f"- {format_conversation_location(str(conversation['conversation_id']))} · "
                        f"사용자 메시지 {conversation['user_message_count']}개 · "
                        f"최근: {conversation['latest_user_message_at']}\n"
                        f"  {preview}"
                    )
            else:
                lines.append("최근 대화 기록은 아직 없어요.")

        lines.append("바로 볼 수 있는 명령: `오늘 할 일 뭐야?`, `최근 대화에서 할 일 뽑아줘`")
        return "\n".join(lines)

    def reset_context(self, *, scope: ConversationScope, conversations: ConversationStore) -> str:
        counts = conversations.clear_conversation(scope.conversation_id)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="reset_context",
            difficulty="easy",
            model=self.config.easy_model,
            reason="현재 대화 맥락 초기화",
        )
        if counts["messages"] == 0 and counts["summaries"] == 0:
            return "초기화할 이전 대화 맥락이 없어요. 장기 기억은 그대로 유지됩니다."
        return (
            "현재 대화 맥락을 초기화했어요. "
            f"이전 메시지 {counts['messages']}개와 요약 {counts['summaries']}개를 지웠고, "
            "장기 기억은 그대로 유지됩니다."
        )


