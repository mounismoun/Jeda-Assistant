"""Read-only browser views of the production SQLite archive. All times shown are KST."""

import asyncio
import json
import sqlite3
import time
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from assistant_bot.context_builder import TOOLS

HOST = "127.0.0.1"
PORT = 8766
ASSETS = Path(__file__).with_name("dashboard_assets")
KST = ZoneInfo("Asia/Seoul")
PAGE_SIZE = 40
PAGES = {"overview": "개요", "conversations": "대화", "memories": "메모리", "stats": "통계", "request": "요청 상세"}
PERIODS = {"hour": "시간별", "day": "일별", "week": "주별", "month": "월별"}
STATES = {
    "open": "종료 미기록",
    "ok": "성공",
    "failed": "실패",
    "cancelled": "취소",
    "steered": "정정",
    "running": "진행 중",
    "sending": "전송 중",
    "done": "처리 완료",
    "unavailable": "접근 불가",
    "partial": "일부 완료",
    "success": "성공",
    "pending": "대기",
    "needs_input": "확인 필요",
}
TEMPLATES = Environment(loader=FileSystemLoader(ASSETS), autoescape=True, trim_blocks=True, lstrip_blocks=True)
TEMPLATES.policies["json.dumps_kwargs"] = {"ensure_ascii": False, "sort_keys": True}


def timestamp(value):
    return datetime.fromtimestamp(value, KST).strftime("%Y.%m.%d %H:%M:%S") if value is not None else "—"


def link(page, **params):
    query = urlencode({key: value for key, value in params.items() if value not in ("", None)})
    return f"/{page}" + (f"?{query}" if query else "")


TEMPLATES.filters.update(stamp=timestamp, number=lambda x: f"{x:,}" if x is not None else "—")
TEMPLATES.globals.update(link=link, states=STATES, pages=PAGES, periods=PERIODS, tools=TOOLS)


def directory(db):
    scopes = db.execute("""
        SELECT s.scope, (SELECT json_extract(i.request,'$.discord_names') FROM inbox i
           WHERE i.scope=s.scope AND json_type(i.request,'$.discord_names')='object' ORDER BY i.rowid DESC LIMIT 1)
        FROM (SELECT scope FROM sessions UNION SELECT scope FROM raw_messages
              UNION SELECT scope FROM memory WHERE json_valid(scope)) s
        ORDER BY (SELECT max(seq) FROM raw_messages m WHERE m.scope=s.scope) DESC
    """)
    places, users = {}, {}
    for scope, names in scopes:
        guild, channel, user = json.loads(scope)
        names = json.loads(names or "{}")
        places[scope] = dict(
            user=user,
            guild=guild,
            channel=channel,
            author=names.get("user_display_name") or user,
            server=names.get("server") or guild,
            room=names.get("channel") or channel,
        )
        if user not in users or users[user] == user:
            users[user] = names.get("user_display_name") or user
    for (user,) in db.execute("SELECT DISTINCT substr(scope,6) FROM memory WHERE scope LIKE 'user:%'"):
        users.setdefault(user, user)
    return places, users


def day_start(value):
    return datetime.combine(value, datetime.min.time(), KST).timestamp()


def bounds(params):
    start = date.fromisoformat(params["start"]) if params.get("start") else None
    end = date.fromisoformat(params["end"]) if params.get("end") else None
    if start and end and start > end:
        raise ValueError("종료일이 시작일보다 앞섭니다.")
    return day_start(start) if start else 0, day_start(end + timedelta(days=1)) if end else 253402214400


# A bot message may be a receipt (first reply) or a fragment of a job's final answer.
MESSAGE_JOBS = """
    WITH links(msg,job) AS (
        SELECT msg,job FROM receipts
        UNION SELECT json_extract(p.value,'$.msg'),j.id FROM jobs j,json_each(j.sent) p
        WHERE json_extract(p.value,'$.msg') IS NOT NULL
    )
"""
FAILED = """(j.state='unavailable' OR EXISTS (SELECT 1 FROM request_errors e WHERE e.job=i.id)
    OR EXISTS (SELECT 1 FROM model_calls c WHERE c.job=i.id AND c.status='failed')
    OR EXISTS (SELECT 1 FROM json_each(j.evidence) t WHERE json_extract(t.value,'$.status') IN ('failed','partial')))"""


def conversations(db, p):
    where, args = ["m.created>=?", "m.created<?"], list(bounds(p))
    for index, field in enumerate(("guild", "channel", "user")):
        if p.get(field):
            where.append(f"json_extract(m.scope,'$[{index}]')=?")
            args.append(p[field])
    if p.get("q"):
        where.append("instr(lower(m.content),lower(?))>0")
        args.append(p["q"])
    if p.get("attachments"):
        where.append("""(json_array_length(i.request,'$.attachments')>0
                      OR json_array_length(i.request,'$.reply.attachments')>0)""")
    if p.get("tool"):
        where.append("EXISTS (SELECT 1 FROM json_each(j.evidence) t WHERE json_extract(t.value,'$.tool')=?)")
        args.append(p["tool"])
    if p.get("failed"):
        where.append(FAILED)
    page = max(1, int(p.get("page", 1)))
    rows = db.execute(
        MESSAGE_JOBS
        + """
        SELECT m.*,i.id AS job,i.request AS payload,j.state FROM raw_messages m
        LEFT JOIN links l ON l.msg=m.msg LEFT JOIN inbox i ON i.id=coalesce(l.job,m.msg) AND i.scope=m.scope
        LEFT JOIN jobs j ON j.id=i.id WHERE """
        + " AND ".join(where)
        + " ORDER BY m.seq DESC LIMIT ? OFFSET ?",
        (*args, PAGE_SIZE + 1, (page - 1) * PAGE_SIZE),
    ).fetchall()
    messages = []
    for row in rows[:PAGE_SIZE]:
        item = dict(row)
        payload = json.loads(item.pop("payload") or "{}")
        item["files"] = [a["name"] for a in payload.get("attachments", [])] if row["role"] == "user" else []
        messages.append(item)
    return dict(messages=messages, page=page, more=len(rows) > PAGE_SIZE)


def detail(db, key):
    inbox = db.execute("SELECT * FROM inbox WHERE id=?", (key,)).fetchone()
    if not inbox:
        raise web.HTTPNotFound(text="요청 기록을 찾을 수 없습니다.")
    job = db.execute("SELECT * FROM jobs WHERE id=?", (key,)).fetchone()
    req = json.loads(inbox["request"])
    reply = json.loads(inbox["response"]) if inbox["response"] else []
    result = dict(
        scope=inbox["scope"],
        req=req,
        key=key,
        state="done" if inbox["done"] else "pending",
        answer=reply[1] if reply else "",
        plan={},
        changes=[],
        evidence={},
        sent=[],
        parents=[],
        receipts=db.execute("SELECT msg FROM receipts WHERE job=?", (key,)).fetchall(),
    )
    if job:
        result.update(
            state=job["state"],
            answer=job["answer"] or result["answer"],
            plan=json.loads(job["request"])["plan"],
            changes=json.loads(job["updates"]),
            evidence=json.loads(job["evidence"]),
            sent=json.loads(job["sent"]),
        )
    else:
        result["parents"] = db.execute(
            "SELECT j.id FROM jobs j,json_each(j.updates) u WHERE j.scope=? AND json_extract(u.value,'$.id')=?",
            (inbox["scope"], key),
        ).fetchall()
    result["calls"] = db.execute("SELECT * FROM model_calls WHERE job=? ORDER BY started", (key,)).fetchall()
    result["errors"] = db.execute("SELECT * FROM request_errors WHERE job=? ORDER BY created", (key,)).fetchall()
    return result


def memories(db, p):
    page = max(1, int(p.get("page", 1)))
    query = "SELECT * FROM memory"
    args = []
    if p.get("user"):
        query += " WHERE scope=? OR CASE WHEN json_valid(scope) THEN json_extract(scope,'$[2]') END=?"
        args.extend(["user:" + p["user"], p["user"]])
    rows = db.execute(
        query + " ORDER BY id DESC LIMIT ? OFFSET ?", (*args, PAGE_SIZE + 1, (page - 1) * PAGE_SIZE)
    ).fetchall()
    items = []
    for row in rows[:PAGE_SIZE]:
        versions = list(
            map(
                dict,
                db.execute(
                    """
            SELECT v.version,v.value,v.source,s.active FROM memory_versions v
            LEFT JOIN memory_version_states s USING(memory_id,version)
            WHERE v.memory_id=? ORDER BY v.version DESC
        """,
                    (row["id"],),
                ),
            )
        )
        for version in versions:
            version["job"] = version["source"].partition(":")[0]
        items.append(dict(**row, versions=versions, job=row["source"].partition(":")[0]))
    return dict(memories=items, page=page, more=len(rows) > PAGE_SIZE)


def overview(db):
    today = day_start(datetime.now(KST).date())
    last = db.execute("SELECT max(created) FROM raw_messages WHERE role='user'").fetchone()[0]
    counts = [
        db.execute(q, args).fetchone()[0]
        for q, args in (
            ("SELECT count(*) FROM raw_messages WHERE role='user' AND created>=?", (today,)),
            ("SELECT count(*) FROM model_calls WHERE started>=?", (today,)),
            ("SELECT count(*) FROM jobs WHERE state IN ('running','sending')", ()),
            ("SELECT count(*) FROM memory WHERE active=1", ()),
        )
    ]
    recent = db.execute("""
        SELECT m.created,m.content,m.scope,i.id,coalesce(j.state,CASE WHEN i.done THEN 'done' ELSE 'pending' END) state
        FROM raw_messages m JOIN inbox i ON i.id=m.msg
        LEFT JOIN jobs j ON j.id=i.id WHERE m.role='user' ORDER BY m.seq DESC LIMIT 8
    """).fetchall()
    failures = db.execute(
        """
        SELECT i.id,m.content,m.created FROM inbox i LEFT JOIN jobs j ON j.id=i.id
        JOIN raw_messages m ON m.msg=i.id AND m.scope=i.scope WHERE """
        + FAILED
        + " ORDER BY m.seq DESC LIMIT 6"
    ).fetchall()
    running = db.execute("""
        SELECT m.created,m.content,m.scope,j.id,j.state FROM jobs j
        JOIN raw_messages m ON m.msg=j.id AND m.scope=j.scope
        WHERE j.state IN ('running','sending') ORDER BY m.seq DESC
    """).fetchall()
    return dict(
        counts=counts,
        recent=recent,
        failures=failures,
        running=running,
        last=last,
        today=datetime.now(KST).date().isoformat(),
    )


def statistics(db, p):
    period = p.get("period", "day")
    if period not in PERIODS:
        raise ValueError("집계 단위를 확인하세요.")
    start, end = bounds(p)
    bucket = {
        "hour": "strftime('%Y-%m-%d %H:00', instant,'unixepoch','+9 hours')",
        "day": "date(instant,'unixepoch','+9 hours')",
        "week": "date(instant,'unixepoch','+9 hours','-6 days','weekday 1')",
        "month": "strftime('%Y-%m',instant,'unixepoch','+9 hours')",
    }[period]
    events = """WITH events AS (
        SELECT started instant,1 calls,0 requests,status,retry,input_tokens,output_tokens,seconds
        FROM model_calls WHERE started>=? AND started<?
        UNION ALL SELECT created,0,1,NULL,0,NULL,NULL,NULL FROM raw_messages
        WHERE role='user' AND created>=? AND created<?)
    """
    rows = db.execute(
        events
        + f"""
        SELECT {bucket} bucket,min(instant) first_at,max(instant) last_at,sum(requests) requests,sum(calls) calls,
          sum(status='failed') failures,sum(retry) retries,sum(input_tokens) input,sum(output_tokens) output,
          avg(seconds) latency FROM events GROUP BY bucket ORDER BY bucket DESC
    """,
        (start, end, start, end),
    ).fetchall()
    models = db.execute(
        """
        SELECT model,purpose,count(*) calls,sum(status='failed') failures,sum(retry) retries,
               sum(input_tokens) input,sum(output_tokens) output,avg(seconds) latency
        FROM model_calls WHERE started>=? AND started<? GROUP BY model,purpose ORDER BY calls DESC,model,purpose
    """,
        (start, end),
    ).fetchall()
    return dict(buckets=rows, models=models, period=period, peak=max((r["calls"] for r in rows), default=1) or 1)


def render(path, page, params, status):
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2)) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        places, users = directory(db)
        collection = db.execute("SELECT started FROM collection_info WHERE id=1").fetchone()
        view = dict(
            view=page,
            p=params,
            places=places,
            users=users,
            status=status,
            collected=collection[0] if collection else None,
            now=time.time(),
        )
        selected = [place for place in places.values() if place["user"] == params.get("user")]
        view["servers"] = {place["guild"]: place["server"] for place in selected}
        view["channels"] = {
            place["channel"]: place["room"] for place in selected if place["guild"] == params.get("guild")
        }
        if page == "overview":
            view.update(overview(db))
        elif page == "conversations":
            view.update(conversations(db, params))
        elif page == "request":
            view["item"] = detail(db, params.get("id", ""))
        elif page == "memories":
            view.update(memories(db, params))
        else:
            today = datetime.now(KST).date()
            if "start" not in params and "end" not in params:
                days = {"hour": 2, "week": 84, "month": 365}.get(params.get("period"), 30)
                params.update(start=(today - timedelta(days=days - 1)).isoformat(), end=today.isoformat())
            view.update(statistics(db, params))
        return TEMPLATES.get_template("dashboard.html").render(view)


def dashboard_app(path, status):
    path = Path(path).resolve()

    @web.middleware
    async def local_only(request, handler):
        port = request.transport.get_extra_info("sockname")[1]
        authority = request.headers.get("Host", "")
        if (
            request.remote != HOST
            or authority not in {f"{HOST}:{port}", f"localhost:{port}"}
            or request.headers.get("Origin", f"http://{authority}") != f"http://{authority}"
            or request.headers.get("Sec-Fetch-Site") == "cross-site"
        ):
            raise web.HTTPForbidden(text="이 PC의 로컬 관리창에서만 접근할 수 있습니다.")
        response = await handler(request)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": (
                    "default-src 'none'; style-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
                ),
            }
        )
        return response

    async def show(request):
        page = request.path.strip("/") or "overview"
        try:
            html = await asyncio.to_thread(render, path, page, dict(request.query), status())
        except (OverflowError, ValueError):
            raise web.HTTPBadRequest(text="조회 날짜나 페이지 번호를 확인하세요.") from None
        return web.Response(text=html, content_type="text/html")

    async def stylesheet(_request):
        return web.FileResponse(ASSETS / "dashboard.css")

    app = web.Application(middlewares=[local_only])
    app.router.add_get("/", show)
    for name in PAGES:
        app.router.add_get("/" + name, show)
    app.router.add_get("/dashboard.css", stylesheet)
    return app
