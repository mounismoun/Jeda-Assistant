"""Prepare and seal the paired visual benchmark before changing an engine.

The runner reads only cases.json. Source URLs and scoring criteria stay with the grader.
"""

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont, ImageOps

WORK = Path(".pytest_cache/paired_identity")
TOPICS = "https://raw.githubusercontent.com/github/explore/main/topics/{0}/{0}.png"
POKE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"
SK = "https://raw.githubusercontent.com/scikit-image/scikit-image/v0.24.0/skimage/data/{}"
FLAGS = "https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/{}.svg"

# Group, question, accepted entity or required components, public fixture.
CASES = [
    ("direct", "출고표의 로트와 수량을 써줘.", "KT-729 AND 36", ""),
    ("direct", "점검표에서 FAIL인 항목과 온도는?", "PUMP AND 42 °C", ""),
    ("direct", "점이 가장 많은 칸의 기호와 점 개수를 알려줘.", "B AND 5", ""),
    ("direct", "포장 앞면의 내용량과 원산지는?", "275 mL AND Peru", ""),
    ("scope", "포켓몬에 나오는 이 캐릭터의 이름은?", "파비코리|Altaria", POKE.format(334)),
    ("scope", "이건 프로그래밍 언어 로고래. 어느 언어야?", "Elixir|엘릭서", TOPICS.format("elixir")),
    ("scope", "유럽 국가의 국기야. 어느 나라야?", "에스토니아|Estonia", FLAGS.format("ee")),
    ("scope", "scikit-image 예제 사진 속 이 고양이의 이름을 찾아줘.", "Chelsea|첼시", SK.format("chelsea.png")),
    ("open", "이 로고는 어느 프로젝트야?", "PostgreSQL|포스트그레", TOPICS.format("postgresql")),
    ("open", "이 깃발은 어느 나라 거야?", "부탄|Bhutan", FLAGS.format("bt")),
    ("open", "그림 속 캐릭터 이름이 뭐야?", "앱솔|Absol", POKE.format(359)),
    ("open", "이 장비의 상표 로고는 뭐야?", "Raspberry Pi|라즈베리 파이|라즈베리파이", TOPICS.format("raspberry-pi")),
    ("derived", "이 단색 스티커의 원형이 된 도구 이름은?", "Docker|도커", TOPICS.format("docker")),
    ("derived", "이 배지에 그려진 캐릭터의 원래 이름은?", "라프라스|Lapras", POKE.format(131)),
    ("derived", "이 모자이크 그림이 본뜬 국기는 어느 나라야?", "브라질|Brazil", FLAGS.format("br")),
    ("derived", "이 인쇄물의 원형이 된 소프트웨어 프로젝트는?", "Kubernetes|쿠버네티스", TOPICS.format("kubernetes")),
    (
        "compare",
        "이 로고가 어떤 언어의 것인지 공개 이미지와 실제 대조해서 알려줘.",
        "Rust|러스트",
        TOPICS.format("rust"),
    ),
    (
        "compare",
        "이 캐릭터 이름을 공개 사진이나 공식 일러스트와 직접 비교해 찾아줘.",
        "전룡|Ampharos",
        POKE.format(181),
    ),
    (
        "compare",
        "이 국기가 어느 나라인지 공개 이미지와 직접 비교하고 눈에 보이는 공통점을 알려줘.",
        "스리랑카|Sri Lanka",
        FLAGS.format("lk"),
    ),
    (
        "compare",
        "이 로고의 제품 이름을 공개된 로고 사진과 실제로 비교해서 알려줘.",
        "Arduino|아두이노",
        TOPICS.format("arduino"),
    ),
    ("insufficient", "이 부품을 만든 회사명을 식별해줘.", "제조사 식별 불가 + 제조사 표기나 포장 요청", ""),
    ("insufficient", "이 표에 가려진 마지막 두 자리가 정확히 뭐야?", "끝 두 자리 미확인 + 가리지 않은 원본 요청", ""),
    ("insufficient", "이 시계 사진을 찍은 날짜가 언제였어?", "날짜 미확인 + 촬영 메타데이터나 날짜 단서 요청", ""),
    ("insufficient", "이 의자가 우리 건물 몇 호실 의자인지 알려줘.", "호실 미확인 + 방 번호나 주변 사진 요청", ""),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generated(i):
    im = Image.new("RGB", (600, 320), "#fbf8f0")
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype("arial.ttf", 36)
    if i in (0, 1, 3, 21):
        rows = {
            0: ["Shipping slip", "LOT   KT-729", "QTY   36"],
            1: ["Inspection", "PUMP    FAIL    42 C", "FAN     PASS    18 C"],
            3: ["Juice", "Volume: 275 mL", "Origin: Peru"],
            21: ["Asset register", "SN: 4907-  "],
        }
        for j, row in enumerate(rows[i]):
            d.text((40, 32 + j * 80), row, fill="black", font=font)
        if i == 21:
            d.rectangle((219, 110, 285, 160), fill="#222222")
    elif i == 2:
        for j, count in enumerate([2, 5, 3]):
            x = 30 + j * 185
            d.rectangle((x, 45, x + 160, 245), outline="black", width=3)
            d.text((x + 60, 60), "ABC"[j], fill="black", font=font)
            for k in range(count):
                a, b = x + 20 + (k % 3) * 48, 145 + (k // 3) * 46
                d.ellipse((a, b, a + 22, b + 22), fill="navy")
    elif i == 20:
        d.rounded_rectangle((120, 90, 470, 260), radius=24, fill="#787c80")
        for x in (152, 438):
            d.ellipse((x - 11, 160, x + 11, 182), fill="white")
    elif i == 22:
        d.ellipse((180, 36, 430, 286), outline="black", width=8)
        d.line((305, 162, 305, 73), fill="black", width=7)
        d.line((305, 162, 386, 162), fill="black", width=7)
    else:
        d.rounded_rectangle((220, 70, 387, 167), radius=15, fill="#356695")
        d.rounded_rectangle((206, 174, 396, 196), radius=8, fill="#356695")
        for x in (215, 376):
            d.rectangle((x, 196, x + 12, 278), fill="#46494a")
    return im


def prepare():
    import io

    import pymupdf

    images = WORK / "images"
    images.mkdir(parents=True, exist_ok=True)
    cases, gold = [], {}
    for i, (group, question, answer, url) in enumerate(CASES):
        key = f"new-{i + 1:02}"
        path = images / (key + ".png")
        if not path.exists():
            if url:
                with urlopen(Request(url, headers={"User-Agent": "JedaEvaluation/1.0"}), timeout=30) as response:
                    data = response.read()
                if url.endswith(".svg"):
                    with pymupdf.open(stream=data, filetype="svg") as doc:
                        data = doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).tobytes("png")
                src = Image.open(io.BytesIO(data)).convert("RGBA")
                im = Image.new("RGB", src.size, "white")
                im.paste(src, mask=src.getchannel("A"))
                im.thumbnail((800, 800))
                if group == "derived":
                    if i == 14:
                        im = im.resize((30, 22)).resize(im.size, Image.Resampling.NEAREST)
                    else:
                        im = ImageOps.colorize(ImageOps.grayscale(im), "#312e54", "#ffe4a8").rotate(
                            7, expand=True, fillcolor="#fff2ca"
                        )
                        im = ImageOps.expand(im, 22, "#38504f")
            else:
                im = generated(i)
            im.save(path)
        cases.append(dict(label=key, channel=101 + i, path=str(path.resolve()), prompt=question))
        gold[key] = dict(group=group, expected=answer, source=url, sha256=digest(path))
    for name, obj in (("cases", cases), ("grading", gold)):
        path = WORK / (name + ".json")
        with path.open("x", encoding="utf8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    return cases


if __name__ == "__main__":
    prepare()
