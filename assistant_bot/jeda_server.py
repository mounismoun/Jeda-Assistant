"""로컬 실서비스 검증용 루프백 HTTP 진입점. Discord와 동일한 Engine 사용."""

from __future__ import annotations

import argparse
import asyncio
import base64
import binascii
import json
import logging
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from aiohttp import web

from assistant_bot.openai_service import Models, Settings
from assistant_bot.runtime import Engine, Output, Request
from assistant_bot.stores import JedaStore, Scope


@asynccontextmanager
async def no_typing():
    yield


def build_app(engine, transport_path):
    app = web.Application(client_max_size=engine.cfg.max_bytes * 2)
    # This sidecar represents Discord in local tests, including deletion and restart.
    transport = sqlite3.connect(transport_path)
    transport.row_factory = sqlite3.Row
    transport.executescript("""
        CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY, channel TEXT, author TEXT, body TEXT);
        CREATE TABLE IF NOT EXISTS fixtures(id TEXT PRIMARY KEY, channel TEXT, message TEXT, data BLOB);
        CREATE TABLE IF NOT EXISTS events(tag TEXT PRIMARY KEY, request TEXT, kind TEXT, message TEXT);
    """)
    pending = set()

    def lookup(channel, key):
        row = transport.execute("SELECT body FROM messages WHERE channel=? AND id=?", (channel, key)).fetchone()
        return json.loads(row[0]) if row else {"id": key, "unavailable": True}

    def output(channel, key):
        async def send(kind, content, tag):
            row = transport.execute("SELECT message FROM events WHERE tag=?", (tag,)).fetchone()
            if row:
                return row[0]
            mid = uuid4().hex
            msg = {"id": mid, "text": content, "attachments": [], "author": "jeda"}
            with transport:
                transport.execute("INSERT INTO messages VALUES(?,?,?,?)", (mid, channel, "jeda", json.dumps(msg)))
                transport.execute("INSERT INTO events VALUES(?,?,?,?)", (tag, key, kind, mid))
            return mid

        async def load(ref):
            row = transport.execute(
                "SELECT data FROM fixtures WHERE id=? AND channel=? AND message=?",
                (ref["id"], channel, ref["message"]),
            ).fetchone()
            if ref.get("guild") != "local" or ref.get("channel") != channel or not row:
                raise ValueError("원본을 찾을 수 없습니다. 파일을 다시 첨부해 주세요.")
            return row[0]

        async def reconcile(tag, _):
            row = transport.execute("SELECT message FROM events WHERE tag=?", (tag,)).fetchone()
            return row[0] if row else ""

        return Output(send, load, no_typing, reconcile)

    async def request_turn(http):
        try:
            body = await http.json()
            user = body["user"]
            channel = body.get("channel", "development")
            text = body["text"]
            if not all(isinstance(v, str) for v in (user, channel, text)) or not user or not channel:
                raise ValueError("user, channel, text 값을 확인해 주세요.")
            key = uuid4().hex
            scope = Scope("local", channel, user)
            reply_to = body.get("reply_to")
            if reply_to is not None and not isinstance(reply_to, str):
                raise ValueError("reply_to에는 메시지 ID 문자열이 필요합니다.")
            reply = lookup(channel, reply_to) if reply_to else None
            attachments = []
            with transport:
                for a in body.get("attachments", []):
                    data = base64.b64decode(a["base64"], validate=True)
                    if len(data) > engine.cfg.max_bytes:
                        raise ValueError("파일 크기 초과")
                    aid = uuid4().hex
                    transport.execute("INSERT INTO fixtures VALUES(?,?,?,?)", (aid, channel, key, data))
                    attachments.append(
                        {
                            "id": aid,
                            "name": Path(a["name"]).name,
                            "size": len(data),
                            "guild": "local",
                            "channel": channel,
                            "message": key,
                        }
                    )
                msg = {"id": key, "author": user, "text": text, "attachments": attachments}
                transport.execute("INSERT INTO messages VALUES(?,?,?,?)", (key, channel, user, json.dumps(msg)))
        except (ValueError, TypeError, KeyError, binascii.Error) as exc:
            raise web.HTTPBadRequest(text=str(exc)) from exc
        req = Request(key, text, attachments, reply)
        engine.register(scope, req)
        out = output(channel, key)

        async def run():
            try:
                await engine.submit(scope, req, out)
            except Exception:
                logging.getLogger(__name__).exception("local request failed")
                await out.send("error", "서버 오류", key + ":error")

        task = asyncio.create_task(run())
        pending.add(task)
        task.add_done_callback(pending.discard)
        if body.get("wait", True):
            await task
        return web.json_response(view(key))

    def view(key):
        row = transport.execute("SELECT body FROM messages WHERE id=?", (key,)).fetchone()
        if not row:
            raise web.HTTPNotFound()
        job = engine.job(key)
        events = [
            {
                "kind": event["kind"],
                "id": event["message"],
                "tag": event["tag"],
                "text": json.loads(event["body"])["text"],
            }
            for event in transport.execute(
                "SELECT e.*, m.body FROM events e JOIN messages m ON e.message=m.id WHERE request=? ORDER BY e.rowid",
                (key,),
            )
        ]
        return {
            "id": key,
            "events": events,
            "attachments": json.loads(row[0])["attachments"],
            "state": job["state"] if job else None,
            "revision": job["revision"] if job else None,
            "generation": job["generation"] if job else None,
            "route": json.loads(job["request"])["plan"]["role"] if job else None,
            "evidence": json.loads(job["evidence"]) if job else {},
        }

    async def result(http):
        return web.json_response(view(http.match_info["key"]))

    async def remove_fixture(http):
        with transport:
            changed = transport.execute(
                "DELETE FROM fixtures WHERE message=? AND id=?", (http.match_info["key"], http.match_info["aid"])
            ).rowcount
        if not changed:
            raise web.HTTPNotFound()
        return web.Response(status=204)

    async def resume(_):
        queued = {}
        for item in engine.store.db.execute("SELECT * FROM inbox WHERE done=0 ORDER BY rowid").fetchall():
            scope = Scope(*json.loads(item["scope"]))
            if scope.guild == "local" and not lookup(scope.channel, item["id"]).get("unavailable"):
                queued[item["id"]] = True
                task = asyncio.create_task(
                    engine.submit(scope, Request(**json.loads(item["request"])), output(scope.channel, item["id"]))
                )
                pending.add(task)
                task.add_done_callback(pending.discard)
        for job in engine.store.db.execute("SELECT * FROM jobs WHERE state IN ('running','sending')").fetchall():
            scope = Scope(*json.loads(job["scope"]))
            if (
                job["id"] not in queued
                and scope.guild == "local"
                and not lookup(scope.channel, job["id"]).get("unavailable")
            ):
                engine.start(scope, job["id"], output(scope.channel, job["id"]))
        engine.resume_memory()

    async def cleanup(_):
        tasks = list(pending)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await engine.shutdown()
        transport.close()

    app.router.add_post("/requests", request_turn)
    app.router.add_get("/requests/{key}", result)
    app.router.add_delete("/requests/{key}/attachments/{aid}", remove_fixture)
    app.on_startup.append(resume)
    app.on_cleanup.append(cleanup)
    return app


def main():
    parser = argparse.ArgumentParser(description="Jeda Assistant 로컬 API 검증 서버")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    cfg = Settings.load()
    path = Path(cfg.database)
    # Keep test conversations out of the production archive.
    local_path = path.with_name(path.stem + ".local" + path.suffix)
    engine = Engine(cfg, JedaStore(local_path), Models(cfg))
    web.run_app(build_app(engine, str(local_path) + ".transport"), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
