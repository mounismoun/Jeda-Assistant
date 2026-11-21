"""개편판 전용 SQLite. Discord 원문과 수정 가능한 작업 상태는 별도로 보관한다."""

from __future__ import annotations

import json
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


# Match only a whole, affirmative command. Quoted, qualified or negative requests go through the router.
def requests_all_memories(text):
    return bool(
        re.fullmatch(
            r"(?:(?:이 채널(?:에(?:서)?|의)?|여기서)\s*(?:보이는|있는|조회할 수 있는)?\s*)?"
            r"(?:(?:내가 저장한|내|제)\s*)?(?:(?:기억|메모리)(?:을|를)?\s*(?:모두|전부|다|전체)|"
            r"(?:모든|전체)\s*(?:기억|메모리)(?:을|를)?)\s*"
            r"(?:지워|삭제해)(?:\s*(?:줘|주세요))?[.!]*"
            r"|(?:please\s+)?(?:clear|delete|remove) all (?:of )?my (?:saved )?memories(?: in this channel)?[.!]*",
            text.strip(),
            re.I,
        )
    )


@dataclass(frozen=True)
class Scope:
    guild: str
    channel: str
    user: str

    @property
    def key(self) -> str:
        return json.dumps([self.guild, self.channel, self.user], separators=(",", ":"))


_SCHEMA = """
CREATE TABLE IF NOT EXISTS jeda_schema(version INTEGER PRIMARY KEY CHECK(version=1));
INSERT OR IGNORE INTO jeda_schema VALUES(1);
CREATE TABLE IF NOT EXISTS sessions(
    scope TEXT PRIMARY KEY, epoch INTEGER NOT NULL DEFAULT 1, touched REAL NOT NULL,
    summary TEXT NOT NULL DEFAULT '', summarized INTEGER NOT NULL DEFAULT 0, instruction TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS raw_messages(
    seq INTEGER PRIMARY KEY, scope TEXT NOT NULL, epoch INTEGER NOT NULL, msg TEXT NOT NULL,
    role TEXT NOT NULL, content TEXT NOT NULL, created REAL NOT NULL, UNIQUE(scope, msg));
CREATE TRIGGER IF NOT EXISTS raw_no_edit BEFORE UPDATE ON raw_messages BEGIN
    SELECT RAISE(ABORT,'immutable original'); END;
CREATE TRIGGER IF NOT EXISTS raw_no_delete BEFORE DELETE ON raw_messages BEGIN
    SELECT RAISE(ABORT,'immutable original'); END;
CREATE TABLE IF NOT EXISTS memory(
    id INTEGER PRIMARY KEY, scope TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL,
    value TEXT NOT NULL, source TEXT NOT NULL, version INTEGER NOT NULL, active INTEGER NOT NULL,
    UNIQUE(scope,kind,name));
CREATE TABLE IF NOT EXISTS memory_versions(
    scope TEXT NOT NULL, memory_id INTEGER NOT NULL, version INTEGER NOT NULL,
    value TEXT NOT NULL, source TEXT NOT NULL, PRIMARY KEY(memory_id,version));
CREATE TABLE IF NOT EXISTS memory_queue(
    source TEXT PRIMARY KEY, scope TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
    result TEXT);
CREATE TABLE IF NOT EXISTS mutations(
    scope TEXT NOT NULL, msg TEXT NOT NULL, result TEXT NOT NULL, PRIMARY KEY(scope,msg));
CREATE TABLE IF NOT EXISTS approvals(
    ticket TEXT PRIMARY KEY, scope TEXT NOT NULL, source TEXT NOT NULL, snapshot TEXT NOT NULL, mode TEXT NOT NULL,
    expires REAL NOT NULL, UNIQUE(scope,source));
CREATE TABLE IF NOT EXISTS inbox(
    id TEXT PRIMARY KEY, scope TEXT NOT NULL, request TEXT NOT NULL, response TEXT NOT NULL DEFAULT '',
    done INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS by_inbox_state ON inbox(done,scope);
CREATE TABLE IF NOT EXISTS receipts(msg TEXT PRIMARY KEY,job TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS jobs(
    id TEXT PRIMARY KEY, scope TEXT NOT NULL, epoch INTEGER NOT NULL, revision INTEGER NOT NULL DEFAULT 0,
    state TEXT NOT NULL, generation TEXT NOT NULL DEFAULT '', request TEXT NOT NULL, updates TEXT NOT NULL DEFAULT '[]',
    evidence TEXT NOT NULL DEFAULT '{}', answer TEXT NOT NULL DEFAULT '', sent TEXT NOT NULL DEFAULT '[]');
CREATE TABLE IF NOT EXISTS web_reads(job TEXT NOT NULL, revision INTEGER NOT NULL, chunks TEXT NOT NULL,
    PRIMARY KEY(job,revision));
CREATE TABLE IF NOT EXISTS search_usage(day TEXT NOT NULL,user TEXT NOT NULL, count INTEGER NOT NULL,
    PRIMARY KEY(day,user));
CREATE INDEX IF NOT EXISTS by_conversation ON raw_messages(scope,epoch,seq);
CREATE INDEX IF NOT EXISTS by_job_scope ON jobs(scope,state);
"""


class JedaStore:
    def __init__(self, path: str | Path):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        tables = {
            row[0]
            for row in self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        }
        if tables and "jeda_schema" not in tables:
            self.db.close()
            raise ValueError("기존 DB입니다. JEDA_DATABASE_PATH에 개편판 전용 새 경로를 지정하세요.")
        try:
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.executescript(_SCHEMA)
        except Exception:
            self.db.close()
            raise

    def close(self):
        self.db.close()

    def session(self, scope: Scope):
        now = time.time()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO sessions(scope,touched) VALUES(?,?)", (scope.key, now))
            self.db.execute(
                """UPDATE sessions SET epoch=epoch+1,touched=?,summary='',summarized=0,instruction=''
                   WHERE scope=? AND touched<? AND NOT EXISTS
                   (SELECT 1 FROM jobs WHERE scope=? AND state IN ('running','sending'))""",
                (now, scope.key, now - 86400, scope.key),
            )
        return self.db.execute("SELECT * FROM sessions WHERE scope=?", (scope.key,)).fetchone()

    def reset_session(self, scope: Scope, source=None):
        self.session(scope)
        with self.db:
            if (
                source
                and not self.db.execute(
                    "INSERT OR IGNORE INTO mutations VALUES(?,?,?)", (scope.key, source, "1")
                ).rowcount
            ):
                return
            self.db.execute(
                "UPDATE sessions SET epoch=epoch+1,touched=?,summary='',summarized=0,instruction='' WHERE scope=?",
                (time.time(), scope.key),
            )
            self.db.execute("DELETE FROM approvals WHERE scope=?", (scope.key,))

    def record(self, scope: Scope, msg: str, role: str, content: str, *, epoch: int | None = None) -> bool:
        if epoch is None:
            epoch = self.session(scope)["epoch"]
        now = time.time()
        with self.db:
            added = self.db.execute(
                "INSERT OR IGNORE INTO raw_messages(scope,epoch,msg,role,content,created) VALUES(?,?,?,?,?,?)",
                (scope.key, epoch, msg, role, content, now),
            ).rowcount
            self.db.execute("UPDATE sessions SET touched=? WHERE scope=?", (now, scope.key))
        return bool(added)

    def history(self, scope: Scope, *, current_session=False, query="", limit=100, after=0):
        sql = "SELECT * FROM raw_messages WHERE scope=? AND seq>?"
        args = [scope.key, after]
        if current_session:
            sql += " AND epoch=?"
            args.append(self.session(scope)["epoch"])
        if query:
            sql += " AND instr(lower(content),lower(?))>0"
            args.append(query)
        rows = self.db.execute(sql + " ORDER BY seq DESC LIMIT ?", (*args, limit)).fetchall()
        return list(reversed(rows))

    def last_clarification(self, scope, epoch, current_id):
        row = self.db.execute(
            "SELECT i.request,i.response FROM raw_messages m LEFT JOIN inbox i ON i.id=m.msg AND i.scope=m.scope "
            "WHERE m.scope=? AND m.epoch=? AND m.role='user' AND m.msg!=? ORDER BY m.seq DESC LIMIT 1",
            (scope.key, epoch, current_id),
        ).fetchone()
        if not row or not row["response"]:
            return None
        kind, question, *tags = json.loads(row["response"])
        # Previously stored clarification replies had no explicit tag.
        if kind == "final" and (tags == ["clarification"] or not tags and question.rstrip().endswith(("?", "？"))):
            return {"request": json.loads(row["request"])["text"], "question": question}
        return None

    def memories(self, scope: Scope, *, include_deleted=False):
        condition = "" if include_deleted else " AND active=1"
        return self.db.execute(
            "SELECT * FROM memory WHERE scope IN (?,?)" + condition + " ORDER BY id DESC",
            (scope.key, self.preference_scope(scope)),
        ).fetchall()

    @staticmethod
    def preference_scope(scope: Scope):
        return "user:" + scope.user

    def save_memory(self, scope: Scope, msg: str, kind: str, name: str, value: str):
        owner = self.preference_scope(scope) if kind == "language" else scope.key
        with self.db:
            previous = self.db.execute(
                "SELECT result FROM mutations WHERE scope=? AND msg=?", (scope.key, msg)
            ).fetchone()
            if previous:
                return int(previous[0])
            # A slow background decision cannot undo a newer explicit correction from this owner.
            current = self.db.execute(
                "SELECT source FROM memory WHERE scope=? AND kind=? AND name=?", (owner, kind, name)
            ).fetchone()
            if current:
                incoming_id, previous_id = msg.split(":")[0], current[0].split(":")[0]
                seqs = dict(
                    self.db.execute(
                        "SELECT msg,seq FROM raw_messages WHERE msg IN (?,?) AND role='user'",
                        (incoming_id, previous_id),
                    )
                )
                if seqs.get(incoming_id, 0) and seqs.get(previous_id, 0) > seqs[incoming_id]:
                    self.db.execute("INSERT INTO mutations VALUES(?,?,?)", (scope.key, msg, "0"))
                    return 0
            self.db.execute(
                """INSERT OR IGNORE INTO memory_versions SELECT scope,id,version,value,source FROM memory
                   WHERE scope=? AND kind=? AND name=?""",
                (owner, kind, name),
            )
            row = self.db.execute(
                """INSERT INTO memory(scope,kind,name,value,source,version,active) VALUES(?,?,?,?,?,1,1)
                   ON CONFLICT(scope,kind,name) DO UPDATE SET value=excluded.value,source=excluded.source,
                   active=1,version=version+1 RETURNING id""",
                (owner, kind, name, value, msg),
            ).fetchone()
            self.db.execute("INSERT INTO mutations VALUES(?,?,?)", (scope.key, msg, str(row[0])))
            return row[0]

    def change_active(self, scope: Scope, msg: str, memory_id: int, active: bool):
        with self.db:
            previous = self.db.execute(
                "SELECT result FROM mutations WHERE scope=? AND msg=?", (scope.key, msg)
            ).fetchone()
            if previous:
                return bool(int(previous[0]))
            changed = self.db.execute(
                "UPDATE memory SET active=?,source=?,version=version+1 WHERE id=? AND scope IN (?,?) AND active!=?",
                (active, msg, memory_id, scope.key, self.preference_scope(scope), active),
            ).rowcount
            self.db.execute("INSERT INTO mutations VALUES(?,?,?)", (scope.key, msg, str(changed)))
            return bool(changed)

    def snapshot(self, scope: Scope, ids=None):
        return json.dumps(
            sorted((r["id"], r["version"]) for r in self.memories(scope) if ids is None or r["id"] in ids)
        )

    def request_clear(self, scope: Scope, source: str, ttl=600, ids=None):
        with self.db:
            self.db.execute(
                "INSERT OR IGNORE INTO approvals VALUES(?,?,?,?,?,?)",
                (
                    uuid4().hex[:12],
                    scope.key,
                    source,
                    self.snapshot(scope, ids),
                    "all" if ids is None else "subset",
                    time.time() + ttl,
                ),
            )
        return self.db.execute(
            "SELECT ticket FROM approvals WHERE scope=? AND source=?", (scope.key, source)
        ).fetchone()[0]

    def approve_clear(self, scope: Scope, ticket: str):
        with self.db:
            return self._approve_clear(scope, ticket)

    def resolve_ticket(self, scope, source, ticket, reject):
        with self.db:
            if reject:
                changed = self.db.execute(
                    "DELETE FROM approvals WHERE scope=? AND ticket=?", (scope.key, ticket)
                ).rowcount
                answer = "요청을 취소했습니다." if changed else "이 위치에서 취소할 해당 요청이 없습니다."
            else:
                success = self._approve_clear(scope, ticket, source)
                answer = (
                    "승인한 메모리를 삭제했습니다."
                    if success
                    else "실행하지 않았습니다. 대상 변경·만료·승인 범위를 확인해 주세요."
                )
            self.db.execute(
                "UPDATE inbox SET response=? WHERE id=? AND scope=?", (json.dumps(["final", answer]), source, scope.key)
            )
            return answer

    def _approve_clear(self, scope, ticket, source=None):
        row = self.db.execute(
            "DELETE FROM approvals WHERE scope=? AND ticket=? RETURNING snapshot,expires,mode,source",
            (scope.key, ticket),
        ).fetchone()
        if not row or row["expires"] <= time.time():
            return False
        ids = None if row["mode"] == "all" else {i for i, _ in json.loads(row["snapshot"])}
        if ids is not None:
            # Pending tickets created by older routers can have pinned IDs for a whole-scope request.
            incoming = self.db.execute(
                "SELECT request FROM inbox WHERE scope=? AND id=?", (scope.key, row["source"].partition(":")[0])
            ).fetchone()
            if incoming and requests_all_memories(json.loads(incoming["request"])["text"]):
                ids = None
        if row["snapshot"] != self.snapshot(scope, ids):
            return False
        for memory_id, version in json.loads(row["snapshot"]):
            self.db.execute(
                "UPDATE memory SET active=0,source=COALESCE(?,source),version=version+1 WHERE id=? AND version=?",
                (source, memory_id, version),
            )
        return True

    def reserve_search(self, day: str, user: str, limit: int):
        if limit < 1:
            return False
        with self.db:
            return bool(
                self.db.execute(
                    """INSERT INTO search_usage VALUES(?,?,1) ON CONFLICT(day,user) DO UPDATE SET
                   count=count+1 WHERE count<? RETURNING count""",
                    (day, user, limit),
                ).fetchone()
            )
