import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from assistant_bot.bot import JedaDiscord


def test_discord_reply_keeps_links_and_suppresses_previews():
    bot = JedaDiscord(SimpleNamespace())
    bot.http.request = AsyncMock(return_value={"id": "123"})
    message = SimpleNamespace(id=9, channel=SimpleNamespace(id=2, typing=AsyncMock()))
    text = "[출처](https://example.com/article)"
    asyncio.run(bot.output(None, message).send("final", text, "reply"))
    payload = bot.http.request.await_args.kwargs["json"]
    assert payload["content"] == text
    assert payload["flags"] & 4  # Discord SUPPRESS_EMBEDS


@pytest.mark.parametrize("first", ["final", "ack"])
def test_typing_covers_reference_lookup_and_first_response(first):
    events = []

    @asynccontextmanager
    async def typing():
        events.append("start")
        try:
            yield
        finally:
            events.append("stop")

    async def fetch(mid):
        events.append("fetch")
        return SimpleNamespace(id=mid, author=SimpleNamespace(id=7), content="본문", attachments=[])

    async def send(route, *, json):
        events.append(json["content"])
        return {"id": "123"}

    async def submit(scope, request, output):
        events.append("route")
        await output.send(first, first, "first")
        if first == "ack":
            async with output.typing():
                await output.send("final", "final", "second")

    bot = JedaDiscord(SimpleNamespace(submit=submit))
    bot._connection.user = SimpleNamespace(id=3)
    bot.http.request = send
    msg = SimpleNamespace(
        guild=SimpleNamespace(id=1),
        author=SimpleNamespace(id=5, bot=False),
        id=9,
        content="<@3> 질문",
        channel=SimpleNamespace(id=2, typing=typing, fetch_message=fetch),
        attachments=[],
        reference=SimpleNamespace(message_id=6, channel_id=2),
    )
    asyncio.run(bot.on_message(msg))
    expected = ["start", "fetch", "route", first, "stop"]
    assert events == (expected if first == "final" else expected + ["start", "final", "stop"])


@pytest.mark.parametrize("guild,author_is_bot,text", [(None, False, "<@3>"), (1, True, "<@3>"), (1, False, "안녕")])
def test_ignored_messages_do_not_start_typing(guild, author_is_bot, text):
    bot = JedaDiscord(SimpleNamespace(submit=AsyncMock()))
    bot._connection.user = SimpleNamespace(id=3)
    msg = SimpleNamespace(
        guild=SimpleNamespace(id=guild) if guild else None, author=SimpleNamespace(bot=author_is_bot), content=text
    )
    asyncio.run(bot.on_message(msg))
    bot.engine.submit.assert_not_awaited()
