from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace

import discord

from assistant_bot.agent_registry import AgentContext, build_agent_registry
from assistant_bot.agents import (
    ConversationAgent,
    MemoryAgent,
    ReminderAgent,
    RouterAgent,
    TaskAgent,
    UtilityAgent,
    asks_to_delete_all_memories,
    format_conversation_context,
    format_task_priority,
)
from assistant_bot.config import Config
from assistant_bot.database import AppDatabase
from assistant_bot.file_extractor import extract_attachment_text, is_supported_attachment
from assistant_bot.models import ConversationScope
from assistant_bot.openai_service import OpenAIService
from assistant_bot.operation_result import AgentOutput, OperationResult
from assistant_bot.persona import ASSISTANT_PERSONA
from assistant_bot.response_composer import ResponseComposer
from assistant_bot.stores import (
    AgentLogStore,
    ConversationStore,
    MemoryStore,
    PendingAttachmentStore,
    PendingMemoryCaptureStore,
    PendingMemoryDeletionStore,
    ReminderStore,
    TaskStore,
)
from assistant_bot.text_utils import split_discord_message, strip_bot_mentions
from assistant_bot.time_utils import humanize_datetime_text, now_in_timezone, today_string

logger = logging.getLogger(__name__)
BOT_STATUS_MESSAGE = "범용 AI 비서입니다."


class AssistantBot(discord.Client):
    def __init__(self, config: Config) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.dm_messages = True
        intents.guild_messages = True

        super().__init__(intents=intents)

        self.config = config
        self.database = AppDatabase(config.database_path)
        self.openai = OpenAIService(config)
        self.response_composer = ResponseComposer(config=config, openai=self.openai)
        self.logs = AgentLogStore(self.database.connection)
        self.conversations = ConversationStore(self.database.connection)
        self.pending_attachments = PendingAttachmentStore(self.database.connection)
        self.pending_memory_captures = PendingMemoryCaptureStore(self.database.connection)
        self.pending_memory_deletions = PendingMemoryDeletionStore(self.database.connection)
        self.tasks = TaskStore(self.database.connection)
        self.reminders = ReminderStore(self.database.connection)
        self.memories = MemoryStore(self.database.connection, self.openai)
        self.memory_agent = MemoryAgent(
            config=config,
            openai=self.openai,
            memories=self.memories,
            logs=self.logs,
            conversations=self.conversations,
        )
        self.utility_agent = UtilityAgent(
            config=config,
            memories=self.memories,
            tasks=self.tasks,
            logs=self.logs,
            conversations=self.conversations,
        )
        self.task_agent = TaskAgent(
            config=config,
            tasks=self.tasks,
            conversations=self.conversations,
            logs=self.logs,
        )
        self.reminder_agent = ReminderAgent(
            config=config,
            reminders=self.reminders,
            logs=self.logs,
        )
        self.conversation_agent = ConversationAgent(
            config=config,
            openai=self.openai,
            conversations=self.conversations,
            memories=self.memories,
            tasks=self.tasks,
            logs=self.logs,
        )
        self.agent_registry = build_agent_registry(
            memory_agent=self.memory_agent,
            utility_agent=self.utility_agent,
            task_agent=self.task_agent,
            reminder_agent=self.reminder_agent,
            conversation_agent=self.conversation_agent,
            pending_attachments=self.pending_attachments,
            pending_memory_captures=self.pending_memory_captures,
            pending_memory_deletions=self.pending_memory_deletions,
            pending_confirmation_ttl_minutes=self.config.pending_confirmation_ttl_minutes,
        )
        self.router = RouterAgent(
            config,
            self.openai,
            self.logs,
            routing_prompt_block=self.agent_registry.routing_prompt_block(),
            allowed_intents=set(self.agent_registry.intents()),
        )
        self._task_reminder_started = False

    async def on_ready(self) -> None:
        logger.info("Discord bot logged in as %s (%s)", self.user, self.user.id if self.user else "?")
        await self.change_presence(activity=discord.CustomActivity(name=BOT_STATUS_MESSAGE))
        if not self._task_reminder_started:
            self._task_reminder_started = True
            self.loop.create_task(self.task_reminder_loop())

    async def task_reminder_loop(self) -> None:
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                await self.send_due_reminders()
            except Exception:
                logger.exception("알림 처리 중 오류")
            await asyncio.sleep(min(max(1, self.config.task_reminder_interval_minutes) * 60, 15))

    async def send_due_reminders(self) -> int:
        now_text = now_in_timezone(self.config.timezone).strftime("%Y-%m-%d %H:%M")
        due_reminders = self.reminders.due_for_delivery(
            as_of=now_text,
            limit=self.config.task_reminder_batch_size,
        )
        sent_count = 0
        for reminder in due_reminders:
            destination = await self.resolve_task_destination(None, reminder.user_id)
            if destination is None:
                logger.warning("알림 %s 대상 사용자를 찾지 못했습니다", reminder.id)
                continue
            message = (
                "알림입니다.\n"
                f"- 알림 `{reminder.id}` · {reminder.text}\n"
                f"- 예약 시각: {humanize_datetime_text(reminder.remind_at, self.config.timezone)}"
            )
            await destination.send(message)
            self.reminders.mark_sent(reminder.id)
            sent_count += 1
        return sent_count

    async def send_due_task_reminders(self) -> int:
        return await self.send_due_reminders()

    async def send_due_task_deadline_reminders(self) -> int:
        today = today_string(self.config.timezone)
        now_text = now_in_timezone(self.config.timezone).strftime("%Y-%m-%d %H:%M")
        due_tasks = self.tasks.due_for_reminder(
            today=now_text,
            limit=self.config.task_reminder_batch_size,
        )
        sent_count = 0
        for task in due_tasks:
            destination = await self.resolve_task_destination(None, task.user_id)
            if destination is None:
                logger.warning("할 일 %s 리마인더 대상 사용자를 찾지 못했습니다", task.id)
                continue
            due_text = "오늘까지" if task.due_at == today else f"{task.due_at}까지"
            message = (
                "할 일 리마인더입니다.\n"
                f"- 할 일 `{task.id}` · {task.title}\n"
                f"- 우선순위: {format_task_priority(task.priority)}\n"
                f"- 기한: {due_text}\n"
                "완료했다면 `할 일 {id} 완료했어`라고 답장해 주세요.".format(id=task.id)
            )
            await destination.send(message)
            self.tasks.mark_reminded(task.id)
            sent_count += 1
        return sent_count

    async def resolve_task_destination(
        self,
        channel_id: str | None,
        user_id: str,
    ) -> discord.abc.Messageable | None:
        if channel_id:
            channel = self.get_channel(int(channel_id))
            if channel is None:
                try:
                    channel = await self.fetch_channel(int(channel_id))
                except (discord.NotFound, discord.Forbidden, discord.HTTPException, ValueError):
                    channel = None
            if isinstance(channel, discord.abc.Messageable):
                return channel

        try:
            user = self.get_user(int(user_id)) or await self.fetch_user(int(user_id))
        except (discord.NotFound, discord.Forbidden, discord.HTTPException, ValueError):
            return None
        return user

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if not self.user:
            return
        if not await self.should_respond(message):
            return

        scope = self.scope_for(message)
        clean_text = strip_bot_mentions(message.content, self.user.id)
        author_name = message.author.display_name
        attachments = list(message.attachments)
        conversation_context = format_conversation_context(
            self.conversations.recent_messages(scope.conversation_id, limit=16)
        )

        async with message.channel.typing():
            try:
                raw_answer = await self.handle_message(
                    message=message,
                    text=clean_text,
                    attachments=attachments,
                    scope=scope,
                    author_name=author_name,
                    conversation_context=conversation_context,
                )
                answer = await self.response_composer.compose(
                    user_text=clean_text,
                    raw_response=raw_answer,
                    scope=scope,
                    location_label=describe_message_location(message),
                    conversation_context=conversation_context,
                )
            except Exception:
                logger.exception("메시지 처리 중 오류")
                answer = "처리 중 문제가 생겼어요. 로그를 확인한 뒤 다시 시도해 주세요."

        self.conversations.add_message(
            conversation_id=scope.conversation_id,
            role="user",
            user_id=str(message.author.id),
            content=clean_text or describe_attachments(attachments),
        )
        self.conversations.add_message(
            conversation_id=scope.conversation_id,
            role="assistant",
            user_id=str(self.user.id),
            content=answer,
        )

        confirmation_view = self.confirmation_view_for(raw_answer, scope)
        first_part = True
        for part in split_discord_message(answer):
            await message.reply(
                part,
                mention_author=False,
                view=confirmation_view if first_part else None,
            )
            first_part = False

    def confirmation_view_for(
        self,
        raw_answer: AgentOutput,
        scope: ConversationScope,
    ) -> discord.ui.View | None:
        if not isinstance(raw_answer, OperationResult):
            return None
        if raw_answer.status != "confirm_required":
            return None
        action = self.confirmation_action_for(raw_answer, scope)
        if action is None:
            return None
        return ConfirmationView(
            bot=self,
            scope=scope,
            action=action,
            timeout=max(60, self.config.pending_confirmation_ttl_minutes * 60),
        )

    def confirmation_action_for(self, result: OperationResult, scope: ConversationScope) -> str | None:
        if result.intent == "delete_memory" and self.pending_memory_deletions.latest(
            scope=scope,
            ttl_minutes=self.config.pending_confirmation_ttl_minutes,
        ):
            return "delete_all_memories"
        if result.intent == "remember" and self.pending_attachments.latest(
            scope=scope,
            ttl_minutes=self.config.pending_confirmation_ttl_minutes,
        ):
            return "save_attachment"
        return None

    async def handle_confirmation_button(
        self,
        interaction: discord.Interaction,
        *,
        scope: ConversationScope,
        action: str,
        approved: bool,
    ) -> None:
        if str(interaction.user.id) != scope.user_id:
            await interaction.response.send_message("이 확인 버튼은 요청한 사용자만 누를 수 있어요.", ephemeral=True)
            return

        if action == "delete_all_memories":
            text = "응, 전부 삭제해" if approved else "취소해"
            result = self.handle_pending_memory_deletion_confirmation(text=text, scope=scope)
            if result is None:
                result = OperationResult(
                    agent="memory",
                    intent="delete_memory",
                    status="not_found",
                    summary="처리할 삭제 확인 대기 작업 없음",
                    fallback_text="처리할 삭제 확인 대기 작업이 없어요.",
                )
        elif action == "save_attachment":
            if approved:
                channel = interaction.channel
                if channel is None:
                    result = OperationResult(
                        agent="memory",
                        intent="remember",
                        status="not_found",
                        summary="첨부 원본 채널 확인 불가",
                        fallback_text="첨부 원본 메시지를 확인하지 못했어요.",
                    )
                else:
                    proxy_message = SimpleNamespace(
                        id=interaction.message.id if interaction.message else 0,
                        channel=channel,
                    )
                    result = await self.handle_remember(
                        message=proxy_message,  # type: ignore[arg-type]
                        text="",
                        attachments=[],
                        scope=scope,
                    )
            else:
                pending = self.pending_attachments.resolve_latest(
                    scope=scope,
                    ttl_minutes=self.config.pending_confirmation_ttl_minutes,
                )
                if pending is None:
                    result = OperationResult(
                        agent="registry",
                        intent="cancel_pending",
                        status="not_found",
                        summary="취소할 첨부 저장 대기 작업 없음",
                        fallback_text="취소할 첨부 저장 대기 작업이 없어요.",
                    )
                else:
                    filenames = ", ".join(pending.filenames)
                    result = OperationResult(
                        agent="registry",
                        intent="cancel_pending",
                        status="success",
                        summary="첨부 저장 대기 작업 취소",
                        facts={"filenames": list(pending.filenames)},
                        preserve_values=tuple(pending.filenames),
                        fallback_text=f"`{filenames}` 첨부 저장을 취소했어요.",
                    )
        else:
            result = OperationResult(
                agent="bot",
                intent="unsupported",
                status="unsupported",
                summary="알 수 없는 버튼 확인 작업",
                fallback_text="이 버튼으로 처리할 수 있는 작업을 찾지 못했어요.",
            )

        answer = await self.response_composer.compose(
            user_text="버튼 승인" if approved else "버튼 거부",
            raw_response=result,
            scope=scope,
            location_label="Discord 버튼",
            conversation_context="",
        )
        await interaction.response.edit_message(content=answer, view=None)
        if self.user:
            self.conversations.add_message(
                conversation_id=scope.conversation_id,
                role="user",
                user_id=scope.user_id,
                content="버튼 승인" if approved else "버튼 거부",
            )
            self.conversations.add_message(
                conversation_id=scope.conversation_id,
                role="assistant",
                user_id=str(self.user.id),
                content=answer,
            )

    async def should_respond(self, message: discord.Message) -> bool:
        if isinstance(message.channel, discord.DMChannel):
            return True
        if self.user and self.user in message.mentions:
            return True
        if message.reference and message.reference.message_id:
            try:
                referenced = await message.channel.fetch_message(message.reference.message_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                return False
            return bool(self.user and referenced.author.id == self.user.id)
        return False

    def scope_for(self, message: discord.Message) -> ConversationScope:
        guild_id = str(message.guild.id) if message.guild else None
        if isinstance(message.channel, discord.DMChannel):
            conversation_id = f"dm:{message.author.id}"
        elif isinstance(message.channel, discord.Thread):
            conversation_id = f"thread:{message.channel.id}:user:{message.author.id}"
        else:
            conversation_id = f"channel:{message.channel.id}:user:{message.author.id}"

        return ConversationScope(
            conversation_id=conversation_id,
            channel_id=str(message.channel.id),
            user_id=str(message.author.id),
            guild_id=guild_id,
        )

    async def handle_message(
        self,
        *,
        message: discord.Message,
        text: str,
        attachments: list[discord.Attachment],
        scope: ConversationScope,
        author_name: str,
        conversation_context: str,
    ) -> AgentOutput:
        supported_attachments = [
            attachment for attachment in attachments if is_supported_attachment(attachment.filename)
        ]
        pending_deletion_response = self.handle_pending_memory_deletion_confirmation(text=text, scope=scope)
        if pending_deletion_response is not None:
            return pending_deletion_response

        pending_capture_response = await self.handle_pending_memory_capture(
            text=text,
            scope=scope,
            message_id=str(message.id),
        )
        if pending_capture_response is not None:
            return pending_capture_response

        route = await self.router.route(
            text=text,
            has_attachments=bool(supported_attachments),
            scope=scope,
            conversation_context=conversation_context,
        )

        if supported_attachments and text.strip() and route.intent != "unsupported":
            save_result = await self.handle_remember(
                message=message,
                text=text,
                attachments=supported_attachments,
                scope=scope,
            )
            if asks_attached_document_response(text):
                return await self.answer_about_attached_documents(
                    text=text,
                    scope=scope,
                    save_result=save_result,
                )
            return save_result

        if route.intent == "remember":
            remember_result = await self.handle_remember(
                message=message,
                text=text,
                attachments=supported_attachments,
                scope=scope,
            )
            if (
                isinstance(remember_result, OperationResult)
                and remember_result.facts.get("capture_mode") == "next_message"
            ):
                self.pending_memory_captures.add(scope=scope, message_id=str(message.id))
            return remember_result

        if route.intent == "delete_memory":
            if asks_to_delete_all_memories(text):
                return self.request_memory_deletion_confirmation(
                    message_id=str(message.id),
                    scope=scope,
                )

        if route.intent == "unsupported":
            return await self.agent_registry.dispatch(
                route.intent,
                AgentContext(
                    text=text,
                    scope=scope,
                    message_id=str(message.id),
                    author_name=author_name,
                    location_label=describe_message_location(message),
                    has_attachments=bool(supported_attachments),
                ),
            )

        if supported_attachments and not asks_to_remember(text):
            filenames = ", ".join(attachment.filename for attachment in supported_attachments)
            self.pending_attachments.add(
                scope=scope,
                message_id=str(message.id),
                filenames=[attachment.filename for attachment in supported_attachments],
            )
            fallback = (
                f"`{filenames}` 첨부를 확인했어요. 기억해두길 원하면 이 메시지에 "
                "“응, 기억해줘”라고 답장해 주세요. 저장하지 않으려면 “취소해”라고 답장하면 됩니다."
            )
            return OperationResult(
                agent="bot",
                intent="remember",
                status="confirm_required",
                summary="첨부 파일 기억 저장 확인 대기",
                facts={"filenames": [attachment.filename for attachment in supported_attachments]},
                next_actions=("기억하려면 확인 답장을 요청한다", "저장하지 않으려면 취소 답장을 안내한다"),
                preserve_values=tuple(attachment.filename for attachment in supported_attachments),
                fallback_text=fallback,
            )

        if attachments and not supported_attachments:
            filenames = ", ".join(attachment.filename for attachment in attachments)
            fallback = (
                f"`{filenames}` 첨부는 아직 읽을 수 없어요. "
                "현재는 `.txt`, `.md`, `.pdf` 파일만 기억할 수 있습니다."
            )
            return OperationResult(
                agent="bot",
                intent="remember",
                status="unsupported",
                summary="지원하지 않는 첨부 파일 형식",
                facts={
                    "filenames": [attachment.filename for attachment in attachments],
                    "supported_extensions": [".txt", ".md", ".pdf"],
                },
                preserve_values=tuple(attachment.filename for attachment in attachments),
                fallback_text=fallback,
            )

        return await self.agent_registry.dispatch(
            route.intent,
            AgentContext(
                text=text,
                scope=scope,
                message_id=str(message.id),
                author_name=author_name,
                location_label=describe_message_location(message),
                has_attachments=bool(supported_attachments),
            ),
        )

    def handle_pending_memory_deletion_confirmation(
        self, *, text: str, scope: ConversationScope
    ) -> OperationResult | None:
        expired_count = self.pending_memory_deletions.resolve_expired(
            scope=scope,
            ttl_minutes=self.config.pending_confirmation_ttl_minutes,
        )
        pending = self.pending_memory_deletions.latest(scope=scope)
        if pending is None:
            if expired_count and (is_positive_confirmation(text) or is_negative_confirmation(text)):
                fallback = (
                    "전체 기억 삭제 확인 시간이 만료됐어요. "
                    "삭제하려면 다시 `내 기억 전부 삭제해줘`라고 말해 주세요."
                )
                return OperationResult(
                    agent="memory",
                    intent="delete_memory",
                    status="confirm_required",
                    summary="전체 기억 삭제 확인 시간 만료",
                    next_actions=("삭제하려면 다시 전체 기억 삭제를 요청하도록 안내한다",),
                    fallback_text=fallback,
                )
            return None
        if is_negative_confirmation(text):
            self.pending_memory_deletions.resolve(pending.id)
            return OperationResult(
                agent="memory",
                intent="delete_memory",
                status="success",
                summary="전체 기억 삭제 취소",
                fallback_text="전체 기억 삭제를 취소했어요.",
            )
        if not is_memory_deletion_confirmation(text):
            return None

        self.pending_memory_deletions.resolve(pending.id)
        deleted_count = self.memories.delete_all_for_user(scope=scope)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="delete_memory",
            difficulty="easy",
            model=self.config.easy_model,
            reason="사용자 전체 장기 기억 삭제 확인 후 실행",
        )
        if deleted_count == 0:
            return OperationResult(
                agent="memory",
                intent="delete_memory",
                status="not_found",
                summary="삭제할 저장 기억 없음",
                fallback_text="삭제할 저장 기억이 없어요.",
            )
        return OperationResult(
            agent="memory",
            intent="delete_memory",
            status="success",
            summary="사용자 기준 저장 기억 전체 삭제 완료",
            facts={"deleted_count": deleted_count},
            preserve_values=(str(deleted_count),),
            fallback_text=f"확인했어요. 사용자 기준 저장 기억 {deleted_count}개를 모두 삭제 처리했어요.",
        )

    async def handle_pending_memory_capture(
        self,
        *,
        text: str,
        scope: ConversationScope,
        message_id: str,
    ) -> OperationResult | None:
        pending = self.pending_memory_captures.latest(
            scope=scope,
            ttl_minutes=self.config.pending_confirmation_ttl_minutes,
        )
        if pending is None:
            return None
        if is_memory_capture_cancel(text):
            self.pending_memory_captures.resolve(pending.id)
            return OperationResult(
                agent="memory",
                intent="remember",
                status="success",
                summary="메모 대기 취소",
                fallback_text="알겠어요. 이번 메모 대기는 취소할게요.",
            )
        if not text.strip():
            return OperationResult(
                agent="memory",
                intent="remember",
                status="needs_input",
                summary="메모 대기 중 빈 메시지 수신",
                next_actions=("저장할 내용을 한 번 더 요청한다",),
                fallback_text="이건 메모 내용으로 보기 어려워요. 저장할 내용을 한 번만 더 적어주세요.",
            )

        duplicate = self.memories.find_duplicate_text_memory(scope=scope, text=text)
        if duplicate is not None:
            self.pending_memory_captures.resolve(pending.id)
            return OperationResult(
                agent="memory",
                intent="remember",
                status="success",
                summary="메모 대기 중 정확한 중복 확인",
                facts={
                    "duplicate_memory_id": duplicate.id,
                    "source_location": duplicate.source_location,
                    "text": text,
                },
                preserve_values=(str(duplicate.id), duplicate.source_location),
                fallback_text=(
                    f"이미 같은 내용을 기억하고 있어요. 기존 메모 ID는 `{duplicate.id}`이고, "
                    f"저장 위치는 {duplicate.source_location}입니다."
                ),
            )

        similar = await self.memories.search(scope=scope, query=text, limit=1)
        if similar and similar[0].kind == "memory" and similar[0].score >= 0.82:
            self.pending_memory_captures.resolve(pending.id)
            return OperationResult(
                agent="memory",
                intent="remember",
                status="confirm_required",
                summary="유사 메모 수정/병합 제안",
                facts={
                    "candidate_memory_id": similar[0].id,
                    "candidate_title": similar[0].title,
                    "similarity": similar[0].score,
                    "new_text": text,
                },
                preserve_values=(str(similar[0].id), similar[0].title),
                fallback_text=(
                    f"비슷한 메모 `{similar[0].id}` · {similar[0].title}가 있어요. "
                    "기존 메모에 덧붙일까요, 새로 저장할까요?"
                ),
            )

        self.pending_memory_captures.resolve(pending.id)
        memory_id = await self.memories.save_text_memory(
            scope=scope,
            text=text,
            source_message_id=message_id,
        )
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="remember",
            difficulty="easy",
            model=self.config.easy_model,
            reason="대기 중인 다음 메시지 메모 저장",
        )
        return OperationResult(
            agent="memory",
            intent="remember",
            status="success",
            summary="대기 중인 다음 메시지 메모 저장 완료",
            facts={"memory_id": memory_id, "text": text},
            preserve_values=(str(memory_id),),
            fallback_text=f"메모해뒀어요. 저장 ID는 `{memory_id}`입니다.",
        )

    def request_memory_deletion_confirmation(self, *, message_id: str, scope: ConversationScope) -> OperationResult:
        stats = self.memories.stats(scope=scope)
        total = stats["memories"] + stats["documents"]
        if total == 0:
            return OperationResult(
                agent="memory",
                intent="delete_memory",
                status="not_found",
                summary="삭제할 저장 기억 없음",
                fallback_text="삭제할 저장 기억이 없어요.",
            )
        self.pending_memory_deletions.add(
            scope=scope,
            message_id=message_id,
            memory_count=stats["memories"],
            document_count=stats["documents"],
        )
        fallback = (
            f"정말 사용자 기준 저장 기억 전체를 삭제할까요? "
            f"현재 텍스트 기억 {stats['memories']}개, 문서 {stats['documents']}개가 대상입니다. "
            f"{self.config.pending_confirmation_ttl_minutes}분 안에 이 메시지에 `응, 전부 삭제해`라고 답장해 주세요. "
            "취소하려면 `취소해`라고 답장하면 됩니다."
        )
        return OperationResult(
            agent="memory",
            intent="delete_memory",
            status="confirm_required",
            summary="사용자 기준 저장 기억 전체 삭제 확인 필요",
            facts={
                "memory_count": stats["memories"],
                "document_count": stats["documents"],
                "ttl_minutes": self.config.pending_confirmation_ttl_minutes,
            },
            next_actions=("정해진 시간 안에 삭제 확인 답장을 요청한다", "취소할 수 있음을 안내한다"),
            preserve_values=(
                str(stats["memories"]),
                str(stats["documents"]),
                str(self.config.pending_confirmation_ttl_minutes),
            ),
            fallback_text=fallback,
        )

    async def handle_remember(
        self,
        *,
        message: discord.Message,
        text: str,
        attachments: list[discord.Attachment],
        scope: ConversationScope,
    ) -> AgentOutput:
        saved_results: list[OperationResult] = []
        effective_attachments = attachments
        source_message_id = str(message.id)
        pending_request_id: int | None = None

        if not effective_attachments:
            pending = self.pending_attachments.latest(
                scope=scope,
                ttl_minutes=self.config.pending_confirmation_ttl_minutes,
            )
            if pending:
                try:
                    original_message = await message.channel.fetch_message(int(pending.message_id))
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    original_message = None

                if original_message:
                    effective_attachments = [
                        attachment
                        for attachment in original_message.attachments
                        if is_supported_attachment(attachment.filename)
                    ]
                    source_message_id = str(original_message.id)
                    pending_request_id = pending.id

        if text.strip() and not effective_attachments:
            saved_results.append(
                await self.memory_agent.remember_text(
                    text=text,
                    scope=scope,
                    message_id=str(message.id),
                )
            )

        for attachment in effective_attachments:
            try:
                extracted = await extract_attachment_text(
                    attachment,
                    max_bytes=self.config.max_attachment_bytes,
                )
            except ValueError as error:
                saved_results.append(
                    OperationResult(
                        agent="memory",
                        intent="remember",
                        status="unsupported",
                        summary="첨부 파일 저장 실패",
                        facts={"filename": attachment.filename, "error": str(error)},
                        preserve_values=(attachment.filename,),
                        fallback_text=f"`{attachment.filename}`은 저장하지 못했어요. {error}",
                    )
                )
                continue

            duplicate = self.memories.find_duplicate_document(scope=scope, text=extracted.text)
            if duplicate is not None:
                self.logs.add(
                    conversation_id=scope.conversation_id,
                    agent="memory",
                    intent="remember",
                    difficulty="easy",
                    model=self.config.easy_model,
                    reason="동일한 문서 내용 중복 저장 방지",
                )
                fallback = (
                    f"`{extracted.filename}`과 같은 내용을 이미 기억하고 있어요. "
                    f"기존 문서 ID는 `{duplicate.id}`, 저장 위치는 {duplicate.source_location}입니다."
                )
                saved_results.append(
                    OperationResult(
                        agent="memory",
                        intent="remember",
                        status="success",
                        summary="중복 문서 기억 확인",
                        facts={
                            "filename": extracted.filename,
                            "duplicate_document_id": duplicate.id,
                            "source_location": duplicate.source_location,
                        },
                        preserve_values=(extracted.filename, str(duplicate.id), duplicate.source_location),
                        fallback_text=fallback,
                    )
                )
                continue

            document_id, chunk_count = await self.memories.save_document(
                scope=scope,
                filename=extracted.filename,
                content_type=extracted.content_type,
                text=extracted.text,
                source_message_id=source_message_id,
            )
            fallback = (
                f"`{extracted.filename}` 문서를 기억해둘게요. "
                f"문서 ID는 `{document_id}`, chunk는 {chunk_count}개입니다."
            )
            saved_results.append(
                OperationResult(
                    agent="memory",
                    intent="remember",
                    status="success",
                    summary="문서 기억 저장 완료",
                    facts={
                        "filename": extracted.filename,
                        "document_id": document_id,
                        "chunk_count": chunk_count,
                        "content_type": extracted.content_type,
                    },
                    preserve_values=(extracted.filename, str(document_id), str(chunk_count)),
                    fallback_text=fallback,
                )
            )

        if not saved_results:
            return OperationResult(
                agent="memory",
                intent="remember",
                status="needs_input",
                summary="기억할 내용 없음",
                next_actions=("텍스트나 지원하는 첨부 파일과 함께 다시 말해 달라고 안내한다",),
                fallback_text="기억할 내용을 찾지 못했어요. 텍스트나 지원하는 첨부 파일과 함께 다시 말해 주세요.",
            )

        if pending_request_id is not None and any("문서" in result for result in saved_results):
            self.pending_attachments.resolve(pending_request_id)

        if len(saved_results) == 1:
            return saved_results[0]

        fallback = "\n".join(str(result) for result in saved_results)
        return OperationResult(
            agent="memory",
            intent="remember",
            status="success",
            summary="기억 저장 결과 묶음",
            facts={"result_count": len(saved_results)},
            items=tuple(
                {
                    "agent": result.agent,
                    "intent": result.intent,
                    "status": result.status,
                    "summary": result.summary,
                    "facts": result.facts,
                }
                for result in saved_results
            ),
            preserve_values=tuple(
                value
                for result in saved_results
                for value in result.preserve_values
            ),
            fallback_text=fallback,
        )

    async def answer_about_attached_documents(
        self,
        *,
        text: str,
        scope: ConversationScope,
        save_result: AgentOutput,
    ) -> OperationResult:
        operation_result = (
            save_result
            if isinstance(save_result, OperationResult)
            else OperationResult.legacy(str(save_result))
        )
        document_ids = extract_saved_document_ids(operation_result)
        documents = [
            detail
            for document_id in document_ids
            if (detail := self.memories.get_document_detail(scope=scope, document_id=document_id)) is not None
        ]
        if not documents:
            return operation_result

        document_context = "\n\n".join(
            f"[문서 {detail.id}: {detail.title}]\n{detail.text[:8000]}"
            for detail in documents
        )
        answer = await self.openai.text_response(
            model=self.config.medium_model,
            instructions=f"""
{ASSISTANT_PERSONA}

너는 방금 사용자가 첨부한 문서를 읽고 요청에 바로 답한다.
문서는 이미 코드가 장기 기억에 저장했다.
사용자 요청이 요약이면 핵심 내용을 간결하게 정리한다.
문서에 없는 내용은 추측하지 않는다.
답변 끝에 참고한 문서 ID와 파일명을 짧게 적는다.
""",
            input_text=(
                f"사용자 요청:\n{text}\n\n"
                f"방금 저장된 첨부 문서:\n{document_context}"
            ),
            temperature=0.2,
        )
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="recall",
            difficulty="medium",
            model=self.config.medium_model,
            reason="첨부 문서 자동 저장 후 사용자 요청에 즉시 답변",
        )
        return OperationResult(
            agent="memory",
            intent="recall",
            status="success",
            summary="첨부 문서 자동 저장 후 요청 답변 완료",
            facts={
                "document_ids": document_ids,
                "saved_result": operation_result.to_prompt_text(),
                "answer": answer.strip(),
            },
            items=tuple(
                {
                    "kind": "document",
                    "id": detail.id,
                    "title": detail.title,
                    "chunk_count": detail.chunk_count,
                }
                for detail in documents
            ),
            preserve_values=tuple(str(document_id) for document_id in document_ids),
            fallback_text=answer.strip(),
        )


class ConfirmationView(discord.ui.View):
    def __init__(
        self,
        *,
        bot: AssistantBot,
        scope: ConversationScope,
        action: str,
        timeout: float,
    ) -> None:
        super().__init__(timeout=timeout)
        self.bot = bot
        self.scope = scope
        self.action = action

    @discord.ui.button(label="승인", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.bot.handle_confirmation_button(
            interaction,
            scope=self.scope,
            action=self.action,
            approved=True,
        )

    @discord.ui.button(label="거부", style=discord.ButtonStyle.secondary)
    async def reject(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.bot.handle_confirmation_button(
            interaction,
            scope=self.scope,
            action=self.action,
            approved=False,
        )


def asks_to_remember(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in ["기억해", "저장해", "remember", "save this"])


def asks_attached_document_response(text: str) -> bool:
    normalized = text.casefold()
    compact = "".join(normalized.split())
    document_markers = ["문서", "파일", "첨부", "pdf", "document", "file"]
    action_markers = [
        "요약",
        "정리",
        "분석",
        "설명",
        "검토",
        "알려",
        "찾아",
        "뽑아",
        "추출",
        "봐",
        "해봐",
        "summary",
        "summarize",
        "analyze",
        "explain",
    ]
    return any(marker in normalized or marker in compact for marker in document_markers) and any(
        marker in normalized or marker in compact for marker in action_markers
    )


def extract_saved_document_ids(result: OperationResult) -> list[int]:
    ids: list[int] = []
    for key in ("document_id", "duplicate_document_id"):
        value = result.facts.get(key)
        if isinstance(value, int):
            ids.append(value)
    for item in result.items:
        facts = item.get("facts")
        if isinstance(facts, dict):
            for key in ("document_id", "duplicate_document_id"):
                value = facts.get(key)
                if isinstance(value, int):
                    ids.append(value)
        if item.get("kind") == "document" and isinstance(item.get("id"), int):
            ids.append(int(item["id"]))
    return list(dict.fromkeys(ids))


def is_positive_confirmation(text: str) -> bool:
    normalized = text.strip().lower()
    return any(
        marker in normalized
        for marker in [
            "응",
            "네",
            "예",
            "맞아",
            "확인",
            "삭제해",
            "전부 삭제",
            "모두 삭제",
            "yes",
            "ok",
            "confirm",
        ]
    )


def is_memory_deletion_confirmation(text: str) -> bool:
    normalized = text.strip().lower()
    if not is_positive_confirmation(normalized):
        return False

    delete_markers = ["삭제", "지워", "delete", "remove"]
    scope_markers = ["전부", "전체", "모두", "all", "everything"]
    return any(marker in normalized for marker in delete_markers) and any(
        marker in normalized for marker in scope_markers
    )


def is_negative_confirmation(text: str) -> bool:
    normalized = text.strip().lower()
    return any(
        marker in normalized
        for marker in ["취소", "아니", "하지마", "하지 마", "no", "cancel", "never mind"]
    )


def is_memory_capture_cancel(text: str) -> bool:
    normalized = text.strip().lower()
    compact = "".join(normalized.split())
    markers = [
        "메모 그만",
        "메모그만",
        "메모 취소",
        "메모취소",
        "저장하지 마",
        "저장하지마",
        "기억하지 마",
        "기억하지마",
        "취소",
        "cancel",
        "stop memo",
    ]
    return any(marker in normalized or marker in compact for marker in markers)


def describe_attachments(attachments: list[discord.Attachment]) -> str:
    if not attachments:
        return ""
    return "첨부 파일: " + ", ".join(attachment.filename for attachment in attachments)


def describe_message_location(message: discord.Message) -> str:
    if isinstance(message.channel, discord.DMChannel):
        return "DM"
    guild_name = message.guild.name if message.guild else "서버"
    if isinstance(message.channel, discord.Thread):
        return f"서버 `{guild_name}`의 스레드 `#{message.channel.name}`"
    channel_name = getattr(message.channel, "name", str(message.channel.id))
    return f"서버 `{guild_name}`의 채널 `#{channel_name}`"
