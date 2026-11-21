"""PDF 묶음 처리에서 실제 API로 재현하기 어려운 경계 조건."""

import asyncio
from types import SimpleNamespace

import fitz

from assistant_bot.document_reader import analyze_document
from assistant_bot.pdf_reader import Table, table_evidence


def test_missing_or_duplicate_page_retries_only_that_page():
    class Reader:
        def __init__(self):
            self.groups = []
            self.active = self.peak = 0

        async def text(self, model, effort, instructions, data, **kwargs):
            pages = [
                int(p["text"].split()[1].split("쪽")[0])
                for p in data[0]["content"]
                if p.get("text", "").startswith("PDF ")
            ]
            self.groups.append(pages)
            self.active += 1
            self.peak = max(self.peak, self.active)
            await asyncio.sleep(0.02)
            self.active -= 1
            notes = [dict(page=n, observed=f"근거 {n}", needs_detail=False, unread="") for n in pages]
            if pages[0] == 1 and len(pages) > 1:
                notes.pop(2)
                notes.append(notes[0])
            elif pages == [3]:
                notes[0].update(unread="범례가 흐립니다.")
            return {"pages": notes, "enough_for_overview": False}

    with fitz.open() as doc:
        for _ in range(17):
            page = doc.new_page(width=200, height=100)
            page.draw_line((10, 30), (100, 15))
        source = doc.tobytes()
    reader = Reader()
    result = asyncio.run(
        analyze_document(
            reader,
            SimpleNamespace(vision="vision", everyday="text"),
            "plots.pdf",
            source,
            "그래프 전체 요약",
            dict(chapter=0, first=0, last=0, pdf_mode="full"),
        )
    )
    assert sorted(reader.groups) == sorted([list(range(1, 9)), list(range(9, 17)), [1], [3], [17]])
    assert reader.peak == 2
    assert result["status"] == "partial" and result["unread"] == ["plots.pdf · PDF 3쪽 — 범례가 흐립니다."]
    locations = [int(line.split("PDF ")[1].split("쪽")[0]) for line in result["text"].splitlines() if "근거" in line]
    assert locations == list(range(1, 18))


def test_native_limit_preserves_unread_tail_without_inventing_a_sum():
    with fitz.open() as doc:
        for i in range(82):
            doc.new_page().insert_text((20, 50), f"Source document {i + 1}.")
        data = doc.tobytes()
    r = asyncio.run(analyze_document(None, None, "range.pdf", data, "요약", dict(chapter=0, first=0, last=0)))
    assert r["reader_calls"] == 0 and r["pages_read"] == list(range(1, 81))
    assert r["status"] == "partial" and "81–82쪽" in r["unread"][0]


def test_totals_check_source_and_omit_nonnumeric_columns():
    table = Table(
        2, ["Item", "Price", "Quantity"], "", [["A", "2.99", "1.1"], ["B", "1.25", "2.2"], ["Total", "", "3.4"]]
    )
    blocks = table_evidence([table], True)
    assert len(blocks) == 2 and "3.3" in blocks[1] and "3.4와 불일치" in blocks[1]
    assert table_evidence([table], False) == blocks[:1]
