"""사용자가 검토 후 실행하는 실서버·실모델 시나리오. mocks나 Discord 토큰을 사용하지 않는다."""

from __future__ import annotations

import base64
import json
import os
import re
import time
from urllib.request import Request, urlopen
from uuid import uuid4

import pytest

pytestmark = pytest.mark.skipif(os.getenv("JEDA_LIVE_TESTS") != "1", reason="실제 모델 호출은 명시적으로 실행합니다.")
SERVER = os.getenv("JEDA_TEST_SERVER", "http://127.0.0.1:8765")


transcript = []


@pytest.fixture(autouse=True)
def record_api_exchange(record_property):
    transcript.clear()
    yield
    record_property("jeda_api", json.dumps(transcript, ensure_ascii=False))


def http(path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(SERVER + path, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=300) as response:
        result = json.load(response)
    if body is not None or result["state"] in {"done", "cancelled"}:
        transcript.append({"prompt": body.get("text") if body else None, "result": result})
    return result


def turn(text, *, user=None, **kwargs):
    return http("/requests", {"user": user or uuid4().hex, "text": text, **kwargs})


def answer(result):
    finals = [e["text"] for e in result["events"] if e["kind"] == "final"]
    assert finals, result
    return "\n".join(finals)


def results(result, tool):
    deadline = time.monotonic() + 90
    while True:
        records = [e for e in result["evidence"].values() if e["tool"] == tool]
        if tool != "remember" or not any(e.get("status") == "pending" for e in records):
            return records
        assert time.monotonic() < deadline, "백그라운드 메모리 요청이 완료되지 않음"
        time.sleep(0.25)
        result = http("/requests/" + result["id"])


def attach(name, data):
    return {"name": name, "base64": base64.b64encode(data).decode()}


def test_simple_request_has_one_final_message():
    r = turn("3 더하기 8은? 숫자만 답해줘")
    assert "11" in answer(r)
    assert [e["kind"] for e in r["events"]] == ["final"]


@pytest.mark.parametrize(
    "prompt",
    [
        "내일 오후 3시에 나에게 DM 알림을 예약해줘",
        "내 할 일 목록에 장보기 추가해줘",
        "어제 내가 한 대화의 원문 기록을 영구 삭제해줘",
    ],
)
def test_removed_actions_never_claim_success(prompt):
    r = turn(prompt)
    text = answer(r)
    assert any(w in text for w in ("없", "미지원", "제공하지", "지원하지", "지원되지 않", "어렵", "불가")), text
    assert not any(item.get("changed") for item in r["evidence"].values())


def test_unseen_attachment_is_not_summarized():
    r = turn("첨부했다고 생각한 PDF에서 납기일이 언제인지 알려줘. 파일을 아직 안 올렸어.")
    text = answer(r)
    assert any(w in text for w in ("첨부", "파일", "올려", "업로드"))
    assert "2031-09-17" not in text


def test_document_reads_original_with_unique_value():
    secret = "QUARTZ-" + uuid4().hex[:8]
    r = turn(
        "첨부 문서에 실제로 적힌 검수 번호와 날짜를 알려줘.",
        attachments=[attach("invoice.txt", f"검수 번호 {secret}\n검수일 2031-09-17".encode())],
    )
    assert results(r, "file"), r
    assert secret in answer(r) and "2031" in answer(r)
    assert not results(r, "web") and not results(r, "remember_file")
    assert r["events"][0]["kind"] == "ack"


def test_pdf_specific_chapter_and_visual():
    import fitz

    with fitz.open() as doc:
        for chapter, tag in [(3, "WRONG-RED"), (4, "QUARTZ-77"), (5, "WRONG-GREEN")]:
            page = doc.new_page()
            page.insert_text((40, 50), f"Chapter {chapter} / verification code {tag}")
            if chapter == 4:
                page.draw_line((30, 160), (130, 90))
        doc.set_toc([[1, "Chapter 3", 1], [1, "Chapter 4", 2], [1, "Chapter 5", 3]])
        data = doc.tobytes()
    r = turn(
        "PDF 4장에 나온 검수 코드와 선의 방향을 읽고 원본 쪽수도 알려줘.", attachments=[attach("vector.pdf", data)]
    )
    text = answer(r)
    assert "QUARTZ-77" in text and "WRONG-" not in text
    assert results(r, "file") and any(w in text for w in ("2쪽", "2페이지", "p. 2", "p.2"))
    assert any(w in text for w in ("상승", "오른쪽 위", "우상향", "올라", "높아"))


def test_damaged_pdf_is_not_success():
    r = turn("첨부한 PDF 내용의 합계를 구해줘.", attachments=[attach("broken.pdf", b"%PDF-incomplete")])
    text = answer(r)
    assert any(w in text for w in ("못", "실패", "없", "손상", "어렵", "오류")), text
    assert not any(e.get("changed") for e in r["evidence"].values())


def test_remember_reference_and_followup_read():
    user, tag = uuid4().hex, uuid4().hex[:10]
    saved = turn(
        "이 문서를 나중에 다시 찾게 기억해줘", user=user, attachments=[attach("quote.txt", f"검산 키 {tag}".encode())]
    )
    assert results(saved, "remember_file") and "참조" in answer(saved)
    read = turn("기억한 quote.txt를 다시 열어서 검산 키를 알려줘", user=user)
    evidence = results(read, "file")[-1]
    assert evidence["opened"] and evidence["status"] == "success" and tag in evidence["text"]
    assert tag in answer(read) and not any(word in answer(read) for word in ("열리지 않", "열 수 없", "다시 첨부"))


def test_own_memory_correction_and_cross_user_isolation():
    user, code = uuid4().hex, "P-" + uuid4().hex[:8]
    saved = turn(f"내 프로젝트 출하 코드는 {code}야. 이 사실을 기억해줘.", user=user)
    assert any(e.get("changed") for e in results(saved, "remember"))
    own = turn("내 프로젝트 출하 코드가 뭐였지?", user=user)
    assert code in answer(own)
    outsider = turn("내 프로젝트 출하 코드를 저장된 기억에서 찾아줘")
    assert code not in answer(outsider)


def test_explicit_bulk_approval_bound_to_user():
    user = uuid4().hex
    turn("나는 바닐라 아이스크림을 좋아해. 이걸 기억해줘.", user=user)
    pending = turn("이 채널에서 조회할 수 있는 내 메모리를 전부 삭제해줘.", user=user)
    ticket = re.search(r"승인 ([a-f0-9]{12})", answer(pending)).group(1)
    assert "실행하지 않았" in answer(turn("승인 " + ticket))
    assert "삭제했습니다" in answer(turn("승인 " + ticket, user=user))
    assert "실행하지 않았" in answer(turn("승인 " + ticket, user=user))


def test_web_comparison_uses_citations_and_reply_owner():
    a = turn("Python tomllib에 대해 간단히 설명해줘.")
    r = turn("이거에 대해 공식 웹 문서를 검색해줘.", reply_to=a["id"])
    web = results(r, "web")
    assert web and web[-1].get("urls"), r
    assert any("docs.python.org" in url for url in web[-1]["urls"]), web
    assert any(url in answer(r) for url in web[-1]["urls"])


def test_nonexistent_direct_url_never_claims_reading():
    r = turn("https://example.invalid/jeda-absent 페이지 원문에 적힌 가격을 직접 확인해줘.")
    assert results(r, "web")[-1]["status"] == "failed", r
    assert any(w in answer(r) for w in ("없", "못", "실패", "한도"))


def test_direct_correction_during_an_active_request():
    user = uuid4().hex
    original = turn(
        "문서의 모든 주장을 검토하고 10단계의 자세한 설계를 작성해줘.",
        user=user,
        wait=False,
        attachments=[attach("design.txt", ("프로젝트는 4단계 검수를 거친다.\n" * 100).encode())],
    )
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        state = http("/requests/" + original["id"])
        if state["state"] == "running" and state["events"]:
            break
        assert state["state"] not in {"done", "cancelled"}, "정정 전에 완료되어 동시성 시나리오를 재현하지 못함"
        time.sleep(0.2)
    changed = turn("방금 작성 중인 답을 두 문장으로 바꾸고 맨 끝에 JEDA-END를 적어줘.", user=user)
    assert any(e["kind"] == "ack" for e in changed["events"]), changed
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        state = http("/requests/" + original["id"])
        if state["state"] == "done":
            assert state["revision"] > 0 and "JEDA-END" in answer(state)
            return
        time.sleep(0.5)
    pytest.fail("최신 정정 답변을 전송하지 못함")


def test_image_uses_visual_evidence():
    from io import BytesIO

    from PIL import Image, ImageDraw

    canvas = Image.new("RGB", (420, 220), "white")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((25, 40, 160, 175), fill="red")
    draw.ellipse((230, 40, 365, 175), fill="blue")
    data = BytesIO()
    canvas.save(data, format="PNG")
    r = turn("왼쪽과 오른쪽 도형의 모양과 색을 순서대로 알려줘.", attachments=[attach("sample.png", data.getvalue())])
    text = answer(r)
    assert results(r, "file")[-1]["status"] == "success"
    assert any(w in text for w in ("빨간", "빨강", "붉", "적색"))
    assert any(w in text for w in ("네모", "사각형"))
    assert any(w in text for w in ("파란", "파랑", "청색", "푸른")) and "원" in text


def test_spreadsheet_numeric_total_and_range():
    from io import BytesIO

    from openpyxl import Workbook

    units = [int(uuid4().hex[:4], 16) + 1 for _ in range(3)]
    book = Workbook()
    sheet = book.active
    sheet.title = "검수"
    sheet.append(["항목", "수량"])
    for name, count in zip(("A", "B", "C"), units, strict=True):
        sheet.append([name, count])
    sheet.append(["소계", sum(units)])
    data = BytesIO()
    book.save(data)
    r = turn(
        "검수 시트 B2:B4의 합계를 알려줘. B5 소계는 중복해서 더하지 마.",
        attachments=[attach("items.xlsx", data.getvalue())],
    )
    assert results(r, "file") and str(sum(units)) in answer(r).replace(",", "")
    assert str(2 * sum(units)) not in answer(r).replace(",", "")


def test_slide_specific_marker():
    from io import BytesIO

    from pptx import Presentation
    from pptx.util import Inches

    deck = Presentation()
    tag = "PPT-" + uuid4().hex[:8]
    for marker in ("WRONG-MARKER", tag):
        slide = deck.slides.add_slide(deck.slide_layouts[6])
        slide.shapes.add_textbox(Inches(1), Inches(1), Inches(5), Inches(1)).text = "Verification code " + marker
    data = BytesIO()
    deck.save(data)
    r = turn("2번째 슬라이드의 검수 코드만 알려줘.", attachments=[attach("deck.pptx", data.getvalue())])
    assert results(r, "file") and tag in answer(r) and "WRONG-MARKER" not in answer(r)


def test_deleted_remembered_file_requests_reattachment():
    user = uuid4().hex
    r = turn(
        "나중에 참조할 수 있게 이 파일을 기억해줘.", user=user, attachments=[attach("draft.txt", b"unique: AZ-123")]
    )
    assert results(r, "remember_file")
    with urlopen(
        Request(SERVER + f"/requests/{r['id']}/attachments/{r['attachments'][0]['id']}", method="DELETE"), timeout=15
    ) as response:
        assert response.status == 204
    reread = turn("기억한 draft.txt 원본에서 unique 값을 직접 다시 읽어줘.", user=user)
    assert results(reread, "file")[-1]["status"] == "failed"
    assert "첨부" in answer(reread) and "AZ-123" not in answer(reread)


def test_partial_evidence_never_supplies_missing_total():
    tag = uuid4().hex[:8]
    r = turn(
        "두 견적서의 코드를 읽고 총액을 비교해줘. 확인한 파일과 확인하지 못한 파일을 구분해줘.",
        attachments=[
            attach("known.txt", f"검수코드 {tag}, 합계 27300원".encode()),
            attach("unknown.pdf", b"%PDF-broken"),
        ],
    )
    records = results(r, "file")
    assert {item["status"] for item in records} >= {"success", "failed"}
    text = answer(r)
    assert tag in text and "27300" in text.replace(",", "")
    assert "unknown.pdf" in text and any(w in text for w in ("못", "불가", "없", "손상", "실패"))


def test_weather_uses_current_cited_source():
    r = turn("오늘 서울 날씨를 지금 검색해 줘. 날짜, 기온과 확인한 출처를 함께 알려줘.")
    web = results(r, "web")
    assert web and web[-1]["status"] == "success", r
    assert "서울" in answer(r) and any(source in answer(r) for source in web[-1]["urls"] + web[-1].get("feeds", []))


def test_direct_url_requires_actual_open():
    r = turn("https://docs.python.org/3/library/tomllib.html 페이지를 직접 열고 load와 loads의 차이를 출처와 설명해줘.")
    web = results(r, "web")
    assert web and web[-1]["status"] == "success" and web[-1]["urls"]
    assert "load" in answer(r) and any(url in answer(r) for url in web[-1]["urls"])


def test_memory_update_takes_precedence_and_raw_history_survives_reset():
    user = uuid4().hex
    old, new = ("P-" + uuid4().hex[:8] for _ in range(2))
    saved = turn(f"내 제품 코드는 {old}야. 이 사실을 기억해줘.", user=user)
    edited = turn(f"기억해 둔 내 제품 코드를 {new}로 정정해줘.", user=user)
    assert any(e.get("changed") for e in results(edited, "remember"))
    turn("새 대화 세션을 시작해줘.", user=user)
    recalled = turn("저장된 기억에서 현재 내 제품 코드만 찾아줘.", user=user)
    assert new in answer(recalled) and old not in answer(recalled)
    original = turn(f"예전 대화 원문에서 {old}라는 값이 나왔던 당시 내 발언을 찾아줘.", user=user)
    matches = json.loads(results(original, "history")[-1]["text"])
    assert any(m["id"] == saved["id"] and m["role"] == "user" and old in m["text"] for m in matches)
    assert old in answer(original)


def test_server_restart_recovers_an_accepted_real_request(tmp_path):
    import socket
    import subprocess
    import sys

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    env = dict(os.environ, JEDA_DATABASE_PATH=str(tmp_path / "jeda.sqlite"))

    def launch():
        proc = subprocess.Popen([sys.executable, "-m", "assistant_bot.jeda_server", "--port", str(port)], env=env)
        try:
            until = time.monotonic() + 20
            while time.monotonic() < until and proc.poll() is None:
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                        return proc
                except OSError:
                    time.sleep(0.2)
            pytest.fail("격리된 재시작 검증 서버를 열 수 없음")
        except BaseException:
            proc.terminate()
            proc.wait(timeout=10)
            raise

    def read(path, body=None):
        request = Request(
            url + path, data=json.dumps(body).encode() if body else None, headers={"Content-Type": "application/json"}
        )
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    proc = launch()
    try:
        tag = "RESUME-" + uuid4().hex[:8]
        r = read(
            "/requests",
            {
                "user": "recovery",
                "text": "첨부 문서의 검수 코드와 전체 절차를 자세히 요약해줘.",
                "attachments": [attach("recovery.txt", (tag + "\n" + "검수·검증·인수 절차\n" * 100).encode())],
                "wait": False,
            },
        )
        path = "/requests/" + r["id"]
        until = time.monotonic() + 120
        while time.monotonic() < until:
            r = read(path)
            if r["state"] == "running" and r["events"]:
                break
            assert r["state"] != "done", "재시작 전에 답변이 완성됨"
            time.sleep(0.15)
        assert r["state"] == "running" and r["events"]
        proc.kill()
        proc.wait(timeout=10)
        proc = launch()
        until = time.monotonic() + 240
        while time.monotonic() < until:
            r = read(path)
            if r["state"] == "done":
                break
            time.sleep(0.4)
        assert r["state"] == "done" and tag in answer(r)
        assert sum(e["kind"] == "ack" for e in r["events"]) == 1
        assert len({e["tag"] for e in r["events"]}) == len(r["events"])
    finally:
        proc.terminate()
        proc.wait(timeout=30)


def await_state(key, predicate, timeout=180):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        result = http("/requests/" + key)
        if predicate(result):
            return result
        assert result["state"] not in {"cancelled", "done"}, result
        time.sleep(0.25)
    pytest.fail("지정한 작업 단계에 도달하지 못함")


def test_cancellation_only_affects_requester():
    user = uuid4().hex
    original = turn(
        "첨부 자료 내용을 분석하고 자세한 검증 절차를 설계해줘.",
        user=user,
        wait=False,
        attachments=[attach("long.txt", ("검토 대상은 시트 별 단위 변환과 감사 기록이다.\n" * 120).encode())],
    )
    await_state(original["id"], lambda r: r["state"] == "running" and r["events"])
    outsider = turn("다른 사람이 진행 중인 문서 작업을 취소해줘.")
    assert not any(e.get("changed") for e in outsider["evidence"].values())
    stopped = turn("방금 내가 요청한 문서 분석 작업은 지금 취소해줘.", user=user)
    assert "취소" in answer(stopped)
    state = http("/requests/" + original["id"])
    assert state["state"] == "cancelled" and all(e["kind"] != "final" for e in state["events"])


def test_mixed_supported_and_unavailable_request():
    r = turn("37 더하기 82를 계산하고 그 결과를 내 DM으로 보내줘.")
    text = answer(r)
    assert "119" in text and "DM" in text.upper()
    assert any(w in text for w in ("없", "불가", "어렵", "지원하지", "지원되지 않"))
    assert not any(e.get("changed") for e in r["evidence"].values())


def test_explanation_opens_with_topic_and_action():
    prompt = "토크나이저에 대해 자세하게 설명해줘"
    result = turn(prompt)
    openings = [event["text"] for event in result["events"] if event["kind"] == "ack"]
    assert len(openings) == 1 and result["events"][0]["kind"] == "ack"
    assert "토크나이저" in openings[0] and any(word in openings[0] for word in ("설명", "알려", "살펴", "풀어"))
    assert prompt not in openings[0] and "요청의 조건" not in openings[0]
    assert len(openings[0]) <= 36
    assert "토큰" in answer(result)


def test_advanced_design_and_explicit_detail():
    r = turn(
        "SQLite를 사용하는 Discord 봇의 작업 큐를 설계해줘. 워커가 중간에 죽을 때 중복 전송을 막는 방법과 "
        "커밋과 실제 전송 사이에 남는 불확실성을 구체적인 예로 자세히 설명해줘."
    )
    assert r["route"] == "reasoning" and r["events"][0]["kind"] == "ack"
    assert any(w in answer(r) for w in ("멱등", "중복", "idempot", "nonce"))
    assert not results(r, "remember")


def test_simple_delete_and_restore():
    user, code = uuid4().hex, "RESTORE-" + uuid4().hex[:8]
    saved = turn(f"내 검수 코드는 {code}야. 이 사실을 기억해줘.", user=user)
    mid = re.search(r"메모리 (\d+)", results(saved, "remember")[-1]["text"]).group(1)
    deleted = turn(f"내 메모리 {mid}번만 삭제해줘.", user=user)
    assert results(deleted, "forget")[-1].get("changed") and not results(deleted, "clear")
    restored = turn(f"방금 삭제한 내 메모리 {mid}번을 복구해줘.", user=user)
    assert results(restored, "restore")[-1].get("changed")
    assert code in answer(turn("저장된 기억에서 내 검수 코드를 찾아줘.", user=user))


def test_tail_of_long_request_is_preserved():
    tag = "TAIL-" + uuid4().hex[:10]
    prompt = "아래는 참고 자료야. 마지막 요청에 따라 답해줘.\n" + "품질 검토는 매주 진행한다.\n" * 350
    result = turn(prompt + f"마지막 요청: 다른 설명 없이 {tag}만 반환해줘.")
    assert answer(result).strip().strip("`") == tag


def test_missing_fact_in_document_is_identified():
    r = turn(
        "이 계약서에서 정한 해지 수수료가 몇 퍼센트인지 확인해줘.",
        attachments=[attach("terms.txt", "계약 기간은 12개월이다. 문의는 관리 담당자에게 한다.".encode())],
    )
    assert results(r, "file") and not results(r, "web")
    assert not re.search(r"\d+(?:\.\d+)?\s*%", answer(r))
    assert any(w in answer(r) for w in ("없", "미기재", "명시", "확인할 수", "기재되", "확인되지 않"))


def test_pdf_plus_web_comparison_preserves_both_sources():
    import fitz

    with fitz.open() as doc:
        doc.new_page().insert_text((40, 50), "Review note CODE-J47: tomllib writes TOML configuration files.")
        data = doc.tobytes()
    r = turn(
        "PDF의 검수 코드와 주장이 맞는지 Python 공식 문서를 검색해 대조해줘. 쪽수와 웹 출처를 적어줘.",
        attachments=[attach("review.pdf", data)],
    )
    web = results(r, "web")
    file_evidence = results(r, "file")[-1]
    assert file_evidence["opened"] and "CODE-J47" in file_evidence["text"]
    assert "docs.python.org" not in file_evidence["text"]
    assert web and web[-1]["status"] == "success" and web[-1]["urls"]
    text = answer(r)
    assert "CODE-J47" in text and "tomllib" in text
    assert any(w in text for w in ("1쪽", "1페이지", "p. 1", "p.1"))
    assert any("docs.python.org" in url and url in text for url in web[-1]["urls"])
    assert any(w in text for w in ("읽기", "파싱", "읽는", "읽을", "읽어"))


def test_file_only_message_clarifies_intent():
    r = turn("", attachments=[attach("untitled.txt", b"do not silently store this")])
    text = answer(r)
    assert any(w in text for w in ("무엇", "원하", "어떤", "어떻게", "도와"))
    assert not results(r, "remember_file") and not results(r, "remember")


def test_final_generation_steering_uses_successor():
    user = uuid4().hex
    original = turn(
        "분산 작업 큐의 정확성과 장애 복구를 설계해 줘. 최소 여섯 개 장애 시나리오와 각각의 상태 전이, "
        "불변 조건, 의사 코드를 포함해서 상세하게 작성해줘.",
        user=user,
        wait=False,
    )
    await_state(original["id"], lambda r: r["state"] == "running" and r["generation"] == "websocket")
    updated = turn("지금 설계 중인 그 답의 범위와 추론 수준은 유지하고 마지막 문장만 STEER-DONE으로 끝내줘.", user=user)
    assert any(e["kind"] == "ack" for e in updated["events"])
    state = await_state(original["id"], lambda r: r["state"] == "done", timeout=240)
    assert state["revision"] > 0 and "STEER-DONE" in answer(state)
    assert state["generation"] == "steered", "정정 내용은 반영됐으나 WebSocket 후속 응답은 검증되지 않음"


def test_weather_location_reply_searches_with_evidence():
    user = uuid4().hex
    prompt = turn("오늘 날씨 어때", user=user)
    assert not results(prompt, "web") and any(w in answer(prompt) for w in ("지역", "도시", "위치", "어디"))
    r = turn("원주 ㄱㄱ", user=user)
    records = results(r, "web")
    assert records and records[-1]["status"] == "success", r
    text = answer(r)
    assert "원주" in text and re.search(r"-?\d+\s*(?:°|℃|도)", text), text
    assert any(source in text for source in records[-1]["urls"] + records[-1].get("feeds", []))


def test_follow_repository_to_exact_line():
    user = uuid4().hex
    turn("https://github.com/mounismoun/InvGUI 이 저장소의 목적을 한 문장으로 요약해줘.", user=user)
    result = turn(
        "같은 저장소 커밋 8b1879e3e8beee139eed570fee70d8a8d634f81c의 GuiManager.kt 33번째 줄의 코드와 출처를 보여줘.",
        user=user,
    )
    (web,) = results(result, "web")
    (source,) = [r for r in web["records"] if r["kind"] == "file"]
    assert source["commit"] == "8b1879e3e8beee139eed570fee70d8a8d634f81c" and source["requested_line"] == 33
    assert (
        source["text"].splitlines()[32]
        == source["line_text"]
        == "        if (event.view.topInventory != session.inventory) return"
    )
    assert source["line_text"] in answer(result) and source["url"] in answer(result)
