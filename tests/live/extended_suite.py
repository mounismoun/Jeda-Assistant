"""로컬 실서버 대상 추가 시나리오. 실행 예: python tests/live/extended_suite.py DIR --port 8779"""

import argparse
import asyncio
import base64
import json
import re
from io import BytesIO
from pathlib import Path
from time import monotonic
from uuid import uuid4

import aiohttp
import pymupdf as fitz
from docx import Document
from extended_cases import cases
from openpyxl import Workbook
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation


def artifact(name, content):
    suffix = Path(name).suffix.lower()
    stream = BytesIO()
    if isinstance(content, bytes):
        return content
    if suffix == ".xlsx":
        book = Workbook()
        book.remove(book.active)
        for sheet, rows in content.items():
            tab = book.create_sheet(sheet)
            for row in rows:
                tab.append(row)
        book.save(stream)
    elif suffix == ".pdf":
        with fitz.open() as doc:
            pages = content["pages"] if isinstance(content, dict) else content
            for title, body in pages:
                page = doc.new_page()
                page.insert_text((54, 60), title, fontsize=18)
                if isinstance(body, str):
                    page.insert_text((54, 120), body, fontsize=14)
                else:
                    page.insert_image(fitz.Rect(54, 90, 534, 390), stream=artifact("scan.png", body))
            doc.set_toc([[1, title, i] for i, (title, _) in enumerate(pages, 1)])
            opts = (
                {"encryption": fitz.PDF_ENCRYPT_AES_256, "user_pw": "fixture-only", "owner_pw": "fixture-owner"}
                if isinstance(content, dict)
                else {}
            )
            stream.write(doc.tobytes(**opts))
    elif suffix == ".docx":
        doc = Document()
        for part in content:
            if isinstance(part, str):
                doc.add_paragraph(part)
            else:
                table = doc.add_table(rows=0, cols=len(part[0]))
                for row in part:
                    for cell, value in zip(table.add_row().cells, row, strict=True):
                        cell.text = value
        doc.save(stream)
    elif suffix == ".pptx":
        slides = Presentation()
        for title, body in content:
            slide = slides.slides.add_slide(slides.slide_layouts[1])
            slide.shapes.title.text = title
            slide.placeholders[1].text = body
        slides.save(stream)
    elif suffix in {".png", ".webp", ".jpg"}:
        canvas = Image.new("RGB", (480, 300), "white")
        draw = ImageDraw.Draw(canvas)
        for shape, points, color in content:
            if shape == "text":
                draw.text(points[:2], points[2], font=ImageFont.load_default(size=32), fill=color)
            elif shape == "line":
                draw.line(points, fill=color, width=8)
            else:
                getattr(draw, shape)(points, fill=color)
        canvas.save(stream, format={".png": "PNG", ".webp": "WEBP", ".jpg": "JPEG"}[suffix])
    else:
        return content.encode()
    return stream.getvalue()


async def execute(session, base, case, directory):
    number, group, expected, turns = case
    token = uuid4().hex[:12]
    history = []
    start = monotonic()
    folder = directory / "fixtures" / f"{number:03}"
    for step in turns:
        files = []
        for name, spec in step.get("files", {}).items():
            data = artifact(name, spec)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / name).write_bytes(data)
            files.append({"name": name, "base64": base64.b64encode(data).decode()})
        body = {
            "user": token + step.get("user", "A"),
            "channel": token + step.get("channel", "X"),
            "text": step["text"],
            "attachments": files,
        }
        if "reply" in step:
            body["reply_to"] = history[step["reply"]]["response"]["id"]
        if "delete" in step:
            source = history[step["delete"]]["response"]
            path = f"/requests/{source['id']}/attachments/{source['attachments'][0]['id']}"
            async with session.delete(base + path) as removed:
                removed.raise_for_status()
        if "ticket" in step:
            events = history[step["ticket"]].get("response", {}).get("events", [])
            ticket = re.search(r"(?:승인|approve)\s+([a-f0-9]{12})", " ".join(e["text"] for e in events), re.I)
            if not ticket:
                history.append({"request": {"text": body["text"]}, "blocked": "선행 응답에 승인 번호 없음"})
                break
            body["text"] = body["text"].replace("{ticket}", ticket[1])
        if step.get("active"):
            body["wait"] = False
        item = {"request": {**body, "attachments": [f["name"] for f in files]}}
        history.append(item)
        try:
            async with session.post(base + "/requests", json=body) as response:
                response.raise_for_status()
                item["response"] = await response.json()
            if step.get("active") or "finish" in step:
                initial = step.get("active", False)
                target = item if initial else history[step["finish"]]
                url = base + "/requests/" + target["response"]["id"]
                deadline = monotonic() + 360
                while monotonic() < deadline:
                    async with session.get(url) as poll:
                        poll.raise_for_status()
                        state = await poll.json()
                    if (initial and state["events"]) or state["state"] in {"done", "cancelled", "failed"}:
                        target["response"] = state
                        if initial:
                            target["state_before_followup"] = state["state"]
                        break
                    await asyncio.sleep(0.15 if initial else 0.5)
                else:
                    item["error"] = "상태 확인 시간 초과"
                    break
        except (aiohttp.ClientError, TimeoutError) as exc:
            item["error"] = repr(exc)
            break
    return {
        "id": number,
        "group": group,
        "expected": expected,
        "turns": history,
        "seconds": round(monotonic() - start, 1),
    }


async def main(catalog=cases):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int, default=100)
    args = parser.parse_args()
    args.directory.mkdir(exist_ok=True, parents=True)
    path = args.directory / "exchanges.jsonl"
    seen = {json.loads(line)["id"] for line in path.read_text().splitlines()} if path.exists() else set()
    lock = asyncio.Semaphore(args.workers)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=630)) as session:

        async def work(case):
            async with lock:
                result = await execute(session, f"http://127.0.0.1:{args.port}", case, args.directory)
                with path.open("a") as out:
                    out.write(json.dumps(result, ensure_ascii=False) + "\n")
                print(case[0], case[1], result["seconds"], flush=True)

        await asyncio.gather(*(work(c) for c in catalog if args.first <= c[0] <= args.last and c[0] not in seen))


if __name__ == "__main__":
    asyncio.run(main())
