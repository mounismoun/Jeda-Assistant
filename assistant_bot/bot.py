from __future__ import annotations

import asyncio
import logging

import discord

from assistant_bot.agent_registry import AgentContext, build_agent_registry
from assistant_bot.agents import (
    ConversationAgent,
    MemoryAgent,
    RouterAgent,
    TaskAgent,
    UtilityAgent,
    asks_to_delete_all_memories,
    format_conversation_context,
    format_task_priority,
    has_substantive_memory_text,
)
from assistant_bot.config import Config
from assistant_bot.database import AppDatabase
from assistant_bot.file_extractor import extract_attachment_text, is_supported_attachment
from assistant_bot.models import ConversationScope
from assistant_bot.openai_service import OpenAIService
from assistant_bot.stores import (
    AgentLogStore,
    ConversationStore,
    MemoryStore,
    PendingAttachmentStore,
    PendingMemoryDeletionStore,
    TaskStore,
)
from assistant_bot.text_utils import split_discord_message, strip_bot_mentions
from assistant_bot.time_utils import now_in_timezone, today_string

logger = logging.getLogger(__name__)


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
        self.logs = AgentLogStore(self.database.connection)
        self.conversations = ConversationStore(self.database.connection)
        self.pending_attachments = PendingAttachmentStore(self.database.connection)
        self.pending_memory_deletions = PendingMemoryDeletionStore(self.database.connection)
        self.tasks = TaskStore(self.database.connection)
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
            conversation_agent=self.conversation_agent,
            pending_attachments=self.pending_attachments,
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
        if not self._task_reminder_started:
            self._task_reminder_started = True
            self.loop.create_task(self.task_reminder_loop())

    async def task_reminder_loop(self) -> None:
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                await self.send_due_task_reminders()
            except Exception:
                logger.exception("할 일 리마인더 처리 중 오류")
            await asyncio.sleep(max(1, self.config.task_reminder_interval_minutes) * 60)

    async def send_due_task_reminders(self) -> int:
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

        async with message.channel.typing():
            try:
                answer = await self.handle_message(
                    message=message,
                    text=clean_text,
                    attachments=attachments,
                    scope=scope,
                    author_name=author_name,
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

        for part in split_discord_message(answer):
            await message.reply(part, mention_author=False)

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
    ) -> str:
        supported_attachments = [
            attachment for attachment in attachments if is_supported_attachment(attachment.filename)
        ]
        pending_deletion_response = self.handle_pending_memory_deletion_confirmation(text=text, scope=scope)
        if pending_deletion_response is not None:
            return pending_deletion_response

        route = await self.router.route(
            text=text,
            has_attachments=bool(supported_attachments),
            scope=scope,
            conversation_context=format_conversation_context(
                self.conversations.recent_messages(scope.conversation_id, limit=8)
            ),
        )

        if route.intent == "remember":
            return await self.handle_remember(
                message=message,
                text=text,
                attachments=supported_attachments,
                scope=scope,
            )

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
            return (
                f"`{filenames}` 첨부를 확인했어요. 기억해두길 원하면 이 메시지에 "
                "“응, 기억해줘”라고 답장해 주세요. 저장하지 않으려면 “취소해”라고 답장하면 됩니다."
            )

        if attachments and not supported_attachments:
            filenames = ", ".join(attachment.filename for attachment in attachments)
            return (
                f"`{filenames}` 첨부는 아직 읽을 수 없어요. "
                "현재는 `.txt`, `.md`, `.pdf` 파일만 기억할 수 있습니다."
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

    def handle_pending_memory_deletion_confirmation(self, *, text: str, scope: ConversationScope) -> str | None:
        expired_count = self.pending_memory_deletions.resolve_expired(
            scope=scope,
            ttl_minutes=self.config.pending_confirmation_ttl_minutes,
        )
        pending = self.pending_memory_deletions.latest(scope=scope)
        if pending is None:
            if expired_count and (is_positive_confirmation(text) or is_negative_confirmation(text)):
                return "전체 기억 삭제 확인 시간이 만료됐어요. 삭제하려면 다시 `내 기억 전부 삭제해줘`라고 말해 주세요."
            return None
        if is_negative_confirmation(text):
            self.pending_memory_deletions.resolve(pending.id)
            return "전체 기억 삭제를 취소했어요."
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
            return "삭제할 저장 기억이 없어요."
        return f"확인했어요. 사용자 기준 저장 기억 {deleted_count}개를 모두 삭제 처리했어요."

    def request_memory_deletion_confirmation(self, *, message_id: str, scope: ConversationScope) -> str:
        stats = self.memories.stats(scope=scope)
        total = stats["memories"] + stats["documents"]
        if total == 0:
            return "삭제할 저장 기억이 없어요."
        self.pending_memory_deletions.add(
            scope=scope,
            message_id=message_id,
            memory_count=stats["memories"],
            document_count=stats["documents"],
        )
        return (
            f"정말 사용자 기준 저장 기억 전체를 삭제할까요? "
            f"현재 텍스트 기억 {stats['memories']}개, 문서 {stats['documents']}개가 대상입니다. "
            f"{self.config.pending_confirmation_ttl_minutes}분 안에 이 메시지에 `응, 전부 삭제해`라고 답장해 주세요. "
            "취소하려면 `취소해`라고 답장하면 됩니다."
        )

    async def handle_remember(
        self,
        *,
        message: discord.Message,
        text: str,
        attachments: list[discord.Attachment],
        scope: ConversationScope,
    ) -> str:
        saved_messages: list[str] = []
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

        if text.strip() and (not effective_attachments or has_substantive_memory_text(text)):
            saved_messages.append(
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
                saved_messages.append(f"`{attachment.filename}`은 저장하지 못했어요. {error}")
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
                saved_messages.append(
                    f"`{extracted.filename}`과 같은 내용을 이미 기억하고 있어요. "
                    f"기존 문서 ID는 `{duplicate.id}`, 저장 위치는 {duplicate.source_location}입니다."
                )
                continue

            document_id, chunk_count = await self.memories.save_document(
                scope=scope,
                filename=extracted.filename,
                content_type=extracted.content_type,
                text=extracted.text,
                source_message_id=source_message_id,
            )
            saved_messages.append(
                f"`{extracted.filename}` 문서를 기억해둘게요. 문서 ID는 `{document_id}`, chunk는 {chunk_count}개입니다."
            )

        if not saved_messages:
            return "기억할 내용을 찾지 못했어요. 텍스트나 지원하는 첨부 파일과 함께 다시 말해 주세요."

        if pending_request_id is not None and any("문서" in message for message in saved_messages):
            self.pending_attachments.resolve(pending_request_id)

        return "\n".join(saved_messages)


def asks_to_remember(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in ["기억해", "저장해", "remember", "save this"])


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
