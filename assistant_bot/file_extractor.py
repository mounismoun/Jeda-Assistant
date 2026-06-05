from __future__ import annotations

import csv
import re
from io import BytesIO
from pathlib import Path

import discord
from pypdf import PdfReader

from assistant_bot.models import ExtractedAttachment

LOCAL_TEXT_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".xlsx", ".csv"}
VISION_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
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
    if lowered.endswith(".csv"):
        return extract_csv_text(data)
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


def extract_csv_text(data: bytes) -> str:
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("CSV를 UTF-8 텍스트로 읽지 못했습니다.") from error
    rows = csv.reader(decoded.splitlines())
    return "\n".join(" | ".join(cell.strip() for cell in row) for row in rows).strip()


def validate_extracted_text(text: str, filename: str) -> None:
    if not text:
        raise ValueError(f"텍스트를 추출하지 못했습니다: {filename}")
    if not has_meaningful_text(text):
        raise ValueError(f"저장할 만한 텍스트를 찾지 못했습니다: {filename}")


def content_type_for_filename(filename: str) -> str:
    lowered = filename.lower()
    if lowered.endswith(".md"):
        return "text/markdown"
    if lowered.endswith(".pdf"):
        return "application/pdf"
    if lowered.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if lowered.endswith(".xlsx"):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if lowered.endswith(".csv"):
        return "text/csv"
    if lowered.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return "image/" + ("jpeg" if lowered.endswith((".jpg", ".jpeg")) else lowered.rsplit(".", 1)[-1])
    return "text/plain"
