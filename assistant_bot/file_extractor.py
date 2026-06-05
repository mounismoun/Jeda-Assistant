from __future__ import annotations

import csv
import json
import re
import zipfile
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree

import discord
from pypdf import PdfReader

from assistant_bot.models import ExtractedAttachment

PLAIN_TEXT_EXTENSIONS = {".txt", ".md", ".log", ".text", ".rst", ".ini", ".conf", ".cfg"}
STRUCTURED_TEXT_EXTENSIONS = {".json", ".jsonl", ".yaml", ".yml", ".xml", ".html", ".htm", ".csv", ".tsv"}
DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".pptx", ".hwpx", ".odt", ".ods"}
LOCAL_TEXT_EXTENSIONS = PLAIN_TEXT_EXTENSIONS | STRUCTURED_TEXT_EXTENSIONS | DOCUMENT_EXTENSIONS
VISION_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif"}
SUPPORTED_EXTENSIONS = LOCAL_TEXT_EXTENSIONS | VISION_EXTENSIONS


def is_supported_attachment(filename: str) -> bool:
    lowered = filename.lower()
    return any(lowered.endswith(extension) for extension in SUPPORTED_EXTENSIONS)


async def extract_attachment_text(
    attachment: discord.Attachment,
    *,
    max_bytes: int,
) -> ExtractedAttachment:
    if not is_supported_attachment(attachment.filename):
        raise ValueError(f"지원하지 않는 파일 형식입니다: {attachment.filename}")
    if attachment.size > max_bytes:
        raise ValueError(f"파일이 너무 큽니다: {attachment.filename}")

    data = await attachment.read()
    text = extract_bytes_text(data, filename=attachment.filename)

    validate_extracted_text(text, attachment.filename)

    return ExtractedAttachment(
        filename=attachment.filename,
        content_type=attachment.content_type,
        text=text,
    )


def extract_local_file_text(path: str | Path, *, max_bytes: int) -> ExtractedAttachment:
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"파일을 찾지 못했습니다: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"일반 파일이 아닙니다: {file_path}")
    if not is_supported_attachment(file_path.name):
        raise ValueError(f"지원하지 않는 파일 형식입니다: {file_path.name}")
    if file_path.stat().st_size > max_bytes:
        raise ValueError(f"파일이 너무 큽니다: {file_path.name}")

    data = file_path.read_bytes()
    text = extract_bytes_text(data, filename=file_path.name)
    content_type = content_type_for_filename(file_path.name)

    validate_extracted_text(text, file_path.name)

    return ExtractedAttachment(
        filename=file_path.name,
        content_type=content_type,
        text=text,
    )


def has_meaningful_text(text: str) -> bool:
    return bool(re.search(r"[0-9A-Za-z가-힣]", text))


def is_vision_attachment(filename: str) -> bool:
    lowered = filename.lower()
    return any(lowered.endswith(extension) for extension in VISION_EXTENSIONS)


def extract_bytes_text(data: bytes, *, filename: str) -> str:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        return extract_pdf_text(data)
    if lowered.endswith(".docx"):
        return extract_docx_text(data)
    if lowered.endswith(".xlsx"):
        return extract_xlsx_text(data)
    if lowered.endswith(".pptx"):
        return extract_pptx_text(data)
    if lowered.endswith(".hwpx"):
        return extract_hwpx_text(data)
    if lowered.endswith(".odt"):
        return extract_odt_text(data)
    if lowered.endswith(".ods"):
        return extract_ods_text(data)
    if lowered.endswith(".csv"):
        return extract_csv_text(data)
    if lowered.endswith(".tsv"):
        return extract_tsv_text(data)
    if lowered.endswith(".json"):
        return extract_json_text(data)
    if lowered.endswith(".jsonl"):
        return extract_jsonl_text(data)
    if lowered.endswith((".yaml", ".yml")):
        return extract_yaml_text(data)
    if lowered.endswith(".xml"):
        return extract_xml_text(data)
    if lowered.endswith((".html", ".htm")):
        return extract_html_text(data)
    if is_vision_attachment(filename):
        raise ValueError(f"이미지 파일은 비전 OCR이 필요합니다: {filename}")
    try:
        return data.decode("utf-8").strip()
    except UnicodeDecodeError as error:
        raise ValueError(f"UTF-8 텍스트로 읽지 못했습니다: {filename}") from error


def extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(page.strip() for page in pages if page.strip()).strip()


def pdf_has_images(data: bytes) -> bool:
    reader = PdfReader(BytesIO(data))
    for page in reader.pages:
        resources = page.get("/Resources") or {}
        xobjects = resources.get("/XObject")
        if xobjects is None:
            continue
        xobject_map = xobjects.get_object()
        for xobject in xobject_map.values():
            candidate = xobject.get_object()
            if candidate.get("/Subtype") == "/Image":
                return True
    return False


def render_pdf_pages_to_png(data: bytes, *, filename: str) -> list[tuple[str, bytes]]:
    try:
        import fitz
    except ImportError as error:
        raise ValueError("스캔 PDF OCR에는 pymupdf 패키지가 필요합니다.") from error
    document = fitz.open(stream=data, filetype="pdf")
    images: list[tuple[str, bytes]] = []
    for index, page in enumerate(document, start=1):
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        images.append((f"{filename}-page-{index}.png", pixmap.tobytes("png")))
    return images


def extract_docx_text(data: bytes) -> str:
    try:
        from docx import Document
    except ImportError as error:
        raise ValueError("DOCX 분석에는 python-docx 패키지가 필요합니다.") from error
    document = Document(BytesIO(data))
    parts = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return "\n".join(parts).strip()


def extract_xlsx_text(data: bytes) -> str:
    try:
        from openpyxl import load_workbook
    except ImportError as error:
        raise ValueError("XLSX 분석에는 openpyxl 패키지가 필요합니다.") from error
    workbook = load_workbook(BytesIO(data), read_only=True, data_only=True)
    parts: list[str] = []
    for sheet in workbook.worksheets:
        parts.append(f"# Sheet: {sheet.title}")
        for row in sheet.iter_rows(values_only=True):
            values = [str(value).strip() for value in row if value is not None and str(value).strip()]
            if values:
                parts.append(" | ".join(values))
    return "\n".join(parts).strip()


def extract_pptx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            parts: list[str] = []
            slide_names = sorted(
                name
                for name in archive.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            )
            for index, name in enumerate(slide_names, start=1):
                slide_text = extract_zip_xml_text(archive, name)
                if slide_text:
                    parts.append(f"# Slide {index}\n{slide_text}")
            note_names = sorted(
                name
                for name in archive.namelist()
                if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")
            )
            for index, name in enumerate(note_names, start=1):
                note_text = extract_zip_xml_text(archive, name)
                if note_text:
                    parts.append(f"# Speaker Notes {index}\n{note_text}")
            return "\n\n".join(parts).strip()
    except zipfile.BadZipFile as error:
        raise ValueError("PPTX 구조를 읽지 못했습니다.") from error


def extract_hwpx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            xml_names = [
                name
                for name in archive.namelist()
                if name.lower().endswith(".xml")
                and (
                    name.startswith("Contents/")
                    or name.startswith("Sections/")
                    or "section" in name.casefold()
                    or "content" in name.casefold()
                )
            ]
            parts = [extract_zip_xml_text(archive, name) for name in sorted(xml_names)]
            return "\n\n".join(part for part in parts if part).strip()
    except zipfile.BadZipFile as error:
        raise ValueError("HWPX 구조를 읽지 못했습니다.") from error
    except ElementTree.ParseError as error:
        raise ValueError("HWPX XML을 읽지 못했습니다.") from error


def extract_odt_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            return extract_zip_xml_text(archive, "content.xml")
    except KeyError as error:
        raise ValueError("ODT 본문 XML을 찾지 못했습니다.") from error
    except zipfile.BadZipFile as error:
        raise ValueError("ODT 구조를 읽지 못했습니다.") from error


def extract_ods_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            return extract_zip_xml_text(archive, "content.xml")
    except KeyError as error:
        raise ValueError("ODS 본문 XML을 찾지 못했습니다.") from error
    except zipfile.BadZipFile as error:
        raise ValueError("ODS 구조를 읽지 못했습니다.") from error


def extract_csv_text(data: bytes) -> str:
    return extract_delimited_text(data, delimiter=",", format_name="CSV")


def extract_tsv_text(data: bytes) -> str:
    return extract_delimited_text(data, delimiter="\t", format_name="TSV")


def extract_delimited_text(data: bytes, *, delimiter: str, format_name: str) -> str:
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"{format_name}를 UTF-8 텍스트로 읽지 못했습니다.") from error
    rows = csv.reader(decoded.splitlines(), delimiter=delimiter)
    return "\n".join(" | ".join(cell.strip() for cell in row) for row in rows).strip()


def extract_json_text(data: bytes) -> str:
    try:
        payload = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("JSON을 읽지 못했습니다.") from error
    return json.dumps(payload, ensure_ascii=False, indent=2)


def extract_jsonl_text(data: bytes) -> str:
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("JSONL을 UTF-8 텍스트로 읽지 못했습니다.") from error
    lines = []
    for index, line in enumerate(decoded.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"JSONL {index}번째 줄을 읽지 못했습니다.") from error
        lines.append(json.dumps(payload, ensure_ascii=False, indent=2))
    return "\n\n".join(lines).strip()


def extract_yaml_text(data: bytes) -> str:
    try:
        import yaml
    except ImportError as error:
        raise ValueError("YAML 분석에는 PyYAML 패키지가 필요합니다.") from error
    try:
        payload = yaml.safe_load(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise ValueError("YAML을 읽지 못했습니다.") from error
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False).strip()


def extract_xml_text(data: bytes) -> str:
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as error:
        raise ValueError("XML을 읽지 못했습니다.") from error
    return xml_text(root)


def extract_html_text(data: bytes) -> str:
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("HTML을 UTF-8 텍스트로 읽지 못했습니다.") from error
    parser = VisibleTextHTMLParser()
    parser.feed(decoded)
    return "\n".join(parser.parts).strip()


def extract_zip_xml_text(archive: zipfile.ZipFile, name: str) -> str:
    root = ElementTree.fromstring(archive.read(name))
    return xml_text(root)


def xml_text(root: ElementTree.Element) -> str:
    parts = [text.strip() for text in root.itertext() if text and text.strip()]
    return "\n".join(parts).strip()


class VisibleTextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in {"script", "style", "noscript"}:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"script", "style", "noscript"} and self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._hidden_depth:
            return
        text = data.strip()
        if text:
            self.parts.append(text)


def validate_extracted_text(text: str, filename: str) -> None:
    if not text:
        raise ValueError(f"텍스트를 추출하지 못했습니다: {filename}")
    if not has_meaningful_text(text):
        raise ValueError(f"저장할 만한 텍스트를 찾지 못했습니다: {filename}")


def content_type_for_filename(filename: str) -> str:
    lowered = filename.lower()
    if lowered.endswith(".md"):
        return "text/markdown"
    if lowered.endswith((".log", ".text", ".rst", ".ini", ".conf", ".cfg")):
        return "text/plain"
    if lowered.endswith(".pdf"):
        return "application/pdf"
    if lowered.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if lowered.endswith(".xlsx"):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if lowered.endswith(".pptx"):
        return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    if lowered.endswith(".hwpx"):
        return "application/vnd.hancom.hwpx"
    if lowered.endswith(".odt"):
        return "application/vnd.oasis.opendocument.text"
    if lowered.endswith(".ods"):
        return "application/vnd.oasis.opendocument.spreadsheet"
    if lowered.endswith(".csv"):
        return "text/csv"
    if lowered.endswith(".tsv"):
        return "text/tab-separated-values"
    if lowered.endswith(".json"):
        return "application/json"
    if lowered.endswith(".jsonl"):
        return "application/x-ndjson"
    if lowered.endswith((".yaml", ".yml")):
        return "application/x-yaml"
    if lowered.endswith(".xml"):
        return "application/xml"
    if lowered.endswith((".html", ".htm")):
        return "text/html"
    if lowered.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif")):
        extension = lowered.rsplit(".", 1)[-1]
        if extension == "jpg":
            extension = "jpeg"
        if extension == "tif":
            extension = "tiff"
        return "image/" + extension
    return "text/plain"
