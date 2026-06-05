from __future__ import annotations

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope, ExecutionContext
from assistant_bot.operation_result import OperationResult
from assistant_bot.stores import AgentLogStore, ReminderStore
from assistant_bot.time_utils import humanize_datetime_text

from .common import asks_to_list_reminders, asks_to_show_recent_reminder, extract_reminder_text


class ReminderAgent:
    def __init__(
        self,
        *,
        config: Config,
        reminders: ReminderStore,
        logs: AgentLogStore,
    ) -> None:
        self.config = config
        self.reminders = reminders
        self.logs = logs

    def handle(
        self,
        *,
        text: str,
        scope: ConversationScope,
        message_id: str | None = None,
        execution_context: ExecutionContext | None = None,
    ) -> OperationResult:
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="reminder",
            intent="manage_reminder",
            difficulty="easy",
            model=self.config.easy_model,
            reason="사용자 알림 예약 요청",
        )
        if asks_to_list_reminders(text):
            return self.list_reminders(scope=scope)
        if asks_to_show_recent_reminder(text):
            return self.show_latest_reminder(scope=scope)

        reminder_text, remind_at = extract_reminder_text(text, timezone_name=self.config.timezone)
        if remind_at is None:
            latest = self.reminders.latest(scope=scope)
            if latest is not None:
                status = "발송 완료" if latest.sent_at else "발송 대기"
                fallback = (
                    f"가장 최근 등록한 알림은 `{latest.remind_at}` 예정의 `{latest.text}`입니다. "
                    f"상태는 {status}예요."
                )
                return OperationResult(
                    agent="reminder",
                    intent="manage_reminder",
                    status="success",
                    summary="최근 등록한 알림 조회",
                    facts={
                        "reminder_id": latest.id,
                        "text": latest.text,
                        "remind_at": latest.remind_at,
                        "human_remind_at": humanize_datetime_text(latest.remind_at, self.config.timezone),
                        "delivery": "DM",
                        "state": status,
                    },
                    preserve_values=(str(latest.id), latest.remind_at, latest.text, status),
                    fallback_text=fallback,
                )
            return OperationResult(
                agent="reminder",
                intent="manage_reminder",
                status="needs_input",
                summary="알림을 등록하려면 시간이 필요함",
                next_actions=("언제 알려줄지 물어본다",),
                fallback_text="언제 알려드릴지 알려주세요. 예: `30분 뒤 물 마시라고 알려줘`",
            )
        reminder_id = self.reminders.add(
            scope=scope,
            text=reminder_text,
            remind_at=remind_at,
            source_message_id=message_id,
        )
        fallback = f"알림 `{reminder_id}`로 등록했어요. `{remind_at}`에 DM으로 알려드릴게요."
        return OperationResult(
            agent="reminder",
            intent="manage_reminder",
            status="success",
            summary="사용자 알림 등록 완료",
            facts={
                "reminder_id": reminder_id,
                "text": reminder_text,
                "remind_at": remind_at,
                "human_remind_at": humanize_datetime_text(remind_at, self.config.timezone),
                "delivery": "DM",
            },
            preserve_values=(str(reminder_id), remind_at, reminder_text, "DM"),
            fallback_text=f"알림 `{reminder_id}`로 등록했어요. `{remind_at}`에 DM으로 알려드릴게요.",
        )

    def list_reminders(self, *, scope: ConversationScope) -> OperationResult:
        items = self.reminders.list_recent(scope=scope, pending_only=True, limit=10)
        if not items:
            return OperationResult(
                agent="reminder",
                intent="manage_reminder",
                status="success",
                summary="등록된 미발송 알림 없음",
                items=(),
                fallback_text="현재 등록된 미발송 알림은 없어요.",
            )
        lines = [f"현재 등록된 미발송 알림 {len(items)}개입니다:"]
        for item in items:
            lines.append(f"- 알림 `{item.id}` · {item.remind_at} · {item.text}")
        return OperationResult(
            agent="reminder",
            intent="manage_reminder",
            status="success",
            summary="미발송 알림 목록 조회",
            facts={"count": len(items), "delivery": "DM"},
            items=tuple(
                {
                    "reminder_id": item.id,
                    "text": item.text,
                    "remind_at": item.remind_at,
                    "human_remind_at": humanize_datetime_text(item.remind_at, self.config.timezone),
                    "state": "발송 대기",
                }
                for item in items
            ),
            preserve_values=tuple(str(item.id) for item in items) + tuple(item.remind_at for item in items),
            fallback_text="\n".join(lines),
        )

    def show_latest_reminder(self, *, scope: ConversationScope) -> OperationResult:
        item = self.reminders.latest(scope=scope)
        if item is None:
            return OperationResult(
                agent="reminder",
                intent="manage_reminder",
                status="not_found",
                summary="최근 등록한 알림 없음",
                fallback_text="최근 등록한 알림이 없어요.",
            )
        status = "발송 완료" if item.sent_at else "발송 대기"
        fallback = (
            f"가장 최근 등록한 알림은 `{item.remind_at}` 예정의 `{item.text}`입니다. "
            f"상태는 {status}예요."
        )
        return OperationResult(
            agent="reminder",
            intent="manage_reminder",
            status="success",
            summary="최근 등록한 알림 조회",
            facts={
                "reminder_id": item.id,
                "text": item.text,
                "remind_at": item.remind_at,
                "human_remind_at": humanize_datetime_text(item.remind_at, self.config.timezone),
                "delivery": "DM",
                "state": status,
            },
            preserve_values=(str(item.id), item.remind_at, item.text, status),
            fallback_text=fallback,
        )
