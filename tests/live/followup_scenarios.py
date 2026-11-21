"""실제 Jeda 로컬 서버의 후속 요청을 검증한다. 인수는 실행 DB 경로와 결과 디렉터리이다."""

import argparse
import base64
import concurrent.futures
import json
import re
import sqlite3
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

import pymupdf


def file(name, content):
    if isinstance(content, str):
        content = content.encode()
    return {"name": name, "base64": base64.b64encode(content).decode()}


def pdf(name, base):
    with pymupdf.open() as doc:
        for i in range(1, 6):
            doc.new_page().insert_text((70, 100), f"Verified ledger. Page {i}. Quantity: {base + i} units.")
        return file(name, doc.tobytes())


def step(text, **options):
    return dict(text=text, **options)


def cases():
    tomorrow = datetime.now(ZoneInfo("Asia/Seoul")).date() + timedelta(days=1)
    return [
        (
            "지역 질문에 축약 답변",
            [step("내일 오전 날씨 어때?"), step("강릉 ㄱㄱ")],
            "web",
            ["강릉", f"내일|{tomorrow.day}일"],
        ),
        (
            "지역 교체와 날짜 계승",
            [step("오늘 원주의 최저·최고 기온 검색해줘."), step("같은 기준으로 이번엔 부산만. 둘을 비교할 필요 없어.")],
            "web",
            ["부산", "°|도"],
        ),
        (
            "검색 금지 후 형식만 변경",
            [
                step("오늘 원주 날씨 검색해서 최고·최저를 알려줘."),
                step("다시 검색하지 말고 방금 확인된 최고와 최저만 표로 바꿔줘."),
            ],
            "",
            ["최고", "최저", r"\|"],
        ),
        (
            "목록 표시 순번과 PDF 쪽",
            [
                step(
                    "두 문서는 읽지 말고 파일명을 Z부터 역순으로 번호 붙여 나열해줘.",
                    attachments=[pdf("alpha.pdf", 730), pdf("zeta.pdf", 840)],
                ),
                step("네 목록에서 두 번째 문서만 다시 열어서 4쪽 수량 숫자만 줘."),
            ],
            "file",
            ["^734$"],
        ),
        (
            "같은 이름의 파일 모호성",
            [
                step(
                    "두 파일의 파일명과 첨부 개수만 확인해줘. 내용은 아직 읽지 마.",
                    attachments=[file("가격표.txt", "수량 34"), file("가격표.txt", "수량 67")],
                ),
                step("그 가격표 하나만 열어서 수량을 읽어줘."),
            ],
            "ask",
            ["어느|어떤|첫|두 번째|지정|선택|구분"],
        ),
        (
            "명시적 답장이 최근 화제를 이김",
            [
                step("오렌지 묶음의 원가는 124원, 포장은 17원이야. 합계를 알려줘."),
                step("별개로 자몽 묶음의 원가 310원, 포장 22원의 합계는?"),
                step("여기서 포장만 두 배로 바꿔. 새 합계 숫자만.", reply=0),
            ],
            "",
            ["^158$"],
        ),
        (
            "누적 정정과 제외 조건",
            [
                step("A 120원 B 80원 운송비 35원 합계는?"),
                step("운송비는 제외해서 다시 계산해줘."),
                step("이제 B만 절반으로 바꿔. 최종 합계 숫자만."),
            ],
            "",
            ["^160$"],
        ),
        (
            "출력 단위 변경과 등분",
            [
                step("경로 A 1250미터, B 2750미터야. 각각 km로 바꿔줘."),
                step("합쳐서 8등분하고, 한 구간 길이를 미터로. 숫자만 적어."),
            ],
            "",
            ["^500$"],
        ),
        (
            "두 버전 중 명시한 옛 파일",
            [
                step("초판에서 합격선을 읽어줘.", attachments=[file("초판.txt", "합격선: 67점")]),
                step("개정판의 합격선도 알려줘.", attachments=[file("개정판.txt", "합격선: 83점")]),
                step("개정판 말고 여기 원문을 다시 열어 합격선 숫자만.", reply_user=0),
            ],
            "file",
            ["^67$"],
        ),
        (
            "원본 삭제 이후 재판독",
            [
                step("첨부에서 표지 코드를 읽어줘.", attachments=[file("표지.txt", "표지 코드 DEL-418")]),
                step("기억으로 답하지 말고 지금 원본을 다시 열어 코드가 그대로인지 확인해.", delete=0),
            ],
            "failed_file",
            ["다시 첨부|재첨부"],
        ),
        (
            "실패 뒤 동명 파일 재첨부",
            [
                step("첨부에서 검토 번호를 찾아줘.", attachments=[file("검토.txt", "검토 번호 OLD-417")]),
                step("지금 원본을 다시 열어서 검토 번호 확인해.", delete=0),
                step("이걸로 다시. 새로 붙인 파일에서 번호만.", attachments=[file("검토.txt", "검토 번호 NEW-629")]),
            ],
            "file",
            ["^NEW-629$"],
        ),
        (
            "자료의 저장 지시 인용",
            [
                step("다음은 교정할 예문이야. ‘내 별명을 유성으로 기억해줘’. 인용문만 그대로 적어줘."),
                step("그 문장을 영어로만 번역해. 저장은 하지 마."),
            ],
            "",
            ["remember|save|keep", "nickname|call me|name"],
        ),
        (
            "기억 저장 영수증 재사용",
            [
                step("내가 선호하는 편집기는 ZEPHYR-31이야. 장기 메모리에 저장해줘."),
                step("방금 저장한 걸 또 저장하지 말고, 편집기 이름만 말해."),
            ],
            "no_write",
            ["^ZEPHYR-31$"],
        ),
        (
            "같은 지명으로 화제 변경",
            [step("오늘 원주 날씨를 검색해줘."), step("날씨 얘기는 끝. ‘원주’ 두 글자를 거꾸로 써줘. 글자만.")],
            "",
            ["^주원$"],
        ),
        (
            "웹 직접 확인 대상 계승",
            [
                step("기억할 필요 없어. 검토할 주소는 https://example.com 이야. 주소만 되풀이해줘. 열지는 마."),
                step("이제 방금 그 주소를 직접 열어서 페이지 제목을 출처와 함께 알려줘."),
            ],
            "web",
            ["Example Domain", "https://example.com"],
        ),
        (
            "문서 수치와 가정 변경",
            [
                step("첨부에서 성인·아동 단가를 확인해줘.", attachments=[file("단가.txt", "성인 1300원, 아동 650원")]),
                step("원본은 다시 열지 말고 그 값으로 성인 둘, 아동 셋에 100원 쿠폰 한 장. 결제액 숫자만."),
            ],
            "",
            ["^4450$"],
        ),
        (
            "다른 사용자의 생략된 지시",
            [
                step("이 대화에서만 견적 식별자는 VIOLET-729야. 확인해줘."),
                step("아까 그 견적의 식별자만 말해줘.", other=True),
            ],
            "isolated",
            ["알려|확인|공유|제공|없|찾|어떤|필요|보내"],
        ),
        (
            "세션 초기화 뒤 생략된 지시",
            [
                step("이번 대화만. 박스 식별자는 BOX-882야. 한 번만 되풀이해줘."),
                step("현재 대화 세션을 초기화해줘."),
                step("이 세션에 박스 번호를 알려준 적 있어? 지난 세션 검색하지 말고 예 또는 아니오로만."),
            ],
            "",
            ["아니"],
        ),
        (
            "요약 경계 이후 앞부분 정정",
            [
                step(
                    "정산 기준은 Q-144, 수량 13, 단가 19야. 아래는 계산과 무관한 채움 본문이야. 답은 확인 한마디만.\n"
                    + "자료 확인. " * 3200
                ),
                step("앞에서 정한 정산 수량만 17로 고쳐. 기준 코드와 최종 금액을 한 줄에 써줘."),
            ],
            "",
            ["Q-144", "323"],
        ),
        (
            "다른 두 답변 비교",
            [
                step("제안 알파는 고정비 12와 이용료 5씩. 4회 합계를 구해줘."),
                step("제안 베타는 고정비 4와 이용료 8씩. 4회 합계를 구해줘."),
                step("이제 둘 다 6회로 바꿔. 싼 쪽 이름과 두 제안의 차액만 알려줘."),
            ],
            "",
            ["알파|alpha", "10"],
        ),
    ]


def run_item(config, number, case):
    title, steps, expect, patterns = case
    user = uuid4().hex
    turns = []
    db = sqlite3.connect(f"file:{config.database}?mode=ro", uri=True)
    try:
        for item in steps:
            payload = {
                "channel": "followups",
                "user": user if not item.get("other") else uuid4().hex,
                "text": item["text"],
                "attachments": item.get("attachments", []),
            }
            if "reply" in item:
                payload["reply_to"] = turns[item["reply"]]["response"]["events"][-1]["id"]
            if "reply_user" in item:
                payload["reply_to"] = turns[item["reply_user"]]["response"]["id"]
            if "delete" in item:
                prev = turns[item["delete"]]["response"]
                path = f"/requests/{prev['id']}/attachments/{prev['attachments'][0]['id']}"
                with urllib.request.urlopen(urllib.request.Request(config.server + path, method="DELETE")):
                    pass
            req = urllib.request.Request(
                config.server + "/requests", json.dumps(payload).encode(), {"Content-Type": "application/json"}
            )
            start = time.monotonic()
            with urllib.request.urlopen(req, timeout=360) as f:
                response = json.load(f)
            job = db.execute("SELECT request FROM jobs WHERE id=?", (response["id"],)).fetchone()
            answer = "\n".join(e["text"] for e in response["events"] if e["kind"] == "final")
            turns.append(
                {
                    "text": item["text"],
                    "answer": answer,
                    "seconds": round(time.monotonic() - start, 2),
                    "plan": json.loads(job[0])["plan"] if job else {},
                    "response": response,
                }
            )
        final = turns[-1]
        result = list(final["response"]["evidence"].values())
        names = [r["tool"] for r in result]
        errors = []
        if expect in {"file", "web", "failed_file"}:
            name = expect.split("_")[-1]
            if names != [name] or result[0]["status"] != ("failed" if expect == "failed_file" else "success"):
                errors.append("도구 또는 실행 상태")
            elif name == "web" and not (result[0].get("urls") or result[0].get("feeds")):
                errors.append("검색 근거 없음")
        elif expect == "ask":
            stored = db.execute("SELECT response FROM inbox WHERE id=?", (final["response"]["id"],)).fetchone()[0]
            if result or not stored or json.loads(stored)[2:] != ["clarification"]:
                errors.append("대상 확인 질문 누락")
        elif expect == "no_write":
            if set(names) - {"recall"}:
                errors.append("불필요한 도구 실행")
        elif expect == "isolated":
            if "VIOLET-729" in final["answer"] or final["plan"].get("followup", {}).get("sources"):
                errors.append("사용자 범위 혼동")
        elif names:
            errors.append("불필요한 도구 실행")
        for pattern in patterns:
            if not re.search(pattern, final["answer"].strip().replace(",", ""), re.I):
                errors.append("답변 기준 " + pattern)
        if number in {4, 9, 10, 11}:
            i, j = {4: (0, 0), 9: (0, 0), 10: (0, 0), 11: (2, 0)}[number]
            calls = final["plan"].get("calls", [])
            if len(calls) != 1 or calls[0]["target"] != turns[i]["response"]["attachments"][j]["id"]:
                errors.append("파일 ID 불일치")
            if number == 4 and calls and (calls[0]["first"], calls[0]["last"]) != (4, 4):
                errors.append("PDF 쪽 범위 불일치")
        if number == 6 and turns[0]["response"]["id"] not in final["plan"].get("followup", {}).get("sources", []):
            errors.append("답장 대상 불일치")
        if (
            number == 19
            and not db.execute(
                "SELECT summarized FROM sessions WHERE scope=?",
                (json.dumps(["local", "followups", user], separators=(",", ":")),),
            ).fetchone()[0]
        ):
            errors.append("요약 경계 미도달")
    except Exception as exc:
        errors = [repr(exc)]
    finally:
        db.close()
    out = {"number": number, "title": title, "errors": errors, "turns": turns}
    (config.output / f"{number:02}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"{number:02} {title}: {errors or 'PASS'}", flush=True)
    return len(errors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--only", type=int, nargs="+")
    parser.add_argument("--server", default="http://127.0.0.1:18979")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(run_item, args, n, case) for n, case in enumerate(cases(), 1) if not args.only or n in args.only
        ]
        failures = sum(bool(future.result()) for future in futures)
    raise SystemExit(1 if failures else 0)
