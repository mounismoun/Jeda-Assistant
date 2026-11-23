import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiohttp.test_utils import TestClient, TestServer

from assistant_bot.dashboard import HOST, KST, dashboard_app, statistics
from assistant_bot.metrics import request_context
from assistant_bot.openai_service import Models
from assistant_bot.stores import JedaStore, Scope


@pytest.fixture
def archive(tmp_path):
    path = tmp_path / "봇 기록.sqlite"
    store = JedaStore(path)
    try:
        yield path, store
    finally:
        store.close()


def put_request(store, scope, key, question):
    request = json.dumps(
        {
            "text": question,
            "attachments": [],
            "discord_names": {"user_display_name": "도토리", "server": "연구회", "channel": "일반"},
            "plan": {"role": "everyday", "effort": "low", "calls": [{"name": "web"}]},
        }
    )
    store.record(scope, key, "user", question)
    with store.db as db:
        db.execute("INSERT INTO inbox(id,scope,request,done) VALUES(?,?,?,1)", (key, scope.key, request))
        db.execute(
            "INSERT INTO jobs(id,scope,epoch,request,state,evidence,answer,sent) VALUES(?,?,1,?,'done',?,?,?)",
            (
                key,
                scope.key,
                request,
                json.dumps({"call": {"tool": "web", "status": "success", "text": "근거"}}),
                "최종 답변",
                json.dumps([{"msg": "answer-" + key}]),
            ),
        )
    store.record(scope, "answer-" + key, "assistant", "최종 답변")


def test_local_browser_views_and_scope_filters(archive):
    path, store = archive
    first, other = Scope("g", "c", "u"), Scope("g", "c", "another")
    put_request(store, first, "origin", "내용 <script>alert(1)</script>")
    put_request(store, other, "other", "다른 계정 대화")
    mid = store.save_memory(first, "origin:0", "fact", "이름", "첫 값")
    store.change_active(first, "origin:1", mid, False)
    store.change_active(first, "origin:2", mid, True)
    store.save_memory(first, "origin:language", "language", "언어", "한국어")
    store.save_memory(other, "other:0", "fact", "다른 계정 기억", "다른 값")
    store.record_error("origin", "답변 전송", TimeoutError())

    async def visit():
        app = dashboard_app(path, lambda: {"connected": True, "last_connected": None})
        async with TestClient(TestServer(app, host=HOST)) as client:

            async def html(url):
                response = await client.get(url)
                assert response.status == 200
                assert response.headers["Cache-Control"] == "no-store"
                return await response.text()

            home = await html("/")
            assert "Discord 연결됨" in home and "다른 계정 대화" in home
            for route in (
                "/conversations?user=u",
                "/conversations?user=u&guild=g",
                "/conversations?user=u&guild=g&channel=c&tool=web&failed=1",
            ):
                content = await html(route)
                assert "&lt;script&gt;" in content and "다른 계정 대화" not in content
                assert 'href="/request?id=origin"' in content
            assert "조건에 맞는 대화가 없습니다" in await html("/conversations?q=notfound")
            detail = await html("/request?id=origin")
            assert "TimeoutError" in detail and "최종 답변" in detail
            memory = await html("/memories?user=u")
            assert "첫 값" in memory and "v2 · 삭제됨" in memory and "사용자 공통" in memory
            assert "다른 계정 기억" not in memory
            assert "기록된 요청" in await html("/stats?start=2001-01-01&end=2001-01-01")
            assert "시간별 사용량" in await html("/stats?period=hour")
            assert (await client.get("/", headers={"Host": "example.invalid"})).status == 403
            assert (await client.get("/", headers={"Origin": "https://example.invalid"})).status == 403
            assert (await client.get("/", headers={"Sec-Fetch-Site": "cross-site"})).status == 403
            assert (await client.post("/requests")).status in (404, 405)
            assert (await client.get("/stats?start=oops")).status == 400
            assert (await client.get("/request?id=missing")).status == 404

    asyncio.run(visit())


def test_korean_calendar_buckets_separate_requests_from_calls(archive):
    _, store = archive
    scope = Scope("s", "c", "u")
    store.record(scope, "job", "user", "질문")
    sunday = datetime(2026, 5, 31, 23, 59, tzinfo=KST).timestamp()
    monday = sunday + 60
    with store.db as db:
        db.execute("UPDATE sessions SET touched=?", (sunday,))
        db.execute("INSERT INTO collection_info VALUES(1,?)", (sunday,))
        db.executemany(
            """
            INSERT INTO model_calls(job,model,purpose,retry,started,seconds,status,input_tokens,output_tokens)
            VALUES('job','model','답변',?,?,1,?,?,?)
        """,
            [(0, sunday, "failed", None, None), (1, monday, "ok", 20, 5)],
        )
        db.execute(
            "INSERT INTO raw_messages(scope,epoch,msg,role,content,created) VALUES(?,1,'old','user','이전',?)",
            (scope.key, sunday),
        )
    ranges = {"hour": "2026-05-31 23:00", "day": "2026-05-31", "week": "2026-05-25", "month": "2026-05"}
    for period, first_bucket in ranges.items():
        data = statistics(db, {"period": period, "start": "2026-05-31", "end": "2026-06-01"})
        latest, first = data["buckets"]
        assert (first["bucket"], first["requests"], first["failures"]) == (first_bucket, 1, 1)
        assert latest["requests"] == 0 and latest["retries"] == 1
        assert data["models"][0]["input"] == 20


def test_model_metrics_capture_usage_failure_and_retry_without_payloads(archive):
    _, store = archive
    reply = SimpleNamespace(
        status="completed", output_text="결과", usage=SimpleNamespace(input_tokens=10, output_tokens=4)
    )
    model = object.__new__(Models)
    model.config = SimpleNamespace(timeout=5)
    model.metrics_db = store.db
    model.client = SimpleNamespace(responses=SimpleNamespace(create=AsyncMock(side_effect=[TimeoutError(), reply])))

    async def invoke():
        with request_context("req"):
            with pytest.raises(TimeoutError):
                await model.text("demo", "none", "instruction", "질문", purpose="라우팅")
            await model.text("demo", "none", "instruction", "질문", purpose="라우팅", retry=True)

    asyncio.run(invoke())
    rows = store.db.execute("SELECT job,purpose,status,retry,input_tokens,output_tokens FROM model_calls ORDER BY id")
    assert list(map(tuple, rows)) == [("req", "라우팅", "failed", 0, None, None), ("req", "라우팅", "ok", 1, 10, 4)]


def test_usage_from_raw_search_and_steered_websocket(archive, monkeypatch):
    _, store = archive
    model = object.__new__(Models)
    model.config = SimpleNamespace(api_key="test")
    model.metrics_db = store.db
    raw = SimpleNamespace(content=b'{"status":"completed","usage":{"input_tokens":17,"output_tokens":4}}')
    model.client = SimpleNamespace(
        responses=SimpleNamespace(with_raw_response=SimpleNamespace(create=AsyncMock(return_value=raw)))
    )

    async def invoke():
        events = asyncio.Queue()

        async def emit(message):
            if message["type"] == "response.create":
                events.put_nowait({"type": "response.created", "response": {"id": "first"}})
            else:
                events.put_nowait(
                    {
                        "type": "response.incomplete",
                        "response": {
                            "id": "first",
                            "incomplete_details": {"reason": "steered"},
                            "usage": {"input_tokens": 11, "output_tokens": 2},
                        },
                    }
                )
                events.put_nowait({"type": "response.created", "response": {"id": "next"}})
                events.put_nowait(
                    {
                        "type": "response.completed",
                        "response": {
                            "id": "next",
                            "usage": {"input_tokens": 12, "output_tokens": 3},
                            "output": [{"content": [{"type": "output_text", "text": "수정됨"}]}],
                        },
                    }
                )

        @asynccontextmanager
        async def connect(*args, **kwargs):
            yield SimpleNamespace(send_json=emit, receive_json=events.get)

        @asynccontextmanager
        async def session(**kwargs):
            yield SimpleNamespace(ws_connect=connect)

        monkeypatch.setattr("assistant_bot.openai_service.aiohttp.ClientSession", session)
        queue = asyncio.Queue()
        queue.put_nowait((1, "정정"))
        with request_context("weather"):
            await model.discover("search-model", "low", "test", "질문")
            assert await model.compose("final-model", "low", "test", "질문", queue, limit=50, timeout=5) == (
                "수정됨",
                1,
            )

    asyncio.run(invoke())
    rows = store.db.execute("SELECT job,purpose,status,input_tokens,output_tokens FROM model_calls ORDER BY id")
    assert list(map(tuple, rows)) == [
        ("weather", "웹 검색", "ok", 17, 4),
        ("weather", "답변", "steered", 11, 2),
        ("weather", "답변 정정", "ok", 12, 3),
    ]
