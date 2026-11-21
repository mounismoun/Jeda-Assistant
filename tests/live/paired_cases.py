"""50쌍 실API 대조 시험. python tests/live/paired_cases.py OUTPUT --port PORT"""

import asyncio

from extended_suite import main

cases = []


def turn(text, files=None, **kwargs):
    return {"text": text, "files": files or {}, **kwargs}


def pair(title, a, b):
    for side, (expected, turns) in zip("AB", (a, b), strict=True):
        steps = turns if isinstance(turns, list) else [turns]
        cases.append((len(cases) + 1, title + " " + side, expected, steps))


def text_pair(title, a, b):
    pair(title, (a[0], turn(a[1])), (b[0], turn(b[1])))


def files_pair(title, prompt, a, b):
    pair(title, (a[0], turn(prompt, a[1])), (b[0], turn(prompt, b[1])))


text_pair(
    "01 공백과 역순",
    ("MEL", "L E M에서 공백을 빼고 글자 순서를 뒤집어. 결과만."),
    ("MEL", "LEM에서 공백을 빼고 글자 순서를 뒤집어. 결과만."),
)
text_pair(
    "02 시각 표기",
    ("03:25", "UTC 18:25를 서울 시각으로 바꿔 HH:MM만 적어."),
    ("03:25", "UTC 오후 6시 25분을 서울 시각으로 바꿔 HH:MM만 적어."),
)
text_pair(
    "03 경계 포함",
    ("4", "정수 구간 3 이상 7 미만에는 정수가 몇 개야? 숫자만."),
    ("5", "정수 구간 3 이상 7 이하에는 정수가 몇 개야? 숫자만."),
)
text_pair(
    "04 묶음 경계",
    ("7", "한 포대에 12개씩 넣을 수 있다. 84개에 필요한 최소 포대 수만."),
    ("8", "한 포대에 12개씩 넣을 수 있다. 85개에 필요한 최소 포대 수만."),
)
text_pair(
    "05 논리 부정",
    ("수달", "카드 '수달=홀수, 기린=짝수'. 홀수인 동물 이름만."),
    ("기린", "카드 '수달=홀수, 기린=짝수'. 홀수가 아닌 동물 이름만."),
)

text_pair(
    "06 반올림 정책",
    ("12", "12.5원을 가장 가까운 정수로 반올림한다. 정확히 절반이면 짝수로. 최종 금액 숫자만."),
    ("13", "12.5원을 가장 가까운 정수로 반올림한다. 정확히 절반이면 큰 정수로. 최종 금액 숫자만."),
)
text_pair(
    "07 수율 단위",
    (
        "180",
        "250개 부품 중 두 단계의 통과율은 각각 90%, 80%다. 2단계 통과율 분모는 1단계 통과품이다. 최종 통과품 수만.",
    ),
    ("200", "250개 부품 중 두 단계의 통과율은 각각 90%, 80%다. 2단계 통과율 분모는 최초 투입량이다. 최종 통과품 수만."),
)
text_pair(
    "08 집합 교집합",
    ("6", "직원 20명 중 A 교육 14명, B 교육 12명. 모두 적어도 하나 수강. 둘 다 수강한 인원만."),
    ("8", "직원 20명 중 A 교육 14명, B 교육 12명. 아무것도 안 들은 사람은 2명. 둘 다 수강한 인원만."),
)
text_pair(
    "09 예약의 끝점",
    ("1", "회의실 예약 [10:00,11:00), [11:00,12:00). 끝 시각은 제외된다. 동시에 필요한 최대 방 수만."),
    ("2", "회의실 예약 [10:00,11:01), [11:00,12:00). 끝 시각은 제외된다. 동시에 필요한 최대 방 수만."),
)
text_pair(
    "10 정액·정률 순서",
    ("80", "105원에 5원 차감 후 20% 차감. 최종가 숫자만."),
    ("79", "105원에 20% 차감 후 5원 차감. 최종가 숫자만."),
)
text_pair(
    "11 사전식 정렬",
    ("v2.10", "v2.9, v2.10 중 점으로 나눈 정수 버전 순서에서 더 뒤인 버전만."),
    ("v2.9", "v2.9, v2.10 중 ASCII 문자열 사전 순서에서 더 뒤인 버전만."),
)
text_pair(
    "12 윤년 예외",
    ("2", "그레고리력 1900년 2월 28일 00시부터 3월 2일 00시까지 경과 일수만."),
    ("3", "그레고리력 2000년 2월 28일 00시부터 3월 2일 00시까지 경과 일수만."),
)

files_pair(
    "13 TSV 열 재배치",
    "행 ID가 J6인 행의 봉인값만.",
    ("QV-45", {"dock.tsv": "ID\t봉인\t비고\nJ6\tQV-45\tQV-54\nJ9\tQT-88\tQV-54"}),
    ("QV-45", {"dock.tsv": "비고\tID\t봉인\nQV-54\tJ6\tQV-45\nQV-54\tJ9\tQT-88"}),
)
files_pair(
    "14 JSON 배열 순서",
    "첨부에서 primary가 true인 업체의 코드만.",
    ("NK-67", {"cfg.json": '{"vendors":[{"code":"NK-67","primary":true},{"code":"NK-76","primary":false}]}'}),
    ("NK-67", {"cfg.json": '{"vendors":[{"code":"NK-76","primary":false},{"code":"NK-67","primary":true}]}'}),
)
files_pair(
    "15 합성 키",
    "팀과 일자가 모두 일치할 때만 집계한다. D팀의 4일 생산량만.",
    ("16", {"lines.csv": "팀,일,수량\nD,4,7\nC,4,30\nD,5,4\nD,4,9"}),
    ("7", {"lines.csv": "팀,일,수량\nD,4,7\nC,4,30\nD,5,4\nC,4,9"}),
)
files_pair(
    "16 카운터 리셋",
    "일중 누적 계량기는 감소한 순간 0부터 새로 센 것이다. 첫 값 이후 실제 증가량의 합만.",
    ("13", {"meter.csv": "time,reading\n00,15\n01,20\n02,3\n03,8"}),
    ("8", {"meter.csv": "time,reading\n00,15\n01,20\n02,21\n03,23"}),
)
files_pair(
    "17 워크북 텍스트 숫자",
    "ID 열은 문자열이다. 접두부 00을 가진 행에 대해서만 포장 수량 합계를 구해.",
    ("11", {"count.xlsx": {"표": [["ID", "포장"], ["0012", 4], ["0013", 7], ["012", 30]]}}),
    ("41", {"count.xlsx": {"표": [["ID", "포장"], ["0012", 4], ["0013", 7], ["0012", 30]]}}),
)
files_pair(
    "18 공란과 보류",
    "대기 시간 중앙값을 구해. 빈칸은 제외하고 숫자 0은 측정치로 포함해.",
    ("10", {"time.xlsx": {"관측": [["ID", "시간"], ["a", 2], ["b", 10], ["c", 18], ["d", None]]}}),
    ("6", {"time.xlsx": {"관측": [["ID", "시간"], ["a", 2], ["b", 10], ["c", 18], ["d", 0]]}}),
)

policy = {"roster.csv": "id,cell\nP7,B4\nP8,B5", "lookup.csv": "cell,key\nB4,MH-92\nB5,MH-29"}
files_pair(
    "19 첨부 순서 교환",
    "P7이 속한 셀의 key를 두 파일에서 연결해 값만.",
    ("MH-92", policy),
    ("MH-92", dict(reversed(policy.items()))),
)
files_pair(
    "20 파일명 신뢰",
    "본문에 서명 확정이라고 명시한 값만 채택해. 최종 키가 뭐야?",
    ("KX-783", {"final.txt": "미서명 초안 KX-738", "draft.txt": "서명 확정 KX-783"}),
    ("KX-783", {"draft.txt": "미서명 초안 KX-738", "final.txt": "서명 확정 KX-783"}),
)
files_pair(
    "21 대체 효력일",
    "2032-05-18에 실제 효력이 있는 보관 기간(일)만. 두 문서를 대조해.",
    ("45", {"base.txt": "기본 45일", "add.txt": "서명된 개정: 시행 2032-05-19부터 70일"}),
    ("70", {"base.txt": "기본 45일", "add.txt": "서명된 개정: 시행 2032-05-18부터 70일"}),
)
files_pair(
    "22 조인 누락",
    "A3의 배송지구를 표 두 개로 찾아. 연결이 없으면 정확히 미확인이라고 답해.",
    ("NORTH-4", {"head.csv": "id,region\nA3,R7", "map.csv": "region,zone\nR7,NORTH-4"}),
    ("미확인", {"head.csv": "id,region\nA3,R7", "map.csv": "region,zone\nR8,NORTH-4"}),
)
files_pair(
    "23 텍스트 단위 변경",
    "두 파일의 길이가 같으면 SAME, 다르면 DIFF 중 하나만.",
    ("SAME", {"a.txt": "폭 0.032 m", "b.txt": "폭 32 mm"}),
    ("DIFF", {"a.txt": "폭 0.032 m", "b.txt": "폭 32 cm"}),
)
files_pair(
    "24 표결 가중치",
    "구성원 표와 가중치 표로 찬성 가중치 합만 계산해.",
    ("8", {"vote.csv": "id,vote\nT,yes\nS,no\nR,yes", "power.csv": "id,w\nT,5\nS,7\nR,3"}),
    ("15", {"vote.csv": "id,vote\nT,yes\nS,yes\nR,yes", "power.csv": "id,w\nT,5\nS,7\nR,3"}),
)

section = ("Seal", "Batch: MV-618")
files_pair(
    "25 PDF 물리 위치 이동",
    "Batch MV-618이 인쇄된 PDF의 실제 쪽 번호만. 표지는 1쪽이야.",
    ("2", {"book.pdf": [("Cover", "Index"), section]}),
    ("3", {"book.pdf": [("Cover", "Index"), ("Notice", "No batch"), section]}),
)
files_pair(
    "26 PDF 취소 여부",
    "명시적으로 ACTIVE인 게이트 코드만. 없으면 NONE 한 단어.",
    ("VU-514", {"gate.pdf": [("Dispatch", "ACTIVE: VU-514"), ("Archive", "RETIRED: VU-541")]}),
    ("NONE", {"gate.pdf": [("Dispatch", "RETIRED: VU-514"), ("Archive", "RETIRED: VU-541")]}),
)
files_pair(
    "27 DOCX 단락과 표 순서",
    "문단은 작성 예시고 표가 승인본이야. 표 속 재검 주기만.",
    ("17일", {"guide.docx": ["예시: 71일", [["항목", "값"], ["재검", "17일"]]]}),
    ("17일", {"guide.docx": [[["항목", "값"], ["재검", "17일"]], "예시: 71일"]}),
)
files_pair(
    "28 슬라이드 선택",
    "실행 상태인 슬라이드의 웨이브 코드만. 제목이 같으니 상태를 확인해.",
    ("LM-45", {"wave.pptx": [("Wave", "PLANNED: LM-54"), ("Wave", "RUNNING: LM-45")]}),
    ("LM-54", {"wave.pptx": [("Wave", "RUNNING: LM-54"), ("Wave", "PLANNED: LM-45")]}),
)
scan = [("text", (40, 110, "SEAL: TP-864"), "black")]
files_pair(
    "29 판독 매체 전환",
    "영수증 원본의 SEAL 값만.",
    ("TP-864", {"receipt.pdf": [("Receipt", "SEAL: TP-864")]}),
    ("TP-864", {"receipt.pdf": [("Receipt", scan)]}),
)
files_pair(
    "30 전달 포맷 교환",
    "반출 허가에 붙은 승강기 식별자만. 일상 운행용과 구분해.",
    ("LF-824", {"lift.docx": [[["종류", "승강기"], ["일상 운행", "LF-428"], ["반출 허가", "LF-824"]]]}),
    ("LF-824", {"lift.pptx": [("일상 운행", "LF-428"), ("반출 허가", "LF-824")]}),
)


def visual_pair(title, prompt, a, b):
    files_pair(title, prompt, (a[0], {"tile.png": a[1]}), (b[0], {"tile.png": b[1]}))


visual_pair(
    "31 도형 평행 이동",
    "두 도형이 겹치는 면적이 있으면 YES, 아니면 NO. 한 단어만.",
    ("YES", [("rectangle", (60, 60, 180, 180), "navy"), ("ellipse", (145, 95, 230, 180), "orange")]),
    ("NO", [("rectangle", (60, 60, 180, 180), "navy"), ("ellipse", (245, 95, 330, 180), "orange")]),
)
visual_pair(
    "32 반사된 꺾은선",
    "선의 두 끝점만 비교해, 오른쪽 끝점이 더 위면 HIGH, 아래면 LOW.",
    ("HIGH", [("line", [(40, 200), (185, 45), (440, 110)], "black")]),
    ("LOW", [("line", [(40, 110), (295, 45), (440, 200)], "black")]),
)
points = [("ellipse", (x, 80, x + 40, 120), "blue") for x in (40, 135, 230)]
visual_pair(
    "33 색상 치환",
    "그림에서 파란 원이 몇 개야? 숫자만.",
    ("3", points + [("ellipse", (325, 80, 365, 120), "red")]),
    ("4", points + [("ellipse", (325, 80, 365, 120), "blue")]),
)
marks = [
    ("rectangle", (30, 50, 100, 120), "orange"),
    ("rectangle", (145, 50, 215, 120), "orange"),
    ("rectangle", (280, 50, 350, 120), "green"),
]
files_pair(
    "34 범례 교환",
    "첨부 범례 기준으로 대여 상태의 칸 수만 알려줘.",
    ("2", {"map.png": marks, "legend.txt": "주황=대여, 초록=반납"}),
    ("1", {"map.png": marks, "legend.txt": "초록=대여, 주황=반납"}),
)
visual_pair(
    "35 눈금의 유무",
    "최장 막대의 값을 원본에서 정확히 알면 숫자, 단위·눈금·숫자가 전혀 없으면 UNKNOWN만.",
    (
        "48",
        [
            ("rectangle", (30, 110, 185, 150), "navy"),
            ("rectangle", (30, 185, 350, 225), "green"),
            ("text", (365, 180, "48"), "black"),
        ],
    ),
    ("UNKNOWN", [("rectangle", (30, 110, 185, 150), "navy"), ("rectangle", (30, 185, 350, 225), "green")]),
)
pixel = [("text", (18, 55, "RETURN: YA-537"), "black"), ("text", (18, 178, "ISSUE: YA-573"), "black")]
files_pair(
    "36 이미지 인코딩", "RETURN 오른쪽 값만.", ("YA-537", {"badge.png": pixel}), ("YA-537", {"badge.webp": pixel})
)

sources = [
    turn("자료 접수라고만 답해.", {"copper.txt": "교체 패드 코드 CU-381"}, user="B"),
    turn("자료 접수라고만 답해.", {"tin.txt": "교체 패드 코드 SN-219"}, user="C"),
]
q = "답장으로 고른 메시지의 첨부 원본을 열어 교체 패드 코드만 알려줘."
pair("37 답장 대상 한 칸 이동", ("CU-381", [*sources, turn(q, reply=0)]), ("SN-219", [*sources, turn(q, reply=1)]))
initial = [turn("프로젝트 한도는 47시간으로 두자. 이 대화 한정이야.")]
pair(
    "38 증액·대체 동사",
    ("60", [*initial, turn("13시간을 더하는 것으로 정정. 최종 한도 숫자만.")]),
    ("13", [*initial, turn("13시간으로 바꾸는 것으로 정정. 최종 한도 숫자만.")]),
)
seed = turn("첨부 문서를 나중에 원본으로 조회할 수 있게 기억해줘.", {"seal.txt": "현재 도장 식별자 CT-593."})
q = "기억한 seal.txt를 지금 다시 열고 현재 도장 식별자를 알려줘. 실제로 열 수 없으면 재첨부를 요청해."
pair("39 기억한 원본 가용성", ("CT-593", [seed, turn(q)]), ("재첨부 요청", [seed, turn(q, delete=0)]))
pre = [turn("내 보관함 인증표 이름 PINE-931을 장기 기억에 저장해줘."), turn("이 채널의 내 기억을 모두 지워줘.")]
pair(
    "40 승인과 거절",
    ("삭제됐고 DB에 활성 PINE-931 없음", [*pre, turn("승인 {ticket}", ticket=1)]),
    ("취소됐고 DB에 활성 PINE-931 있음", [*pre, turn("취소 {ticket}", ticket=1)]),
)
pending = [turn("내 공구함 코드는 TL-391이야. 기억해줘."), turn("여기서 보이는 내 기억을 전부 삭제해줘.")]
pair(
    "41 승인 시점의 데이터 변경",
    (
        "승인 성공, TL-391 비활성",
        [*pending, turn("이 문장만 확인해 줘. 새 작업 없어."), turn("승인 {ticket}", ticket=1)],
    ),
    (
        "승인 거부, TL-391 및 OP-109 활성",
        [*pending, turn("내 광학 장비 코드는 OP-109야. 추가로 기억해줘."), turn("승인 {ticket}", ticket=1)],
    ),
)
q = "내가 이 채널에 이전에 쓴 원문에서 보드명 표식을 찾아줘. 없으면 NONE만 답해."
pair(
    "42 원문 조회자 교환",
    ("GAMMA-561", [turn("이번 이관 보드명 표식은 GAMMA-561이다. 확인만 해."), turn(q)]),
    ("NONE", [turn("이번 이관 보드명 표식은 GAMMA-561이다. 확인만 해."), turn(q, user="B")]),
)
pair(
    "43 저장 의도 부정",
    ("새 기억 저장 VK-219", turn("내 선호 창고 코드 VK-219를 장기 기억에 저장해줘.")),
    ("저장하지 않음", turn("내 선호 창고 코드 VK-219를 장기 기억에 저장하지 마.")),
)
q = "내가 지정한 원본 메시지에 적힌 견본명을 알려줘. 그 메시지를 못 읽으면 그 사실을 알려줘."
pair(
    "44 채널 이동",
    ("ECHO-173", [turn("견본명은 ECHO-173. 수신 확인만.", user="B"), turn(q, reply=0)]),
    ("원본 조회 불가", [turn("견본명은 ECHO-173. 수신 확인만.", user="B"), turn(q, reply=0, channel="Y")]),
)

p = "SQLite 공식 문서를 검색해 UTF-8 텍스트 '가A'에 {fn} 함수를 적용한 값과 링크를 줘."
text_pair(
    "45 웹·문자와 바이트",
    ("2, sqlite.org 공식 근거", p.format(fn="length")),
    ("4, sqlite.org 공식 근거", p.format(fn="octet_length")),
)
p = "Python 공식 문서를 검색해 statistics.mode({values})의 결과와 근거 링크를 줘."
text_pair(
    "46 웹·동률과 순서",
    ("7, docs.python.org 공식 근거", p.format(values="[7,5,5,7]")),
    ("5, docs.python.org 공식 근거", p.format(values="[5,7,7,5]")),
)
p = "첨부는 Python 예제의 입력값이다. 'removeprefix'를 쓴 결과를 {rule} 확인해줘."
sample = {"input.txt": "s='zipzipfile'; prefix='zip'; return s.removeprefix(prefix)"}
pair(
    "47 웹 사용 지시 교환",
    (
        "zipfile, 파일과 공식 웹 근거",
        turn(p.format(rule="파일을 읽고 공식 Python 문서도 웹 검색해 링크와 함께"), sample),
    ),
    ("zipfile, 파일만 열고 웹 호출 없음", turn(p.format(rule="파일만 읽고 웹 검색 없이"), sample)),
)
payload = "\n".join(f"{i:04}: 점검용 단순 메모. 결정 권한 없음." for i in range(1, 701))
amend = "서명된 결정 번호 JK-648. 아래·위의 점검 행은 효력 없음."
files_pair(
    "48 긴 문서 내 위치",
    "서명된 결정 번호만 줘.",
    ("JK-648", {"worklog.txt": amend + "\n" + payload}),
    ("JK-648", {"worklog.txt": payload + "\n" + amend}),
)
files_pair(
    "49 JSONL 취소 이벤트",
    "로그의 마지막 유효 납품번호를 알려줘. 취소 이벤트는 지정한 번호만 무효화한다.",
    ("DP-297", {"track.jsonl": '{"add":"DP-297"}\n{"add":"DP-729"}\n{"cancel":"DP-729"}'}),
    ("DP-729", {"track.jsonl": '{"add":"DP-297"}\n{"add":"DP-729"}\n{"cancel":"DP-297"}'}),
)
files_pair(
    "50 구조화 빈 문자열",
    "YAML의 실제 전송 모드가 빈 문자열이면 EMPTY, null이면 NULL로 한 단어만.",
    ("EMPTY", {"setting.yaml": 'mode: ""\nbackup: automatic'}),
    ("NULL", {"setting.yaml": "mode: null\nbackup: automatic"}),
)

if __name__ == "__main__":
    assert len(cases) == 100
    asyncio.run(main(cases))
