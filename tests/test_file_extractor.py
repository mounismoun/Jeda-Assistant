import zipfile
from io import BytesIO
from types import ModuleType

import pytest

from assistant_bot.file_extractor import (
    extract_attachment_text,
    extract_bytes_text,
    extract_local_file_text,
    has_meaningful_text,
    is_supported_attachment,
)


def test_supported_attachment_extensions() -> None:
    assert is_supported_attachment("note.txt")
    assert is_supported_attachment("plan.md")
    assert is_supported_attachment("meeting.PDF")
    assert is_supported_attachment("slides.pptx")
    assert is_supported_attachment("report.hwpx")
    assert is_supported_attachment("data.json")
    assert is_supported_attachment("page.html")
    assert is_supported_attachment("table.tsv")
    assert is_supported_attachment("doc.odt")
    assert is_supported_attachment("sheet.ods")
    assert is_supported_attachment("image.png")
    assert is_supported_attachment("scan.tiff")
    assert not is_supported_attachment("legacy.hwp")
    assert not is_supported_attachment("slides.ppt")
    assert not is_supported_attachment("old.xls")
    assert not is_supported_attachment("old.doc")
    assert not is_supported_attachment("archive.zip")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_extract_attachment_text_rejects_invalid_utf8() -> None:
    attachment = FakeAttachment("broken.txt", b"\xff\xfe\x00")

    with pytest.raises(ValueError, match="UTF-8 텍스트로 읽지 못했습니다"):
        await extract_attachment_text(attachment, max_bytes=1024)


@pytest.mark.anyio
async def test_extract_attachment_text_rejects_symbol_only_text() -> None:
    attachment = FakeAttachment("symbols.md", b"---\n***\n")

    with pytest.raises(ValueError, match="저장할 만한 텍스트"):
        await extract_attachment_text(attachment, max_bytes=1024)


@pytest.mark.anyio
async def test_extract_attachment_text_accepts_meaningful_text() -> None:
    attachment = FakeAttachment("note.txt", "회의 메모".encode())

    extracted = await extract_attachment_text(attachment, max_bytes=1024)

    assert extracted.text == "회의 메모"


def test_has_meaningful_text() -> None:
    assert has_meaningful_text("회의 메모")
    assert has_meaningful_text("todo 1")
    assert not has_meaningful_text("--- ***")


def test_extract_local_file_text_accepts_markdown(tmp_path) -> None:
    path = tmp_path / "note.md"
    path.write_text("# 회의 메모\n\n배포 일정 정리", encoding="utf-8")

    extracted = extract_local_file_text(path, max_bytes=1024)

    assert extracted.filename == "note.md"
    assert extracted.content_type == "text/markdown"
    assert "배포 일정" in extracted.text


def test_extract_local_file_text_rejects_unsupported_file(tmp_path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(b"fake")

    with pytest.raises(ValueError, match="비전 OCR"):
        extract_local_file_text(path, max_bytes=1024)


def test_extract_json_text_is_pretty_printed(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"service":"SleepGPT","enabled":true}', encoding="utf-8")

    extracted = extract_local_file_text(path, max_bytes=1024)

    assert extracted.content_type == "application/json"
    assert '"service": "SleepGPT"' in extracted.text


def test_extract_jsonl_text_normalizes_lines(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text('{"event":"start"}\n{"event":"done"}\n', encoding="utf-8")

    extracted = extract_local_file_text(path, max_bytes=1024)

    assert '"event": "start"' in extracted.text
    assert '"event": "done"' in extracted.text


def test_extract_yaml_text(tmp_path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("service: SleepGPT\nenabled: true\n", encoding="utf-8")

    extracted = extract_local_file_text(path, max_bytes=1024)

    assert "service: SleepGPT" in extracted.text


def test_extract_xml_html_and_tsv_text(tmp_path) -> None:
    xml_path = tmp_path / "note.xml"
    html_path = tmp_path / "page.html"
    tsv_path = tmp_path / "table.tsv"
    xml_path.write_text("<root><title>회의</title><body>일정 정리</body></root>", encoding="utf-8")
    html_path.write_text(
        "<html><script>hide()</script><body><h1>공지</h1><p>배포 일정</p></body></html>",
        encoding="utf-8",
    )
    tsv_path.write_text("이름\t금액\nA\t100\n", encoding="utf-8")

    xml = extract_local_file_text(xml_path, max_bytes=1024)
    html = extract_local_file_text(html_path, max_bytes=1024)
    tsv = extract_local_file_text(tsv_path, max_bytes=1024)

    assert "회의" in xml.text
    assert "일정 정리" in xml.text
    assert "공지" in html.text
    assert "hide" not in html.text
    assert "이름 | 금액" in tsv.text
    assert "# File: table.tsv" in tsv.text
    assert "| Row | Column 1 | Column 2 |" in tsv.text


def test_extract_csv_text_preserves_empty_cells_and_headers(tmp_path) -> None:
    path = tmp_path / "schedule.csv"
    path.write_text("과목,학년,교시\n파이썬,2,2A-2B\n정보보호이론,3,\n", encoding="utf-8")

    extracted = extract_local_file_text(path, max_bytes=4096)

    assert "# File: schedule.csv" in extracted.text
    assert "| Row | Column 1 | Column 2 | Column 3 |" in extracted.text
    assert "| 2 | 파이썬 | 2 | 2A-2B |" in extracted.text
    assert "| 3 | 정보보호이론 | 3 |  |" in extracted.text


@pytest.mark.parametrize("encoding", ["utf-8-sig", "cp949", "utf-16"])
def test_delimited_multiline_value_keeps_word_boundary(encoding):
    text = '이름\t값\r\n출하\t"단풍\r\n사과"'
    assert "| 2 | 출하 | 단풍 사과 |" in extract_bytes_text(text.encode(encoding), filename="report.tsv")


def test_xml_keeps_mixed_text_and_renders_table_cells_once():
    data = b"<p>before<b>bold</b>after<table><tr><td>cell</td></tr></table>last</p>"
    parsed = extract_bytes_text(data, filename="sample.xml")
    assert (
        parsed.index("before")
        < parsed.index("bold")
        < parsed.index("after")
        < parsed.index("cell")
        < parsed.index("last")
    )
    assert parsed.count("cell") == 1


def test_extract_pptx_text_from_slides_and_notes(tmp_path) -> None:
    path = tmp_path / "slides.pptx"
    path.write_bytes(
        make_zip_bytes(
            {
                "ppt/slides/slide1.xml": (
                    "<p:sld xmlns:p='p' xmlns:a='a'><a:t>발표 제목</a:t><a:t>핵심 본문</a:t></p:sld>"
                ),
                "ppt/notesSlides/notesSlide1.xml": (
                    "<p:notes xmlns:p='p' xmlns:a='a'><a:t>발표자 노트</a:t></p:notes>"
                ),
            }
        )
    )

    extracted = extract_local_file_text(path, max_bytes=4096)

    assert extracted.content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert "# File: slides.pptx" in extracted.text
    assert "## Slide 1" in extracted.text
    assert "### Speaker Notes 1" in extracted.text
    assert "발표 제목" in extracted.text
    assert "핵심 본문" in extracted.text
    assert "발표자 노트" in extracted.text


def test_extract_hwpx_text_from_xml_package(tmp_path) -> None:
    path = tmp_path / "report.hwpx"
    path.write_bytes(
        make_zip_bytes(
            {"Contents/section0.xml": ("<root><p>한글 문서 본문</p><table><cell>표 내용</cell></table></root>")}
        )
    )

    extracted = extract_local_file_text(path, max_bytes=4096)

    assert extracted.content_type == "application/vnd.hancom.hwpx"
    assert "한글 문서 본문" in extracted.text
    assert "표 내용" in extracted.text
    assert "## XML Section 1: Contents/section0.xml" in extracted.text


def test_extract_odt_and_ods_text(tmp_path) -> None:
    odt_path = tmp_path / "doc.odt"
    ods_path = tmp_path / "sheet.ods"
    odt_path.write_bytes(make_zip_bytes({"content.xml": "<root><p>오픈 문서 본문</p></root>"}))
    ods_path.write_bytes(make_zip_bytes({"content.xml": "<root><table><cell>스프레드시트 값</cell></table></root>"}))

    odt = extract_local_file_text(odt_path, max_bytes=4096)
    ods = extract_local_file_text(ods_path, max_bytes=4096)

    assert "오픈 문서 본문" in odt.text
    assert "스프레드시트 값" in ods.text
    assert "# File: doc.odt" in odt.text
    assert "# File: sheet.ods" in ods.text


def test_extract_docx_table_is_rendered_as_markdown(monkeypatch) -> None:
    class FakeCell:
        def __init__(self, text: str) -> None:
            self.text = text

    class FakeRow:
        def __init__(self, values: list[str]) -> None:
            self.cells = [FakeCell(value) for value in values]

    class FakeTable:
        rows = [FakeRow(["과목", "학년", "교시"]), FakeRow(["파이썬", "2", "2A-2B"])]

    class FakeParagraph:
        text = "문서 본문"

    class FakeDocument:
        paragraphs = [FakeParagraph()]
        tables = [FakeTable()]

    fake_docx = ModuleType("docx")
    fake_docx.Document = lambda _data: FakeDocument()
    monkeypatch.setitem(__import__("sys").modules, "docx", fake_docx)
    monkeypatch.setattr("docx.Document", lambda _data: FakeDocument())

    text = extract_bytes_text(b"fake", filename="report.docx")

    assert "# File: report.docx" in text
    assert "## Document Paragraphs" in text
    assert "### Table 1" in text
    assert "| 과목 | 학년 | 교시 |" in text
    assert "| 파이썬 | 2 | 2A-2B |" in text


def test_extract_xlsx_multiple_sheets_are_labeled(tmp_path) -> None:
    from openpyxl import Workbook

    path = tmp_path / "multi.xlsx"
    workbook = Workbook()
    first = workbook.active
    first.title = "시간표"
    first.append(["과목", "학년"])
    first.append(["파이썬", 2])
    second = workbook.create_sheet("강의실")
    second.append(["강의실", "건물"])
    second.append(["C404", "C"])
    workbook.save(path)

    extracted = extract_local_file_text(path, max_bytes=20000)

    assert "# File: multi.xlsx" in extracted.text
    assert "## Sheet: 시간표" in extracted.text
    assert "## Sheet: 강의실" in extracted.text
    assert "| 2 | 파이썬 | 2 |" in extracted.text


def test_extract_pdf_uses_layout_mode_and_page_labels(monkeypatch) -> None:
    class FakePage:
        def extract_text(self, *args, **kwargs) -> str:
            assert kwargs.get("extraction_mode") == "layout"
            return "컴퓨터공학_기본    파이썬    2    대면    6월 16일    2A    2B"

    class FakeReader:
        pages = [FakePage()]

        def __init__(self, _data) -> None:
            pass

    monkeypatch.setattr("assistant_bot.file_extractor.PdfReader", FakeReader)

    text = extract_bytes_text(b"%PDF", filename="schedule.pdf")

    assert "# File: schedule.pdf" in text
    assert "## Page 1" in text
    assert "컴퓨터공학_기본    파이썬    2" in text


class FakeAttachment:
    def __init__(self, filename: str, data: bytes) -> None:
        self.filename = filename
        self._data = data
        self.size = len(data)
        self.content_type = "text/plain"

    async def read(self) -> bytes:
        return self._data


def make_zip_bytes(files: dict[str, str]) -> bytes:
    output = BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return output.getvalue()


def test_legacy_korean_csv_retains_original_text():
    data = "이름,식별자\n박유진,AY-92".encode("cp949")
    text = extract_bytes_text(data, filename="old.csv")
    assert "박유진" in text and "AY-92" in text
