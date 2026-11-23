from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import time
from contextlib import AsyncExitStack
from datetime import UTC, datetime

import discord
from aiohttp import web
from discord.http import Route

from assistant_bot.dashboard import HOST, PORT, dashboard_app
from assistant_bot.runtime import Engine, Output, Request
from assistant_bot.stores import Scope


def directly_invoked(guild_id, author_is_bot, content, bot_id):
    return bool(guild_id and not author_is_bot and re.search(rf"<@!?{int(bot_id)}>", content))


def attachment_refs(message):
    return [
        {
            "id": str(a.id),
            "name": a.filename,
            "size": a.size,
            "guild": str(message.guild.id),
            "channel": str(message.channel.id),
            "message": str(message.id),
        }
        for a in message.attachments
    ]


class JedaDiscord(discord.Client):
    def __init__(self, engine: Engine):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, allowed_mentions=discord.AllowedMentions.none())
        self.engine = engine
        self.dashboard_runner = None
        self.connected = False
        self.last_connected = None

    async def setup_hook(self):
        def status():
            return {"connected": self.connected, "last_connected": self.last_connected}

        runner = web.AppRunner(dashboard_app(self.engine.cfg.database, status), access_log=None)
        await runner.setup()
        try:
            await web.TCPSite(runner, HOST, PORT).start()
        except OSError:
            await runner.cleanup()
            logging.getLogger(__name__).exception("로컬 관리창 포트 %s를 열 수 없습니다.", PORT)
            return
        self.dashboard_runner = runner
        logging.getLogger(__name__).info("로컬 상태 관리창 http://%s:%s", HOST, PORT)

    async def on_resumed(self):
        self.connected = True
        self.last_connected = time.time()

    async def on_disconnect(self):
        self.connected = False

    async def on_ready(self):
        self.connected = True
        self.last_connected = time.time()
        await self.change_presence(activity=discord.CustomActivity(name="Jeda Assistant · 서버에서 @멘션해 주세요"))
        # Only unfinished work owned by the Discord adapter is recoverable here.
        rows = self.engine.store.db.execute(
            "SELECT id,scope FROM inbox WHERE done=0 UNION "
            "SELECT id,scope FROM jobs WHERE state IN ('running','sending')"
        ).fetchall()
        self.engine.resume_memory()

        for row in rows:
            guild_id, channel_id, user_id = json.loads(row["scope"])
            if not all(i.isdecimal() for i in (guild_id, channel_id, user_id, row["id"])):
                continue
            try:
                channel = self.get_channel(int(channel_id)) or await self.fetch_channel(int(channel_id))
                original = await channel.fetch_message(int(row["id"]))
            except (discord.NotFound, discord.Forbidden):
                with self.engine.store.db as db:
                    db.execute("UPDATE inbox SET done=1 WHERE id=?", (row["id"],))
                    db.execute(
                        "UPDATE jobs SET state='unavailable' WHERE id=? AND state IN ('running','sending')",
                        (row["id"],),
                    )
                continue
            except discord.HTTPException:
                continue  # Retry this item on reconnect and recover the remaining rows now.
            scope = Scope(guild_id, channel_id, user_id)
            out = self.output(scope, original)
            pending = self.engine.store.db.execute(
                "SELECT request FROM inbox WHERE id=? AND done=0", (row["id"],)
            ).fetchone()
            if pending:
                task = asyncio.create_task(self.engine.submit(scope, Request(**json.loads(pending[0])), out))
                self.engine.background.add(task)
                task.add_done_callback(self.engine.background.discard)
            elif self.engine.job(row["id"]):
                self.engine.start(scope, row["id"], out)

    async def on_message(self, message):
        if not self.user or not directly_invoked(
            message.guild and message.guild.id, message.author.bot, message.content, self.user.id
        ):
            return
        scope = Scope(str(message.guild.id), str(message.channel.id), str(message.author.id))
        async with AsyncExitStack() as first_reply:
            try:
                await first_reply.enter_async_context(message.channel.typing())
            except Exception:
                logging.getLogger(__name__).warning("첫 응답의 입력 중 표시를 시작하지 못했습니다.", exc_info=True)
            reply = await self.read_reply(message)
            text = re.sub(rf"<@!?{self.user.id}>", "", message.content).strip()
            await self.engine.submit(
                scope,
                Request(
                    str(message.id),
                    text,
                    attachment_refs(message),
                    reply,
                    original=message.content,
                    discord_names={
                        "server": message.guild.name,
                        "channel": message.channel.name,
                        "user_display_name": message.author.display_name,
                    },
                ),
                self.output(scope, message, first_reply=first_reply),
            )

    async def read_reply(self, message):
        reference = message.reference
        if reference and reference.message_id and reference.channel_id == message.channel.id:
            try:
                source = await message.channel.fetch_message(reference.message_id)
                return {
                    "id": str(source.id),
                    "author": str(source.author.id),
                    "text": source.content,
                    "attachments": attachment_refs(source),
                }
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                return {"id": str(reference.message_id), "unavailable": True}
        return None

    def output(self, scope, message, *, first_reply=None):
        channel = message.channel

        async def load(ref):
            if (ref.get("guild"), ref.get("channel")) != (scope.guild, scope.channel):
                raise ValueError("이 위치에서는 해당 첨부를 읽을 수 없습니다.")
            try:
                source = await channel.fetch_message(int(ref["message"]))
                attachment = next((a for a in source.attachments if str(a.id) == str(ref["id"])), None)
                if not attachment:
                    raise ValueError("원래 첨부가 삭제됐습니다. 파일을 다시 첨부해 주세요.")
                if attachment.size > self.engine.cfg.max_bytes:
                    raise ValueError("첨부 파일 크기 한도를 초과했습니다.")
                return await attachment.read()
            except discord.NotFound as exc:
                raise ValueError("원본 메시지가 삭제됐습니다. 파일을 다시 첨부해 주세요.") from exc
            except discord.Forbidden as exc:
                raise ValueError("원본을 읽을 권한이 없습니다.") from exc

        async def send(kind, text, key):
            payload = {
                "content": text,
                "flags": discord.MessageFlags(suppress_embeds=True).value,
                "allowed_mentions": {"parse": [], "replied_user": False},
                "message_reference": {"message_id": str(message.id), "fail_if_not_exists": False},
                "nonce": hashlib.blake2s(key.encode(), digest_size=12).hexdigest(),
                "enforce_nonce": True,
            }
            try:
                response = await self.http.request(
                    Route("POST", "/channels/{channel_id}/messages", channel_id=channel.id), json=payload
                )
            finally:
                if first_reply is not None:
                    await first_reply.aclose()
            return str(response["id"])

        async def reconcile(key, text):
            # Only claim absence after exhausting the range after the original message.
            count = 0
            job = self.engine.job(str(message.id))
            previous = {s.get("msg") for s in json.loads(job["sent"])} if job else set()
            previous.update(
                r[0] for r in self.engine.store.db.execute("SELECT msg FROM receipts WHERE job=?", (str(message.id),))
            )
            since = message
            if job and (index := key.rsplit(":", 1)[-1]).isdecimal():
                slot = json.loads(job["sent"])[int(index)]
                since = datetime.fromtimestamp(slot["started"] - 5, UTC)
            async for item in channel.history(limit=101, after=since, oldest_first=True):
                count += 1
                if (
                    self.user
                    and item.author.id == self.user.id
                    and item.reference
                    and item.reference.message_id == message.id
                    and str(item.id) not in previous
                    and item.content == text
                ):
                    return str(item.id)
            return "" if count <= 100 else None

        return Output(send, load, channel.typing, reconcile)

    async def close(self):
        try:
            if self.dashboard_runner is not None:
                await self.dashboard_runner.cleanup()
                self.dashboard_runner = None
            await self.engine.shutdown()
        finally:
            await super().close()
