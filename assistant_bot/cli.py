from __future__ import annotations

import argparse
import asyncio
import os
import sqlite3
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

from assistant_bot.jeda_server import no_typing
from assistant_bot.openai_service import Models, Settings
from assistant_bot.runtime import Engine, Output, Request
from assistant_bot.stores import JedaStore, Scope


async def ask(text, user):
    cfg = Settings.load()
    path = Path(cfg.database)
    engine = Engine(cfg, JedaStore(path.with_name(path.stem + ".local" + path.suffix)), Models(cfg))

    async def send(kind, content, tag):
        print(content)
        return uuid4().hex

    async def load(_):
        raise ValueError("첨부가 필요한 경우 로컬 서버에 파일과 요청을 전달해 주세요.")

    try:
        await engine.submit(Scope("local", "cli", user), Request(uuid4().hex, text), Output(send, load, no_typing))
        if engine.background:
            await asyncio.gather(*engine.background)
    finally:
        await engine.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Jeda Assistant 관리")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="설정값의 유무와 DB 위치 확인")
    commands.add_parser("stats", help="개편판 DB 현황")
    back = commands.add_parser("backup", help="SQLite 백업")
    back.add_argument("--output", type=Path, required=True)
    chat = commands.add_parser("ask", help="개발 DB에서 동일한 엔진으로 질문")
    chat.add_argument("text")
    chat.add_argument("--user", default="operator")
    args = parser.parse_args()
    load_dotenv()
    path = Path(os.getenv("JEDA_DATABASE_PATH", Settings.database))
    if args.command == "doctor":
        for key in ["DISCORD_TOKEN", "OPENAI_API_KEY"]:
            print(key, "설정됨" if os.getenv(key) else "비어 있음")
        print("Jeda DB", path)
        return
    if args.command == "ask":
        asyncio.run(ask(args.text, args.user))
        return
    if not path.is_file():
        parser.error("아직 개편판 DB가 없습니다.")
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as source:
        if not source.execute("SELECT 1 FROM sqlite_master WHERE name='jeda_schema'").fetchone():
            parser.error("개편판 DB가 아닙니다.")
        if args.command == "backup":
            with args.output.open("xb"):
                pass
            with sqlite3.connect(args.output) as dest:
                source.backup(dest)
        else:
            for name in ("raw_messages", "jobs", "memory", "sessions"):
                print(name, source.execute(f"SELECT count(*) FROM {name}").fetchone()[0])
