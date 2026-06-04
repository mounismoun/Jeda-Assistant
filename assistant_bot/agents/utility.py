from __future__ import annotations

from assistant_bot.capabilities import help_lines
from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.operation_result import OperationResult
from assistant_bot.stores import AgentLogStore, ConversationStore, MemoryStore, TaskStore
from assistant_bot.time_utils import human_current_time_context, today_string

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

    def help(self, *, scope: ConversationScope) -> OperationResult:
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="help",
            difficulty="easy",
            model=self.config.easy_model,
            reason="도움말 조회",
        )
        lines = help_lines()
        return OperationResult(
            agent="utility",
            intent="help",
            status="success",
            summary="현재 지원 기능 안내",
            facts={"supported_help_lines": lines},
            fallback_text="\n".join(lines),
        )

    def status(
        self,
        *,
        scope: ConversationScope,
        pending_count: int,
        pending_deletion_count: int,
        location_label: str,
    ) -> OperationResult:
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
        lines = [
                "현재 상태입니다.",
                f"- 현재 대화 위치: {location_label}",
                f"- 현재 날짜와 시간: {human_current_time_context(self.config.timezone)}",
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
        return OperationResult(
            agent="utility",
            intent="status",
            status="success",
            summary="봇 상태 조회",
            facts={
                "location": location_label,
                "current_time": human_current_time_context(self.config.timezone),
                "memory_count": stats["memories"],
                "document_count": stats["documents"],
                "chunk_count": stats["chunks"],
                "open_task_count": task_stats["open"],
                "completed_task_count": task_stats["completed"],
                "pending_attachment_count": pending_count,
                "pending_memory_deletion_count": pending_deletion_count,
                "router_model": self.config.router_model,
                "easy_model": self.config.easy_model,
                "medium_model": self.config.medium_model,
                "hard_model": self.config.hard_model,
                "embedding_model": self.config.embedding_model,
            },
            preserve_values=(
                self.config.router_model,
                self.config.easy_model,
                self.config.medium_model,
                self.config.hard_model,
                self.config.embedding_model,
            ),
            fallback_text="\n".join(lines),
        )

    def current_time(self, *, scope: ConversationScope) -> OperationResult:
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="current_time",
            difficulty="easy",
            model=self.config.easy_model,
            reason="현재 날짜/시간 조회",
        )
        current_time = human_current_time_context(self.config.timezone)
        return OperationResult(
            agent="utility",
            intent="current_time",
            status="success",
            summary="현재 날짜와 시간 조회",
            facts={"current_time": current_time, "timezone": self.config.timezone},
            preserve_values=(self.config.timezone,),
            fallback_text=f"지금은 {current_time}입니다.",
        )

    def daily_briefing(self, *, scope: ConversationScope, location_label: str) -> OperationResult:
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
        return OperationResult(
            agent="utility",
            intent="daily_briefing",
            status="success",
            summary="오늘 브리핑 조회",
            facts={
                "location": location_label,
                "open_task_count": task_stats["open"],
                "completed_task_count": task_stats["completed"],
                "memory_count": memory_stats["memories"],
                "document_count": memory_stats["documents"],
                "chunk_count": memory_stats["chunks"],
            },
            items=tuple({"kind": "line", "text": line} for line in lines),
            fallback_text="\n".join(lines),
        )

    def reset_context(self, *, scope: ConversationScope, conversations: ConversationStore) -> OperationResult:
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
            return OperationResult(
                agent="utility",
                intent="reset_context",
                status="not_found",
                summary="초기화할 이전 대화 맥락 없음",
                facts={"long_term_memory_kept": True},
                fallback_text="초기화할 이전 대화 맥락이 없어요. 장기 기억은 그대로 유지됩니다.",
            )
        fallback = (
            "현재 대화 맥락을 초기화했어요. "
            f"이전 메시지 {counts['messages']}개와 요약 {counts['summaries']}개를 지웠고, "
            "장기 기억은 그대로 유지됩니다."
        )
        return OperationResult(
            agent="utility",
            intent="reset_context",
            status="success",
            summary="현재 대화 맥락 초기화 완료",
            facts={
                "deleted_message_count": counts["messages"],
                "deleted_summary_count": counts["summaries"],
                "long_term_memory_kept": True,
            },
            fallback_text=fallback,
        )
