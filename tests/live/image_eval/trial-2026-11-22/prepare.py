"""Freeze both 41-question input manifests before making the candidate change."""

import hashlib
import io
import json
import shutil
from pathlib import Path
from urllib.request import Request, urlopen

import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path.cwd()
WORK = ROOT / ".pytest_cache/identity_binding"
OLD = ROOT / ".pytest_cache/paired_identity/inputs.json"
PUBLIC = "https://raw.githubusercontent.com/"
POKE = PUBLIC + "PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"
FLAGS = PUBLIC + "lipis/flag-icons/main/flags/4x3/{}.svg"
TOPIC = PUBLIC + "github/explore/main/topics/{0}/{0}.png"
SK = PUBLIC + "scikit-image/scikit-image/v0.24.0/skimage/data/hubble_deep_field.jpg"
GROUPS = ["판독", "범위 단서", "무단서", "변형", "외부 대조", "식별 불가"]
CASES = [
    ("다음 두 정차지와 도착 시각을 써 줘.", "Oak 09:21 / Pine 09:46", ""),
    ("예약표의 좌석과 출입구 번호가 뭐야?", "D12 / 7", ""),
    ("시약병 라벨의 농도와 부피를 읽어줘.", "8% / 140 mL", ""),
    ("주소 스티커에 적힌 우편번호와 도시를 써줘.", "85013 / Phoenix", ""),
    ("포켓몬에 나오는 이 캐릭터의 한국어 이름과 외형 근거는?", "누오 / Quagsire", POKE.format(195)),
    ("아프리카 나라의 깃발이야. 국가명과 특징을 알려줘.", "세이셸 / Seychelles", FLAGS.format("sc")),
    ("리눅스 배포판 로고래. 이름과 보이는 근거는?", "데비안 / Debian", TOPIC.format("debian")),
    ("scikit-image 우주 사진 예제에서 이 이미지에 해당하는 데이터 함수 이름이 뭐야?", "hubble_deep_field", SK),
    ("이 로고가 가리키는 소프트웨어 프로젝트의 이름은?", "잉크스케이프 / Inkscape", "icon:inkscape"),
    ("이건 어느 프로젝트 로고야? 외형 근거 하나도 알려줘.", "젠투 / Gentoo", "icon:gentoo"),
    ("사진에 나온 국기가 어느 나라 거야?", "바베이도스 / Barbados", FLAGS.format("bb")),
    ("그림에 나온 캐릭터 이름을 찾아줘.", "핫삼 / Scizor", POKE.format(212)),
    ("이 배지가 본뜬 캐릭터의 고유 이름은?", "샹델라 / Chandelure", POKE.format(609)),
    ("이 인쇄물의 원형이 된 편집기는 뭐야?", "빔 / Vim", TOPIC.format("vim")),
    ("질감을 넣어 만든 이 깃발은 어느 나라를 본뜬 거야?", "네팔 / Nepal", FLAGS.format("np")),
    ("스티커로 만든 이 무늬는 어느 프로젝트의 로고야?", "깃랩 / GitLab", "icon:gitlab"),
    (
        "이 캐릭터 이름이 뭐야? 포켓몬 도감의 공개 그림과 실제 비교하고 공통점을 알려줘.",
        "블래키 / Umbreon; 실제 동종 이미지 대조와 공통점",
        POKE.format(197),
    ),
    (
        "이 깃발이 어느 나라 건지 공개 국기 이미지와 직접 비교하고 공통점을 알려줘.",
        "트리니다드 토바고 / Trinidad and Tobago; 실제 도안 대조와 공통점",
        FLAGS.format("tt"),
    ),
    (
        "이 마스코트가 어느 그래픽 프로그램의 것인지 공개 그림과 직접 비교해서 근거도 알려줘.",
        "김프 / GIMP; 실제 캐릭터 이미지 대조와 공통점",
        "icon:gimp",
    ),
    (
        "이 로고의 프로그램 이름과 공개 로고에서 직접 대조한 특징 한 가지를 알려줘.",
        "블렌더 / Blender; 실제 로고 대조와 공통점",
        "icon:blender",
    ),
    ("이 손잡이를 만든 업체 이름이 정확히 뭐야?", "제조사 단서 없음 + 이름표·부품번호 등", ""),
    ("이 승차권을 누가 결제했는지 알려줘.", "구매자 식별 불가 + 결제·구매 기록이나 이름", ""),
    ("이 안내판을 설치한 연도가 언제야?", "연도 식별 불가 + 날짜나 설치 기록", ""),
    ("이 열쇠가 우리 사무실의 어느 서랍 열쇠야?", "서랍 식별 불가 + 관리번호·잠금장치 등", ""),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(i):
    pic = Image.new("RGB", (580, 280), "#f6f4ef")
    draw = ImageDraw.Draw(pic)
    font = ImageFont.truetype("arial.ttf", 34)
    text = {
        0: "STOPS\nOak    09:21\nPine   09:46",
        1: "BOOKING\nSeat D12\nGate 7",
        2: "Sample A\n8% solution\n140 mL",
        3: "DELIVERY\nPhoenix, AZ\n85013",
        21: "SINGLE RIDE\nFrom: Central\nZone 2",
        22: "EXIT  >",
    }
    if i in text:
        draw.multiline_text((40, 32), text[i], font=font, fill="#213442", spacing=14)
    elif i == 20:
        draw.rounded_rectangle((100, 70, 480, 153), radius=32, fill="gray")
        for x in (103, 433):
            draw.rectangle((x, 122, x + 43, 185), fill="gray")
    else:
        draw.ellipse((90, 85, 182, 177), outline="#757777", width=18)
        draw.rectangle((175, 122, 385, 139), fill="#757777")
        draw.polygon([(295, 135), (295, 163), (320, 163), (320, 148), (350, 148), (350, 136)], fill="#757777")
    return pic


def main():
    images = WORK / "images"
    images.mkdir(parents=True, exist_ok=True)
    cases = [c for c in json.loads(OLD.read_text(encoding="utf8")) if not c["label"].startswith("new-")]
    if not (WORK / "A").exists():
        shutil.copytree(ROOT / "assistant_bot", WORK / "A/assistant_bot", ignore=shutil.ignore_patterns("__pycache__"))
    gold = {}
    for i, (q, answer, src) in enumerate(CASES):
        key = f"blind-{i + 1:02}"
        path = images / (key + ".png")
        if src.startswith("icon:"):
            src = PUBLIC + "simple-icons/simple-icons/develop/icons/" + src.split(":")[1] + ".svg"
        if not path.exists():
            if src:
                with urlopen(Request(src, headers={"User-Agent": "JedaEvaluation/1.0"}), timeout=20) as response:
                    data = response.read()
                if src.endswith(".svg"):
                    with pymupdf.open(stream=data, filetype="svg") as doc:
                        data = (
                            doc[0]
                            .get_pixmap(
                                matrix=pymupdf.Matrix(340 / doc[0].rect.width, 340 / doc[0].rect.width), alpha=True
                            )
                            .tobytes("png")
                        )
                with Image.open(io.BytesIO(data)) as source:
                    rgba = source.convert("RGBA")
                pic = Image.new("RGB", rgba.size, "white")
                pic.paste(rgba, mask=rgba.getchannel("A"))
                pic.thumbnail((850, 850))
                if 12 <= i < 16:
                    if i != 14:
                        pic = ImageOps.colorize(ImageOps.grayscale(pic), "#19332b", "#fbdbac")
                    pic = ImageOps.expand(pic.rotate(-6, expand=True, fillcolor="white"), 12, "#b46d39")
            else:
                pic = generate(i)
            pic.save(path)
        gold[key] = dict(group=GROUPS[i // 4], expected=answer, source=src, sha256=sha(path))
        cases.append(dict(label=key, channel=301 + i, path=str(path.resolve()), prompt=q))
    assert len(cases) == 41
    for c in cases:
        if c["path"]:
            assert Path(c["path"]).is_file(), c["label"]
    (WORK / "inputs.json").write_text(json.dumps(cases, ensure_ascii=False), encoding="utf8")
    dest = Path(__file__).parent / "seal.json"
    with dest.open("x", encoding="utf8") as f:
        json.dump(
            dict(
                gold=gold,
                inputs={
                    c["label"]: dict(
                        prompt=c["prompt"], channel=c["channel"], sha256=sha(Path(c["path"])) if c["path"] else None
                    )
                    for c in cases
                },
                baseline={p.name: sha(p) for p in (WORK / "A/assistant_bot").glob("*.py")},
            ),
            f,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
