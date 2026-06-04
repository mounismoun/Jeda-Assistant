from __future__ import annotations

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.stores import AgentLogStore, ReminderStore

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

    def handle(self, *, text: str, scope: ConversationScope, message_id: str | None = None) -> str:
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
                return (
                    f"가장 최근 등록한 알림은 `{latest.remind_at}` 예정의 `{latest.text}`입니다. "
                    f"상태는 {status}예요."
                )
            return "언제 알려드릴지 알려주세요. 예: `30분 뒤 물 마시라고 알려줘`"
        reminder_id = self.reminders.add(
            scope=scope,
            text=reminder_text,
            remind_at=remind_at,
            source_message_id=message_id,
        )
        return f"알림 `{reminder_id}`로 등록했어요. `{remind_at}`에 DM으로 알려드릴게요."

    def list_reminders(self, *, scope: ConversationScope) -> str:
        items = self.reminders.list_recent(scope=scope, pending_only=True, limit=10)
        if not items:
            return "현재 등록된 미발송 알림은 없어요."
        lines = [f"현재 등록된 미발송 알림 {len(items)}개입니다:"]
        for item in items:
            lines.append(f"- 알림 `{item.id}` · {item.remind_at} · {item.text}")
        return "\n".join(lines)

    def show_latest_reminder(self, *, scope: ConversationScope) -> str:
        item = self.reminders.latest(scope=scope)
        if item is None:
            return "최근 등록한 알림이 없어요."
        status = "발송 완료" if item.sent_at else "발송 대기"
        return f"가장 최근 등록한 알림은 `{item.remind_at}` 예정의 `{item.text}`입니다. 상태는 {status}예요."
