import zipfile
from io import BytesIO

import pytest

from assistant_bot.file_extractor import (
    extract_attachment_text,
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


def test_extract_pptx_text_from_slides_and_notes(tmp_path) -> None:
    path = tmp_path / "slides.pptx"
    path.write_bytes(
        make_zip_bytes(
            {
                "ppt/slides/slide1.xml": (
                    "<p:sld xmlns:p='p' xmlns:a='a'>"
                    "<a:t>발표 제목</a:t><a:t>핵심 본문</a:t>"
                    "</p:sld>"
                ),
                "ppt/notesSlides/notesSlide1.xml": (
                    "<p:notes xmlns:p='p' xmlns:a='a'><a:t>발표자 노트</a:t></p:notes>"
                ),
            }
        )
    )

    extracted = extract_local_file_text(path, max_bytes=4096)

    assert extracted.content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert "발표 제목" in extracted.text
    assert "핵심 본문" in extracted.text
    assert "발표자 노트" in extracted.text


def test_extract_hwpx_text_from_xml_package(tmp_path) -> None:
    path = tmp_path / "report.hwpx"
    path.write_bytes(
        make_zip_bytes(
            {
                "Contents/section0.xml": (
                    "<root><p>한글 문서 본문</p><table><cell>표 내용</cell></table></root>"
                )
            }
        )
    )

    extracted = extract_local_file_text(path, max_bytes=4096)

    assert extracted.content_type == "application/vnd.hancom.hwpx"
    assert "한글 문서 본문" in extracted.text
    assert "표 내용" in extracted.text


def test_extract_odt_and_ods_text(tmp_path) -> None:
    odt_path = tmp_path / "doc.odt"
    ods_path = tmp_path / "sheet.ods"
    odt_path.write_bytes(make_zip_bytes({"content.xml": "<root><p>오픈 문서 본문</p></root>"}))
    ods_path.write_bytes(make_zip_bytes({"content.xml": "<root><table><cell>스프레드시트 값</cell></table></root>"}))

    odt = extract_local_file_text(odt_path, max_bytes=4096)
    ods = extract_local_file_text(ods_path, max_bytes=4096)

    assert "오픈 문서 본문" in odt.text
    assert "스프레드시트 값" in ods.text


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
