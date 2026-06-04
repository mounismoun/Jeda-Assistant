from __future__ import annotations

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.stores import AgentLogStore, ReminderStore

from .common import extract_reminder_text


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
        reminder_text, remind_at = extract_reminder_text(text, timezone_name=self.config.timezone)
        if remind_at is None:
            return "언제 알려드릴지 알려주세요. 예: `30분 뒤 물 마시라고 알려줘`"
        reminder_id = self.reminders.add(
            scope=scope,
            text=reminder_text,
            remind_at=remind_at,
            source_message_id=message_id,
        )
        return f"알림 `{reminder_id}`로 등록했어요. `{remind_at}`에 DM으로 알려드릴게요."
