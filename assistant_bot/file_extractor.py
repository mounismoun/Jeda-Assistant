from __future__ import annotations

import csv
import json
import re
import zipfile
from codecs import BOM_UTF16_BE, BOM_UTF16_LE
from dataclasses import dataclass, field
from html.parser import HTMLParser
from io import BytesIO, StringIO
from pathlib import Path
from xml.etree import ElementTree

import discord
from pypdf import PdfReader


@dataclass(frozen=True)
class ExtractedAttachment:
    filename: str
    content_type: str | None
    text: str


STRUCTURED_MARKDOWN_VERSION = "structured-v1"
CODE_EXTENSIONS = set(".py .js .ts .tsx .java .c .cpp .h .go .rs .sql .sh .toml .diff .patch".split())
SUBTITLE_EXTENSIONS = {".srt", ".vtt"}
PLAIN_TEXT_EXTENSIONS = {".txt", ".md", ".log", ".text", ".rst", ".ini", ".conf", ".cfg"}
STRUCTURED_TEXT_EXTENSIONS = {".json", ".jsonl", ".yaml", ".yml", ".xml", ".html", ".htm", ".csv", ".tsv"}
DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".pptx", ".hwpx", ".odt", ".ods", ".odp"}
LOCAL_TEXT_EXTENSIONS = (
    CODE_EXTENSIONS | SUBTITLE_EXTENSIONS | PLAIN_TEXT_EXTENSIONS | STRUCTURED_TEXT_EXTENSIONS | DOCUMENT_EXTENSIONS
)
VISION_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".heic", ".heif"}
SUPPORTED_EXTENSIONS = LOCAL_TEXT_EXTENSIONS | VISION_EXTENSIONS


@dataclass
class ExtractedSection:
    heading: str
    blocks: list[str] = field(default_factory=list)


@dataclass
class StructuredExtractedDocument:
    filename: str
    sections: list[ExtractedSection] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_section(self, heading: str, *blocks: str) -> None:
        cleaned_blocks = [block.strip() for block in blocks if block and block.strip()]
        if cleaned_blocks:
            self.sections.append(ExtractedSection(heading=heading.strip(), blocks=cleaned_blocks))

    def render(self) -> str:
        parts = [f"# File: {self.filename}", f"<!-- extraction: {STRUCTURED_MARKDOWN_VERSION} -->"]
        if self.warnings:
            parts.append("## Extraction Warnings")
            parts.extend(f"- {warning}" for warning in self.warnings)
        for section in self.sections:
            parts.append(section.heading)
            parts.extend(section.blocks)
        return "\n\n".join(part for part in parts if part.strip()).strip()


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
        return extract_pdf_text(data, filename=filename)
    if lowered.endswith(".docx"):
        return extract_docx_text(data, filename=filename)
    if lowered.endswith(".xlsx"):
        return extract_xlsx_text(data, filename=filename)
    if lowered.endswith(".pptx"):
        return extract_pptx_text(data, filename=filename)
    if lowered.endswith(".hwpx"):
        return extract_hwpx_text(data, filename=filename)
    if lowered.endswith(".odt"):
        return extract_odt_text(data, filename=filename)
    if lowered.endswith(".ods"):
        return extract_ods_text(data, filename=filename)
    if lowered.endswith(".odp"):
        with zipfile.ZipFile(BytesIO(data)) as archive:
            return "\n\n".join(f"슬라이드 {i}\n{text}" for i, (_, text) in enumerate(odp_slides(archive), 1) if text)
    if Path(filename).suffix.lower() in CODE_EXTENSIONS | SUBTITLE_EXTENSIONS:
        value = decode_text(data, filename)
        if "\x00" in value:
            raise ValueError("첨부에서 텍스트를 읽을 수 없습니다.")
        return value
    if lowered.endswith(".csv"):
        return extract_csv_text(data, filename=filename)
    if lowered.endswith(".tsv"):
        return extract_tsv_text(data, filename=filename)
    if lowered.endswith(".json"):
        return extract_json_text(data)
    if lowered.endswith(".jsonl"):
        return extract_jsonl_text(data)
    if lowered.endswith((".yaml", ".yml")):
        return extract_yaml_text(data)
    if lowered.endswith(".xml"):
        return extract_xml_text(data, filename=filename)
    if lowered.endswith((".html", ".htm")):
        return extract_html_text(data, filename=filename)
    if is_vision_attachment(filename):
        raise ValueError(f"이미지 파일은 비전 OCR이 필요합니다: {filename}")
    try:
        return data.decode("utf-8").strip()
    except UnicodeDecodeError as error:
        raise ValueError(f"UTF-8 텍스트로 읽지 못했습니다: {filename}") from error


def extract_pdf_text(data: bytes, *, filename: str = "document.pdf") -> str:
    reader = PdfReader(BytesIO(data))
    document = StructuredExtractedDocument(filename=filename)
    for index, page in enumerate(reader.pages, start=1):
        text = ""
        try:
            text = page.extract_text(extraction_mode="layout") or ""
        except TypeError:
            text = page.extract_text() or ""
        except Exception:
            text = page.extract_text() or ""
        text = normalize_extracted_lines(text)
        if text:
            document.add_section(f"## Page {index}", text)
            if looks_like_collapsed_table(text):
                document.warnings.append(
                    f"Page {index}: table-like text may have lost column spacing during PDF extraction."
                )
    return document.render()


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


def extract_docx_text(data: bytes, *, filename: str = "document.docx") -> str:
    try:
        from docx import Document
    except ImportError as error:
        raise ValueError("DOCX 분석에는 python-docx 패키지가 필요합니다.") from error
    document = Document(BytesIO(data))
    extracted = StructuredExtractedDocument(filename=filename)
    paragraph_text = "\n\n".join(paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip())
    extracted.add_section("## Document Paragraphs", paragraph_text)
    for index, table in enumerate(document.tables, start=1):
        rows: list[list[str]] = []
        for row in table.rows:
            cells = [normalize_cell(cell.text) for cell in row.cells]
            if any(cells):
                rows.append(cells)
        table_text = markdown_table(rows)
        if table_text:
            extracted.add_section(f"### Table {index}", table_text)
    return extracted.render()


def extract_xlsx_text(data: bytes, *, filename: str = "workbook.xlsx") -> str:
    try:
        from openpyxl import load_workbook
    except ImportError as error:
        raise ValueError("XLSX 분석에는 openpyxl 패키지가 필요합니다.") from error
    workbook = load_workbook(BytesIO(data), read_only=True, data_only=True)
    document = StructuredExtractedDocument(filename=filename)
    for sheet in workbook.worksheets:
        rows: list[list[str]] = []
        for row in sheet.iter_rows(values_only=True):
            values = [normalize_cell(value) for value in row]
            if any(values):
                rows.append(values)
        table_text = markdown_table(rows, include_row_numbers=True)
        document.add_section(f"## Sheet: {sheet.title}", table_text)
    return document.render()


def extract_pptx_text(data: bytes, *, filename: str = "presentation.pptx") -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            document = StructuredExtractedDocument(filename=filename)
            slide_names = sorted(
                name for name in archive.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            )
            for index, name in enumerate(slide_names, start=1):
                slide_text = extract_zip_xml_text(archive, name)
                if slide_text:
                    document.add_section(f"## Slide {index}", slide_text)
            note_names = sorted(
                name
                for name in archive.namelist()
                if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")
            )
            for index, name in enumerate(note_names, start=1):
                note_text = extract_zip_xml_text(archive, name)
                if note_text:
                    document.add_section(f"### Speaker Notes {index}", note_text)
            return document.render()
    except zipfile.BadZipFile as error:
        raise ValueError("PPTX 구조를 읽지 못했습니다.") from error


def extract_hwpx_text(data: bytes, *, filename: str = "document.hwpx") -> str:
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
            document = StructuredExtractedDocument(filename=filename)
            for index, name in enumerate(sorted(xml_names), start=1):
                section_text = extract_zip_xml_text(archive, name)
                document.add_section(f"## XML Section {index}: {name}", section_text)
            return document.render()
    except zipfile.BadZipFile as error:
        raise ValueError("HWPX 구조를 읽지 못했습니다.") from error
    except ElementTree.ParseError as error:
        raise ValueError("HWPX XML을 읽지 못했습니다.") from error


def odp_slides(archive):
    content = ElementTree.fromstring(archive.read("content.xml"))
    for slide in content.findall(
        ".//{urn:oasis:names:tc:opendocument:xmlns:office:1.0}presentation/"
        "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}page"
    ):
        pictures = []
        for image in slide.iter("{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}image"):
            binary = image.find("{urn:oasis:names:tc:opendocument:xmlns:office:1.0}binary-data")
            encoded = binary.text if binary is not None else None
            if binary is not None:
                image.remove(binary)
            pictures.append((image.get("{http://www.w3.org/1999/xlink}href", ""), encoded))
        yield pictures, xml_text(slide)


def extract_odt_text(data: bytes, *, filename: str = "document.odt") -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            document = StructuredExtractedDocument(filename=filename)
            document.add_section("## Content", extract_zip_xml_text(archive, "content.xml"))
            return document.render()
    except KeyError as error:
        raise ValueError("ODT 본문 XML을 찾지 못했습니다.") from error
    except zipfile.BadZipFile as error:
        raise ValueError("ODT 구조를 읽지 못했습니다.") from error


def extract_ods_text(data: bytes, *, filename: str = "spreadsheet.ods") -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            document = StructuredExtractedDocument(filename=filename)
            document.add_section("## Content", extract_zip_xml_text(archive, "content.xml"))
            return document.render()
    except KeyError as error:
        raise ValueError("ODS 본문 XML을 찾지 못했습니다.") from error
    except zipfile.BadZipFile as error:
        raise ValueError("ODS 구조를 읽지 못했습니다.") from error


def extract_csv_text(data: bytes, *, filename: str = "data.csv") -> str:
    return extract_delimited_text(data, delimiter=",", format_name="CSV", filename=filename)


def extract_tsv_text(data: bytes, *, filename: str = "data.tsv") -> str:
    return extract_delimited_text(data, delimiter="\t", format_name="TSV", filename=filename)


def decode_text(data: bytes, label: str) -> str:
    try:
        if data.startswith((BOM_UTF16_LE, BOM_UTF16_BE)):
            return data.decode("utf-16")
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return data.decode("cp949")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label}를 UTF-8, UTF-16 또는 CP949 텍스트로 읽지 못했습니다.") from error


def extract_delimited_text(data: bytes, *, delimiter: str, format_name: str, filename: str) -> str:
    decoded = decode_text(data, format_name)
    reader = csv.reader(StringIO(decoded, newline=""), delimiter=delimiter)
    rows = [[normalize_cell(cell) for cell in row] for row in reader]
    rows = [row for row in rows if any(row)]
    document = StructuredExtractedDocument(filename=filename)
    document.add_section(f"## {format_name} Table", markdown_table(rows, include_row_numbers=True))
    return document.render()


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


def extract_xml_text(data: bytes, *, filename: str = "document.xml") -> str:
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as error:
        raise ValueError("XML을 읽지 못했습니다.") from error
    document = StructuredExtractedDocument(filename=filename)
    document.add_section(f"## XML Root: {strip_namespace(root.tag)}", xml_text(root))
    return document.render()


def extract_html_text(data: bytes, *, filename: str = "document.html") -> str:
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("HTML을 UTF-8 텍스트로 읽지 못했습니다.") from error
    parser = VisibleTextHTMLParser()
    parser.feed(decoded)
    document = StructuredExtractedDocument(filename=filename)
    document.add_section("## HTML Visible Text", "\n".join(parser.parts).strip())
    return document.render()


def extract_zip_xml_text(archive: zipfile.ZipFile, name: str) -> str:
    root = ElementTree.fromstring(archive.read(name))
    return xml_text(root)


def xml_text(root: ElementTree.Element) -> str:
    parts = list(xml_blocks(root))
    if parts:
        return "\n\n".join(parts).strip()
    return "\n".join(text.strip() for text in root.itertext() if text and text.strip()).strip()


def xml_blocks(root: ElementTree.Element) -> list[str]:
    blocks: list[str] = []
    table_index = 1
    pending = [root]
    while pending:
        element = pending.pop()
        if isinstance(element, str):
            if element.strip():
                blocks.append(element.strip())
            continue
        tag = strip_namespace(element.tag).casefold()
        if is_xml_table_tag(tag):
            table_rows = xml_table_rows(element)
            table_text = markdown_table(table_rows)
            if table_text:
                blocks.append(f"### Table {table_index}\n\n{table_text}")
                table_index += 1
                continue
        for child in reversed(element):
            if child.tail:
                pending.append(child.tail)
            pending.append(child)
        if element.text:
            pending.append(element.text)
    return blocks


def xml_table_rows(element: ElementTree.Element) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in element.iter():
        if not is_xml_row_tag(strip_namespace(row.tag).casefold()):
            continue
        cells = [
            " ".join(part.strip() for part in cell.itertext() if part and part.strip())
            for cell in row
            if is_xml_cell_tag(strip_namespace(cell.tag).casefold())
        ]
        if any(cells):
            rows.append(cells)
    return rows


def is_xml_table_tag(tag: str) -> bool:
    return "table" in tag and "cell" not in tag and "row" not in tag


def is_xml_row_tag(tag: str) -> bool:
    return tag in {"tr", "row", "table-row"} or tag.endswith("row")


def is_xml_cell_tag(tag: str) -> bool:
    return tag in {"td", "th", "cell", "table-cell"} or tag.endswith("cell")


def strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def normalize_extracted_lines(text: str) -> str:
    lines = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        cleaned = line.rstrip()
        if cleaned.strip():
            lines.append(cleaned)
        elif lines and lines[-1] != "":
            lines.append("")
    return "\n".join(lines).strip()


def normalize_cell(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def markdown_table(rows: list[list[str]], *, include_row_numbers: bool = False) -> str:
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized_rows = [row + [""] * (width - len(row)) for row in rows]
    if include_row_numbers:
        normalized_rows = [["Row", *[f"Column {index}" for index in range(1, width + 1)]]] + [
            [str(index), *row] for index, row in enumerate(normalized_rows, start=1)
        ]
    header = normalized_rows[0]
    body = normalized_rows[1:]
    if not body:
        body = [[""] * len(header)]
    lines = [
        "| " + " | ".join(escape_markdown_cell(cell) for cell in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(escape_markdown_cell(cell) for cell in row) + " |")
    return "\n".join(lines)


def escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def looks_like_collapsed_table(text: str) -> bool:
    compact_lines = [line for line in text.splitlines() if line.strip()]
    if len(compact_lines) < 8:
        return False
    long_dense = [line for line in compact_lines if len(line) > 120 and len(line.split()) <= 4]
    return len(long_dense) >= 3


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
    if lowered.endswith(".odp"):
        return "application/vnd.oasis.opendocument.presentation"
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
    if is_vision_attachment(filename):
        extension = lowered.rsplit(".", 1)[-1]
        if extension == "jpg":
            extension = "jpeg"
        if extension == "tif":
            extension = "tiff"
        return "image/" + extension
    return "text/plain"
