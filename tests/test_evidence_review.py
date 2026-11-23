"""Discord와 외부 모델 대신 고정된 판독·판단 결과로 실제 작업 흐름을 검증한다."""

import asyncio
import base64
import io
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from PIL import Image

from assistant_bot.followups import selected_work
from assistant_bot.openai_service import Settings
from assistant_bot.runtime import Engine, Output, Request
from assistant_bot.stores import JedaStore, Scope
from assistant_bot.visual_evidence import compare_page, plan_visual_search
from assistant_bot.web_agent import discover, read_page

SCOPE = Scope("guild", "channel", "user")
FILE = {"id": "screen", "name": "screen.txt"}
SOURCE = "https://example.org/manual"
FILE_CALL = dict(name="file", target="screen", query="화면의 오류 코드", first=0, last=0, chapter=0, pdf_mode="full")


def routed(call, allowed):
    return dict(
        relation="new",
        targets=[],
        replaces=[],
        role="everyday",
        effort="low",
        delivery={"direct": "short"},
        question="",
        unsupported="",
        partial=False,
        verbatim_value=False,
        calls=[call.copy()],
        preferences=[],
        language="ko",
        storage_instruction="",
        review_tools=allowed,
    )


def decision(action, query="", **kwargs):
    return (
        dict(
            action=action,
            query=query,
            target="",
            url="",
            first=0,
            last=0,
            chapter=0,
            pdf_mode="full",
            reason="원문 단서를 확인했습니다.",
        )
        | kwargs
    )


@pytest.fixture
def service(tmp_path):
    store = JedaStore(tmp_path / "test.sqlite")
    model = SimpleNamespace(text=AsyncMock(), compose=AsyncMock(return_value=("확인 결과입니다.", None)))
    engine = Engine(Settings("test"), store, model)
    output = Output(
        AsyncMock(return_value="sent"), AsyncMock(return_value=f"ACME E104 {SOURCE} 내부메모".encode()), None
    )
    yield engine, model, output
    store.close()


def test_file_to_web_uses_public_clue_then_reuses_saved_result(service, monkeypatch):
    engine, model, output = service
    model.text.side_effect = [
        routed(FILE_CALL, ["web"]),
        decision("web", "ACME E104 공식 문서", url=SOURCE),
        decision("answer"),
    ]
    web = AsyncMock(return_value={"text": "E104의 원인", "urls": [SOURCE]})
    monkeypatch.setattr("assistant_bot.runtime.collect_web", web)
    asyncio.run(engine.submit(SCOPE, Request("q", "이 오류 원인이 뭐야?", [FILE]), output))
    task = web.await_args.args[2]
    assert task["start_urls"] == [SOURCE] and task["question"] == "ACME E104 공식 문서"
    assert "내부메모" not in json.dumps(task, ensure_ascii=False)
    ctx = json.loads(model.compose.await_args.args[3])
    assert [r["tool"] for r in ctx["results"]] == ["file", "web"]
    job = engine.job("q")
    reviews = json.loads(job["request"])["plan"]["reviews"]
    assert reviews[0]["index"] == 1 and reviews[-1]["action"] == "answer"
    engine.update("q", "state='running'", ())
    asyncio.run(engine.generate(SCOPE, engine.job("q"), output))
    web.assert_awaited_once()
    output.load.assert_awaited_once()
    assert model.text.await_count == 3
    engine.update("q", "evidence=json_set(evidence,?,json(?))", ('$."q:1"', '{"tool":"web","status":"running"}'))
    asyncio.run(engine.generate(SCOPE, engine.job("q"), output))
    web.assert_awaited_once()
    assert json.loads(engine.job("q")["evidence"])["q:1"]["status"] == "partial"


@pytest.mark.parametrize(
    ("text", "pick", "outcome"),
    [
        ("무슨 게임이야?", decision("answer"), "answer"),
        ("이게 무슨 게임이야?", decision("clarify", "타이틀 화면도 보여 주실 수 있나요?"), "clarify"),
        ("장면을 설명해 줘. 검색하지 마.", decision("web", "ACME"), "answer"),
        ("파일을 읽어 줘.", decision("remember", "메모"), "answer"),
        ("파일을 읽어 줘.", decision("file", FILE_CALL["query"], target="screen"), "answer"),
        ("파일을 읽어 줘.", decision("file", "다른 원본", target="invented"), "answer"),
        ("링크를 확인해 줘.", decision("web", "자료", url="https://made-up.invalid"), "answer"),
    ],
)
def test_final_answer_or_clarification_without_extra_call(service, text, pick, outcome):
    engine, model, output = service
    model.text.side_effect = [routed(FILE_CALL, ["web", "file", "remember"]), pick]
    asyncio.run(engine.submit(SCOPE, Request("q", text, [FILE]), output))
    job = engine.job("q")
    assert set(json.loads(job["evidence"])) == {"q:0"}
    assert json.loads(job["request"])["plan"]["review"]["action"] == outcome
    assert job["answer"] == "확인 결과입니다."
    actions = model.text.await_args.kwargs["schema"]["properties"]["action"]["enum"]
    assert "remember" not in actions
    if "검색하지 마" in text:
        assert "web" not in actions
    if outcome == "clarify":
        assert engine.store.last_clarification(SCOPE, job["epoch"], "next")["request"] == text


def test_history_result_can_open_the_matched_attachment(service):
    engine, model, output = service
    for who, mid, ref in [
        (SCOPE, "old", FILE),
        (Scope("guild", "channel", "other"), "other", {"id": "x", "name": "x.txt"}),
    ]:
        engine.register(who, Request(mid, "과거화면", [ref]))
        engine.store.record(who, mid, "user", "과거화면")
    engine.store.reset_session(SCOPE)
    model.text.side_effect = [
        routed(dict(FILE_CALL, name="history", query="과거화면", target=""), ["file"]),
        decision("file", "파일의 오류 코드", target=FILE["id"]),
        decision("answer"),
    ]
    asyncio.run(engine.submit(SCOPE, Request("q", "예전 과거화면 파일에서 오류를 찾아줘"), output))
    output.load.assert_awaited_once_with(FILE)
    reviewed = json.loads(model.text.await_args_list[1].args[3])
    assert reviewed["files"] == {"screen": "screen.txt"}
    assert json.loads(engine.job("q")["evidence"])["q:1"]["opened"]


def test_correction_during_review_discards_stale_decision(service, monkeypatch):
    engine, model, output = service
    plan = routed(FILE_CALL, ["web"])

    async def text(*args, purpose, **kwargs):
        if purpose == "라우팅":
            return plan
        update = dict(id="edit", text="검색하지 마", plan=json.loads(engine.job("q")["request"])["plan"])
        if not json.loads(engine.job("q")["updates"]):
            update["plan"].update(calls=[], review_tools=[], replaces=[])
            engine.update("q", "updates=?,revision=revision+1", (json.dumps([update]),))
            return decision("web", "ACME")
        return decision("answer")

    model.text.side_effect = text
    web = AsyncMock()
    monkeypatch.setattr("assistant_bot.runtime.collect_web", web)
    asyncio.run(engine.submit(SCOPE, Request("q", "이 오류 원인은?", [FILE]), output))
    job = engine.job("q")
    assert "review" not in json.loads(job["request"])["plan"]
    assert json.loads(job["updates"])[0]["plan"]["review"]["action"] == "answer"
    web.assert_not_awaited()
    output.load.assert_awaited_once()


def test_hosted_search_does_not_receive_file_or_history_text():
    model = SimpleNamespace(
        discover=AsyncMock(
            return_value={
                "output": [
                    {"type": "web_search_call", "status": "completed", "action": {"sources": []}},
                ]
            }
        )
    )
    task = {"files": ["내부 첨부 전문"], "question": "사적인 원래 질문", "time": "12:00", "file_urls": [SOURCE]}
    asyncio.run(discover(model, Settings("test"), task, "ACME E104"))
    sent = model.discover.await_args.args[3]
    assert "ACME E104" in sent
    assert all(private not in sent for private in [*task["files"], task["question"], SOURCE])


@pytest.mark.parametrize(
    ("observation", "answer"),
    [
        ("로고에 달빛정원이 보임", decision("answer")),
        (
            "블록형 인물이 있는 골목. 제목이나 UI 글자가 보이지 않음",
            decision("clarify", "타이틀 화면도 보여 주실 수 있나요?"),
        ),
    ],
)
def test_image_reader_keeps_original_question_and_reviews_its_observations(service, observation, answer):
    engine, model, output = service
    picture = io.BytesIO()
    Image.new("RGB", (48, 48), color="blue").save(picture, "PNG")
    output.load.return_value = picture.getvalue()
    question = "이거 무슨 게임인지 알겠어?"
    call = dict(FILE_CALL, query="장면 묘사")
    model.text.side_effect = [
        routed(call, ["file", "web"]),
        {"observed": observation, "unread": ""},
        answer,
    ]
    asyncio.run(engine.submit(SCOPE, Request("q", question, [dict(FILE, name="scene.png")]), output))
    reader, reviewer = model.text.await_args_list[1:]
    assert question in reader.args[3][0]["content"][0]["text"]
    assert call["query"] in reader.args[3][0]["content"][0]["text"]
    assert observation in json.loads(reviewer.args[3])["results"][0]["text"]
    assert len(json.loads(engine.job("q")["evidence"])) == 1


def test_review_failure_keeps_available_evidence(service):
    engine, model, output = service
    model.text.side_effect = [routed(FILE_CALL, ["web"]), TimeoutError()]
    asyncio.run(engine.submit(SCOPE, Request("q", "여기 무슨 오류가 떠?", [FILE]), output))
    ctx = json.loads(model.compose.await_args.args[3])
    assert "E104" in ctx["results"][0]["text"]
    assert engine.job("q")["state"] == "done"


def test_changes_hypothesis_within_budget_and_keeps_prior_searches(service, monkeypatch):
    engine, model, output = service
    checks = []

    async def choose(*args, purpose, schema, **kwargs):
        if purpose == "라우팅":
            return routed(FILE_CALL, ["web"])
        checks.append(json.loads(args[3]))
        if "web" not in schema["properties"]["action"]["enum"]:
            return decision("answer")
        return decision("web", f"공개 자료 대안 {len(checks)}")

    model.text.side_effect = choose

    async def search(models, cfg, task, superseded):
        return {"text": "근거 부족", "status": "partial", "actions": [{"action": "search", "term": task["question"]}]}

    monkeypatch.setattr("assistant_bot.runtime.collect_web", search)
    asyncio.run(engine.submit(SCOPE, Request("q", "기록의 대상을 찾아줘", [FILE]), output))
    assert len(checks) == 4
    assert checks[2]["results"][1]["search_terms"] == ["공개 자료 대안 1"]
    assert len(checks[-1]["previous_reviews"]) == 3
    assert len(json.loads(engine.job("q")["evidence"])) == 4


def test_public_page_candidate_pixels_reach_comparison_with_source():
    picture = io.BytesIO()
    Image.new("RGB", (12, 12), color="green").save(picture, "PNG")
    source = picture.getvalue()
    page_url = "https://example.org/characters"
    image_url = "https://example.org/images/character.png"
    reader = SimpleNamespace(
        get=AsyncMock(
            side_effect=[
                (page_url, "text/html", '<img src="/images/character.png" alt="Aster"><img src="/other.png">Profile'),
                (image_url, "image/png", source),
                ("https://example.org/other.png", "image/png", source),
            ]
        )
    )
    page = asyncio.run(read_page(reader, page_url))
    models = SimpleNamespace(
        text=AsyncMock(side_effect=[{"ids": [0]}, {"candidate": 1, "observations": "윤곽 일치", "name_quote": "Aster"}])
    )
    result = asyncio.run(
        compare_page(models, Settings("test"), reader, page, "누구야?", AsyncMock(return_value=source), lambda: False)
    )
    content = models.text.await_args.args[3][0]["content"]
    assert sum(p["type"] == "input_image" for p in content) == 2
    assert result["match"] == 1 and result["candidates"][0]["url"] == image_url
    assert result["page"] == page_url
    assert result["name"] == "Aster" and result["verification"] == "named_match"
    first = models.text.await_args_list[0].args[3][0]["content"]
    assert sum(p["type"] == "input_image" for p in first) == 2
    reader.get.assert_any_await(image_url, image=True)


def test_visual_pivot_rejects_repeated_candidate_in_new_search_family():
    picture = io.BytesIO()
    Image.new("RGB", (8, 8)).save(picture, "PNG")
    repeated = dict(approach="origin", hypothesis="old item", query="Acme original mascot", seeds=["ACME"])
    fresh = dict(approach="roster", hypothesis="event cast", query="festival mascot cast", seeds=[])
    model = SimpleNamespace(text=AsyncMock(return_value={"options": [repeated, fresh]}))
    history = [
        dict(
            approach="recognition",
            query="Acme blue character",
            seeds=["acme marketplace"],
            subject_box=[0, 0, 500, 1000],
        )
    ]
    task = dict(visual_request="누구야?", question="비슷한 상품 찾기", visual_history=history)
    chosen = asyncio.run(plan_visual_search(model, Settings("test"), task, AsyncMock(return_value=picture.getvalue())))
    assert chosen == fresh | {"subject_box": [0, 0, 500, 1000]}
    sent = model.text.await_args.args[3][0]["content"][1]["image_url"].split(",")[1]
    with Image.open(io.BytesIO(base64.b64decode(sent))) as cropped:
        assert cropped.size == (4, 8)
    choices = model.text.await_args.kwargs["schema"]["properties"]["options"]["items"]["properties"]["approach"]
    assert "recognition" not in choices["enum"]


def test_new_sibling_keeps_parent_and_observations():
    image = io.BytesIO()
    Image.new("RGB", (12, 12)).save(image, "PNG")
    sibling = dict(approach="roster", hypothesis="models", seeds=["Acme", "A200"], query="Acme catalogue A200")
    model = SimpleNamespace(text=AsyncMock(return_value={"options": [sibling]}))
    task = dict(
        visual_request="이 제품은?",
        question="명판에 맞는 다음 모델",
        observations=["흐린 A2 표기"],
        visual_history=[dict(approach="recognition", query="Acme A100 manual", seeds=["acme", "a100"])],
    )
    attempt = asyncio.run(plan_visual_search(model, Settings("test"), task, AsyncMock(return_value=image.getvalue())))
    assert attempt["query"] == sibling["query"]
    payload = json.loads(model.text.await_args.args[3][0]["content"][0]["text"])
    assert (payload["review_question"], payload["observations"]) == (task["question"], task["observations"])


def test_web_only_continuation_resolves_prior_photo_and_legacy_search_trail(service):
    engine, _, _ = service
    pic = dict(FILE, name="machine.png")
    web_call = dict(name="web", question="manufacturer", image_target=pic["id"])
    for key, refs, parents, ev in [
        ("origin", [pic], [], dict(actions=[dict(action="search", term="serial plate")], visited=[SOURCE])),
        ("again", [], ["origin"], dict(visual_attempt=dict(target=pic["id"], approach="roster", query="manuals"))),
    ]:
        plan = dict(identify_image=True, calls=[web_call], followup=dict(sources=parents))
        request = dict(id=key, attachments=refs, text="identify", plan=plan)
        engine.store.db.execute(
            "INSERT INTO jobs(id,scope,epoch,request,state,evidence) VALUES(?,?,1,?,'done',?)",
            (key, SCOPE.key, json.dumps(request), json.dumps({f"{key}:0": ev})),
        )
    jobs = selected_work(engine.store, SCOPE, 1, ["again"])
    assert [j["id"] for j in jobs] == ["again", "origin"]
    assert jobs[-1]["files"] == [pic]
    legacy = jobs[-1]["tools"][0]["visual_attempt"]
    assert legacy["queries"] == ["serial plate"] and legacy["pages"] == [SOURCE]
