"""긴 PDF 판독과 표 전사를 실제 로컬 HTTP 서버를 통해 검증한다."""

import csv
import io
import re

import fitz
from docx import Document
from test_jeda_server import answer, attach, pytestmark, results, turn  # noqa: F401


def slides(count, *, late=False, scanned=False):
    with fitz.open() as doc:
        for i in range(1, count + 1):
            page = doc.new_page(width=540, height=300)
            title = "Optical storage maintenance" if not late or i >= 4 else f"Page {i}"
            page.insert_text((25, 45), title, fontsize=20)
            if not late or i >= 4:
                page.insert_text((25, 90), f"Probe {i:02d}: verification key STOR-{700 + i}")
            page.draw_line((40, 170), (190, 115))
        return rasterize(doc) if scanned else doc.tobytes()


def rasterize(doc):
    with fitz.open() as scan:
        for page in doc:
            target = scan.new_page(width=page.rect.width, height=page.rect.height)
            target.insert_image(target.rect, stream=page.get_pixmap(matrix=fitz.Matrix(2, 2)).tobytes("png"))
        return scan.tobytes(deflate=True)


def ledger(scan, count=2):
    expected = []
    with fitz.open() as doc:
        for n in range(count):
            unit = ("USD", "kUSD")[n % 2]
            cols = ["Item", "Q1", "Q2", "Q3", "Q4", "Q5"]
            if n % 2:
                cols[2], cols[3] = cols[3], cols[2]
            rows = [cols]
            for i in range(1, 19):
                rows.append([f"SKU-{i:02d}", *[str(n * 200 + 10 * i + int(c[1])) for c in cols[1:]]])
            rows.append(["Subtotal", *[str(sum(int(r[j]) for r in rows[1:])) for j in range(1, 6)]])
            page = doc.new_page(width=590, height=640)
            page.insert_text((30, 35), f"Ledger / Unit: {unit}", fontsize=16)
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    page.insert_text((32 + 93 * j, 70 + 24 * i), value, fontsize=12)
            expected.append(rows)
        return (rasterize(doc) if scan else doc.tobytes()), expected


def pdf_request(prompt, data):
    response = turn(prompt, attachments=[attach("source.pdf", data)])
    evidence = results(response, "file")[-1]
    assert evidence["status"] == "success", evidence
    return answer(response), evidence


def test_long_document_overview():
    text, evidence = pdf_request("이게 무슨 문서인지 짧게 소개해줘.", slides(55))
    assert evidence["pages_read"] == [1, 2, 3] and evidence["reader_calls"] == 1, evidence
    assert any(word in text.lower() for word in ("광학", "광 저장", "optical")), text


def test_overview_expands_past_uninformative_front():
    text, evidence = pdf_request("이게 어떤 주제의 문서인지 소개해줘.", slides(9, late=True))
    assert 4 in evidence["pages_read"], evidence
    assert any(word in text.lower() for word in ("광학", "광 저장", "optical")), text


def test_full_scan_keeps_last_page():
    text, evidence = pdf_request(
        "문서 전체를 짧게 요약하고 맨 처음과 마지막에 나온 검수 키를 모두 정확히 적어줘.", slides(16, scanned=True)
    )
    assert evidence["pages_read"] == list(range(1, 17)) and evidence["reader_calls"] < 16, evidence
    assert "STOR-701" in text and "STOR-716" in text, text


def test_native_borderless_csv():
    data, expected = ledger(False)
    text, evidence = pdf_request("모든 쪽의 표 전체를 열 순서와 셀 값 그대로 CSV로 옮겨줘.", data)
    assert evidence["reader_calls"] == 0, evidence
    check_csv(text, expected)


def check_csv(text, expected):
    blocks = re.findall(r"```csv\s*\n(.*?)\n```", text, re.S)
    assert [list(csv.reader(io.StringIO(block))) for block in blocks] == expected, text


def test_dense_scan_csv_checksums():
    data, expected = ledger(True)
    text, evidence = pdf_request(
        "모든 표를 한 행도 빠짐없이 그대로 CSV로 옮기고, 소계 행을 제외한 각 열의 합계도 단위별로 검산해줘.", data
    )
    check_csv(text, expected)
    for rows, unit in zip(expected, ("USD", "kUSD"), strict=True):
        assert f"Q2 {unit} = {rows[-1][rows[0].index('Q2')]}" in text, text
    assert evidence["reader_calls"] >= 6, evidence


def test_lookup_in_eight_scanned_tables():
    data, expected = ledger(True, 8)
    text, evidence = pdf_request(
        "이 PDF에서 각 쪽의 SKU-16 행 Q2 값과 단위만 쪽 순서대로 알려줘. 모든 셀을 옮길 필요는 없어.", data
    )
    assert evidence["pdf_mode"] == "lookup" and len(evidence["pages_read"]) == 8, evidence
    values = [rows[16][rows[0].index("Q2")] for rows in expected]
    positions = [re.search(rf"(?<!\d){v}(?!\d)", text.replace(",", "")) for v in values]
    assert all(positions) and [p.start() for p in positions] == sorted(p.start() for p in positions), text
    assert "USD" in text and "kUSD" in text, text


def test_docx_body_and_table():
    doc = Document()
    doc.add_paragraph("Shipment inspection / approval code LIME-724")
    row = doc.add_table(rows=1, cols=2).rows[0]
    row.cells[0].text, row.cells[1].text = "Batch", "ZED-918"
    output = io.BytesIO()
    doc.save(output)
    response = turn(
        "본문 승인 코드와 표의 배치 코드를 둘 다 적어줘.", attachments=[attach("spec.docx", output.getvalue())]
    )
    assert "LIME-724" in answer(response) and "ZED-918" in answer(response)


def test_cp949_csv_exact_lookup():
    response = turn(
        "감사 항목의 확인 코드를 찾아줘.",
        attachments=[attach("items.csv", "항목,확인코드\n입고,BLUE-217\n감사,PLUM-613\n".encode("cp949"))],
    )
    assert "PLUM-613" in answer(response) and "BLUE-217" not in answer(response)


def test_reply_to_long_pdf_respects_mode_and_page():
    original = turn("", attachments=[attach("lecture.pdf", slides(55))])
    overview = turn("답장으로 지정한 PDF가 무슨 문서인지 간단히 소개해줘.", reply_to=original["id"])
    record = results(overview, "file")[-1]
    assert record["pdf_mode"] == "overview" and record["pages_read"] == [1, 2, 3]
    assert any(word in answer(overview).lower() for word in ("광학", "광 저장", "optical"))
    specific = turn("답장으로 지정한 PDF 49쪽 검수 코드를 읽어줘.", reply_to=original["id"])
    assert results(specific, "file")[-1]["pages_read"] == [49] and "STOR-749" in answer(specific)
