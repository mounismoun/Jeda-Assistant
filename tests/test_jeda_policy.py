"""Discord와 외부 API가 필요 없는 개편판 정책 회귀 사례."""

import asyncio
import json
import sqlite3
from dataclasses import asdict
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from assistant_bot.context_builder import build_context, recent_files
from assistant_bot.openai_service import Settings
from assistant_bot.runtime import Engine, Output, Request
from assistant_bot.stores import JedaStore, Scope, requests_all_memories
from assistant_bot.text_utils import format_numeric_answer

A = Scope("guild", "channel", "A")
B = Scope("guild", "channel", "B")


@pytest.fixture
def store(tmp_path):
    result = JedaStore(tmp_path / "new.sqlite")
    yield result
    result.close()


def test_raw_history_is_scoped_append_only_and_idempotent(store):
    store.record(A, "m", "user", "원래 문장")
    store.record(A, "m", "user", "바뀐 문장")
    assert [r["content"] for r in store.history(A)] == ["원래 문장"]
    assert not store.history(B)
    for sql in ("DELETE FROM raw_messages", "UPDATE raw_messages SET content='changed'"):
        with pytest.raises(sqlite3.IntegrityError):
            store.db.execute(sql)


def test_reset_keeps_original_and_memory(store):
    store.record(A, "m", "user", "기억해줘")
    store.save_memory(A, "m", "fact", "배포일", "금요일")
    store.reset_session(A)
    assert not store.history(A, current_session=True)
    assert store.history(A)[0]["content"] == "기억해줘"
    assert store.memories(A)[0]["value"] == "금요일"


def test_clarification_retains_file_reference_only_in_the_same_session(store):
    ref = {"id": "file", "name": "handoff.txt", "message": "upload"}
    store.record(A, "upload", "user", "")
    store.db.execute(
        "INSERT INTO inbox(id,scope,request,done) VALUES(?,?,?,1)",
        ("upload", A.key, json.dumps({"attachments": [ref]})),
    )
    assert recent_files(store, A) == [ref]
    assert not recent_files(store, B)
    assert not recent_files(store, Scope(A.guild, "other", A.user))
    store.reset_session(A)
    assert not recent_files(store, A)


def test_history_matches_literal_id_in_prose_without_crossing_user_scope(store):
    store.record(A, "old", "user", "검수 코드 P-4e42d902")
    store.record(B, "other", "user", "검수 코드 P-4e42d902")
    store.reset_session(A)
    request = Request("current", "P-4e42d902라는 값이 나왔던 당시 내 발언을 찾아줘.")
    store.record(A, request.id, "user", request.text)
    engine = Engine(None, store, None)
    call = {"name": "history", "query": "P-4e42d902를 언급한 발언", "target": ""}
    result = asyncio.run(engine.execute(A, request, None, call, "step", request.text, {}, None, None))
    assert [row["id"] for row in json.loads(result["text"])] == ["old"]


def test_completed_job_does_not_replay_undelivered_initial_ack(store):
    engine = Engine(None, store, None)
    req = Request("request", "첨부를 확인해줘.")
    engine.register(A, req)
    with store.db as db:
        db.execute("UPDATE inbox SET response=? WHERE id=?", (json.dumps(["ack", "확인하겠습니다."]), req.id))
        db.execute("INSERT INTO jobs(id,scope,epoch,state,request) VALUES(?,?,1,'done','{}')", (req.id, A.key))

    async def send(*args):
        pytest.fail("완료된 요청의 첫 안내가 재전송되었습니다.")

    asyncio.run(engine.submit(A, req, Output(send, None, None)))
    assert store.db.execute("SELECT done FROM inbox WHERE id=?", (req.id,)).fetchone()[0] == 1


def test_background_memory_updates_only_its_own_tool_evidence(store):
    manager = AsyncMock(return_value={"kind": "fact", "name": "검수", "value": "HX-7031"})
    engine = Engine(Settings("test"), store, SimpleNamespace(text=manager))
    evidence = {"steer:0": {"tool": "remember", "status": "pending"}, "request:0": {"tool": "file"}}
    payload = {"job": "request", "request": "검수 코드 HX-7031을 기억해 줘."}
    with store.db as db:
        db.execute(
            "INSERT INTO jobs(id,scope,epoch,state,request,evidence) VALUES(?,?,1,'done','{}',?)",
            ("request", A.key, json.dumps(evidence)),
        )
        db.execute("INSERT INTO memory_queue(source,scope,payload) VALUES('steer:0',?,?)", (A.key, json.dumps(payload)))
    asyncio.run(engine.drain_memory(A))
    updated = json.loads(engine.job("request")["evidence"])
    assert updated["steer:0"]["status"] == "success" and updated["steer:0"]["changed"]
    assert updated["request:0"] == evidence["request:0"]


@pytest.mark.parametrize("change_workload", [False, True])
def test_steer_inherits_each_targets_effort_unless_the_task_changes(store, change_workload):
    instruction = "난도를 낮춰 간단히 답해줘." if change_workload else "기존 수준을 유지하고 끝에 DONE을 붙여줘."
    plan = dict(
        relation="update",
        targets=["one", "two"],
        replaces=[],
        role="everyday",
        effort="low",
        delivery={"workload": "short", "initial": "수정하겠습니다."},
        question="",
        unsupported="",
        partial=False,
        verbatim_value=False,
        calls=[],
        preferences=[],
        language="ko",
        storage_instruction="",
        new_reasoning_task=instruction if change_workload else "",
    )
    engine = Engine(Settings("test"), store, SimpleNamespace(text=AsyncMock(return_value=plan)))
    routes = {"one": ("reasoning", "high"), "two": ("vision", "medium")}
    for key, (role, effort) in routes.items():
        payload = {**asdict(Request(key, "진행 중인 요청")), "plan": {"role": role, "effort": effort, "calls": []}}
        store.db.execute(
            "INSERT INTO jobs(id,scope,epoch,state,request) VALUES(?,?,1,'running',?)",
            (key, A.key, json.dumps(payload)),
        )
        engine.steers[key] = [asyncio.Queue(), (role, effort), 0, None]
    asyncio.run(engine.submit(A, Request("next", instruction), Output(AsyncMock(return_value="ack"), None, None)))
    for key, previous in routes.items():
        update = json.loads(engine.job(key)["updates"])[0]["plan"]
        assert (update["role"], update["effort"]) == (("everyday", "low") if change_workload else previous)
        assert engine.steers[key][0].empty() == change_workload


def test_memory_update_is_idempotent_and_scoped(store):
    store.save_memory(A, "one", "fact", "배포일", "금요일")
    store.save_memory(A, "two", "fact", "배포일", "월요일")
    store.save_memory(A, "one", "fact", "배포일", "금요일")
    assert [(r["name"], r["value"]) for r in store.memories(A)] == [("배포일", "월요일")]
    assert not store.memories(B)


def test_high_risk_approval_binds_user_and_snapshot(store):
    store.save_memory(A, "first", "fact", "날짜", "월요일")
    ticket = store.request_clear(A, "clear")
    assert not store.approve_clear(B, ticket)
    store.save_memory(A, "late", "fact", "이름", "제다")
    assert not store.approve_clear(A, ticket)
    assert len(store.memories(A)) == 2
    current = store.request_clear(A, "again")
    assert store.approve_clear(A, current)
    assert not store.approve_clear(A, current)
    assert not store.memories(A)


def test_legacy_database_is_never_migrated(tmp_path):
    path = tmp_path / "old.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE tasks(id INTEGER)")
    with pytest.raises(ValueError, match="기존"):
        JedaStore(path)
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT name FROM sqlite_master").fetchall() == [("tasks",)]


@pytest.mark.parametrize(
    "message,expected",
    [
        ("여기서 보이는 내 기억을 전부 삭제해줘.", True),
        ("이 채널의 내 기억을 모두 지워줘.", True),
        ("이 채널에서 조회할 수 있는 내 메모리를 전부 삭제해줘.", True),
        ("내 기억을 모두 삭제하지 마.", False),
        ("이 채널의 다른 사람 기억을 모두 지워줘.", False),
        ("전체 기억 중 포장 코드만 삭제해줘.", False),
        ("내 기억을 모두 지워줘라는 말을 영어로 번역해줘.", False),
        ("기억을 모두 삭제할 수 있어?", False),
    ],
)
def test_whole_scope_command_matches_only_unqualified_requests(message, expected):
    assert requests_all_memories(message) is expected


@pytest.mark.parametrize(
    "message,success",
    [
        ("이 채널의 내 기억을 모두 지워줘.", False),
        ("기억 중 기존 공구함 코드만 지워줘.", True),
    ],
)
def test_pending_snapshot_respects_original_deletion_scope(store, message, success):
    old = store.save_memory(A, "one", "fact", "공구함", "TL-391")
    store.db.execute(
        "INSERT INTO inbox(id,scope,request) VALUES(?,?,?)", ("clear", A.key, json.dumps({"text": message}))
    )
    ticket = store.request_clear(A, "clear:0", ids=[old])
    store.save_memory(A, "late", "fact", "광학", "OP-109")
    assert store.approve_clear(A, ticket) is success
    assert {row["value"] for row in store.memories(A)} == ({"OP-109"} if success else {"TL-391", "OP-109"})
    assert not store.approve_clear(A, ticket)


@pytest.mark.parametrize(
    "message,answer,expected",
    [
        ("최종 한도 숫자만.", "13시간", "13"),
        ("최종 한도 숫자만.", "**13**시간입니다.", "13"),
        ("숫자만.", "-1.25", "-1.25"),
        ("몇 시간인지 알려줘.", "13시간", "13시간"),
        ("두 값의 범위 숫자만.", "12–13", "12–13"),
        ("숫자만.", "자료가 없습니다.", "자료가 없습니다."),
    ],
)
def test_number_only_format_preserves_other_responses(message, answer, expected):
    assert format_numeric_answer(message, answer) == expected


def test_unsupported_only_mentions_name_without_model_or_download(store):
    engine = Engine(None, store, None)
    names = ["발표.PPT", "명세.hwp", "예산.xls", "정리.doc", "archive.rar"]
    refs = [dict(id=str(i), name=name) for i, name in enumerate(names)]
    req = Request("bad", "", refs)
    output = Output(AsyncMock(return_value="notice"), AsyncMock(), None)
    asyncio.run(engine.submit(A, req, output))
    asyncio.run(engine.submit(A, req, output))
    output.send.assert_awaited_once()
    kind, text, _ = output.send.await_args.args
    assert kind == "final" and "Jeda가 처리할 수 없" in text and all(name in text for name in names)
    output.load.assert_not_awaited()


def test_unsupported_attachment_does_not_discard_separate_question(store):
    plan = dict(
        relation="new",
        targets=[],
        replaces=[],
        role="everyday",
        effort="low",
        delivery={"direct": "short"},
        question="",
        unsupported="RAR 파일은 읽을 수 없습니다.",
        partial=False,
        verbatim_value=False,
        calls=[],
        preferences=[],
        language="ko",
        storage_instruction="",
    )
    model = SimpleNamespace(text=AsyncMock(side_effect=[plan, "31입니다."]))
    engine = Engine(Settings("test"), store, model)
    output = Output(AsyncMock(return_value="sent"), AsyncMock(), None)
    req = Request("mixed", "첨부도 읽고, 12 더하기 19도 알려줘.", [{"id": "a", "name": "archive.rar"}])
    asyncio.run(engine.submit(A, req, output))
    kind, text, _ = output.send.await_args.args
    assert kind == "final" and "archive.rar" in text and "31입니다." in text
    output.load.assert_not_awaited()


def test_weather_clarification_completes_an_empty_tool_plan(store):
    base = dict(
        relation="new",
        targets=[],
        replaces=[],
        role="everyday",
        effort="none",
        delivery={"direct": "short"},
        question="",
        unsupported="",
        partial=False,
        verbatim_value=False,
        calls=[],
        preferences=[],
        language="ko",
        storage_instruction="",
    )
    question = "어느 지역의 예보를 확인할까요?"
    forecast = "원주시 내일 오전 강수 확률 예보"
    model = SimpleNamespace(
        text=AsyncMock(
            side_effect=[
                dict(base, question=question),
                dict(base, followup={"action": "web", "intent": forecast, "sources": []}),
            ]
        ),
        discover=AsyncMock(
            return_value={
                "output": [
                    {"type": "web_search_call", "status": "completed", "action": {"sources": ["oai-weather"]}},
                    {"type": "message", "content": [{"type": "output_text", "text": "예보 결과", "annotations": []}]},
                ]
            }
        ),
        compose=AsyncMock(return_value=("예보 결과 (oai-weather)", None)),
    )
    engine = Engine(Settings("test"), store, model)
    out = Output(AsyncMock(side_effect=["m1", "m2", "m3"]), None, None)
    asyncio.run(engine.submit(A, Request("ask", "내일 오전 비 올까?"), out))
    epoch = store.session(A)["epoch"]
    assert store.last_clarification(B, epoch, "new") is None
    asyncio.run(engine.submit(A, Request("city", "원주 ㄱㄱ"), out))
    args = model.text.await_args_list[1]
    assert json.loads(args.args[3])["clarification"] == {"request": "내일 오전 비 올까?", "question": question}
    assert "followup" in args.kwargs["schema"]["required"]
    assert forecast == json.loads(model.discover.await_args.args[3])["task"]["question"]
    model.compose.assert_awaited_once()
    assert store.last_clarification(A, epoch, "next") is None


def test_router_keeps_all_unsummarized_messages_in_sequence(store):
    store.record(A, "covered", "user", "이전 요약에 포함됨")
    cutoff = store.history(A)[0]["seq"]
    with store.db:
        store.db.execute("UPDATE sessions SET summary=?, summarized=? WHERE scope=?", ("이전 요약", cutoff, A.key))
    content = [f"{i} " + "가나다 " * 14 for i in range(140)]
    for i, value in enumerate(content):
        store.record(A, str(i), "assistant" if i % 2 else "user", value)
    store.record(B, "other", "user", "다른 사용자")
    req = Request("current", "다시 확인해봐")
    store.record(A, req.id, "user", req.text)
    ctx = build_context(store, A, req)
    assert ctx["summary"] == "이전 요약"
    assert [r["text"] for r in ctx["recent"]] == content
    assert ctx["current"]["text"] == req.text


@pytest.mark.parametrize("question", ["이 서버 이름 뭐야?", "이 채팅창 이름 뭐야?", "내 이름이 뭐야?"])
def test_discord_names_reach_router_and_final_context(store, question):
    names = {"server": "테스트 서버", "channel": "개발-질문", "user_display_name": "moun?"}
    request = Request("message", question, discord_names=names)
    engine = Engine(None, store, None)
    engine.register(A, request)
    stored = store.db.execute("SELECT request FROM inbox WHERE id=?", (request.id,)).fetchone()
    restored = Request(**json.loads(stored[0]))
    assert build_context(store, A, request)["current"]["discord_names"] == names
    assert build_context(store, A, restored, final=True)["current"]["discord_names"] == names
    legacy = Request(**{"id": "old", "text": question})
    assert "discord_names" not in build_context(store, A, legacy)["current"]


def test_name_confirmation_sends_exact_discord_value_despite_previous_typo(store):
    store.record(A, "earlier", "assistant", "표시 이름은 𝐦𝐨𝐮?입니다.")
    request = Request("confirm", "내 이름이 그게 확실한가", discord_names={"user_display_name": "𝐦𝐨𝐮𝐧?"})
    plan = dict(
        relation="new",
        targets=[],
        replaces=[],
        role="everyday",
        effort="none",
        delivery={"direct": "short"},
        question="",
        unsupported="",
        partial=False,
        verbatim_value=False,
        calls=[],
        preferences=[],
        language="ko",
        storage_instruction="",
        discord_name_reply=[{"prefix": "표시 이름은 ", "field": "user_display_name", "suffix": "입니다."}],
    )
    model = SimpleNamespace(text=AsyncMock(return_value=plan))
    engine = Engine(Settings("test"), store, model)
    send = AsyncMock(return_value="response")
    asyncio.run(engine.submit(A, request, Output(send, None, None)))
    assert send.await_args.args[:2] == ("final", "표시 이름은 𝐦𝐨𝐮𝐧?입니다.")
    history = build_context(store, A, Request("next", "확인"))["recent"]
    assert [entry["text"] for entry in history] == ["표시 이름은 𝐦𝐨𝐮?입니다.", request.text, "표시 이름은 𝐦𝐨𝐮𝐧?입니다."]
    model.text.assert_awaited_once()


def test_router_uses_summary_boundary_after_compression(store):
    model = SimpleNamespace(text=AsyncMock(return_value="앞부분 요약"))
    engine = Engine(Settings("test"), store, model)
    req = Request("next", "그다음은?")
    content = [f"문단 {i} " + " 토큰" * 500 for i in range(10)]
    for i, value in enumerate(content):
        store.record(A, str(i), "user", value)
    assert [r["text"] for r in build_context(store, A, req)["recent"]] == content
    asyncio.run(engine.compress(A))
    ctx = build_context(store, A, req)
    assert ctx["summary"] == "앞부분 요약"
    assert 0 < len(ctx["recent"]) < len(content)
    assert [r["text"] for r in ctx["recent"]] == content[-len(ctx["recent"]) :]
    assert len(store.history(A)) == len(content)


def test_completed_reply_maps_displayed_order_and_checks_scope(store):
    from assistant_bot.followups import followup_issue, selected_work, work_index

    files = [{"id": "first", "name": "alpha.pdf"}, {"id": "second", "name": "zeta.pdf"}]
    req = {**asdict(Request("old", "파일명 역순", files)), "plan": {"calls": []}}
    store.db.execute(
        "INSERT INTO jobs(id,scope,epoch,state,request,answer,sent) VALUES(?,?,1,'done',?,?,?)",
        ("old", A.key, json.dumps(req), "1. zeta.pdf\n2. alpha.pdf", '[{"msg":"reply"}]'),
    )
    work = work_index(store, A, store.session(A), "reply")
    assert work[0]["replied_to"] and work[0]["displayed_file_numbers"]["2"] == "first"
    assert work[0]["execution"] == "not_attempted"
    assert work_index(store, B, store.session(B), "reply") == []
    assert selected_work(store, B, 1, ["old"]) == []
    ctx = {"work": work, "current": {"attachments": [], "reply": None}, "recent_files": [], "memory_index": []}
    plan = {
        "followup": {
            "action": "file",
            "intent": "목록의 두 번째 파일 읽기",
            "sources": ["old"],
            "displayed_file_number": 2,
        },
        "calls": [{"name": "file", "target": "second"}],
        "question": "",
    }
    assert followup_issue(plan, ctx)
    plan["calls"][0]["target"] = "first"
    assert not followup_issue(plan, ctx)
    store.reset_session(A)
    assert not work_index(store, A, store.session(A), "reply")


@pytest.mark.parametrize("tool", ["web", "file", "remember", "forget", "clear", "restore", "reset", "session_style"])
def test_reuse_cannot_trigger_another_operation(tool):
    from assistant_bot.followups import followup_issue

    plan = {"followup": {"action": "reuse"}, "calls": [{"name": tool}], "web_query": ""}
    assert followup_issue(plan, {})
