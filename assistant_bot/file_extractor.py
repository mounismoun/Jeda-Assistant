from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

import discord
from pypdf import PdfReader

from assistant_bot.models import ExtractedAttachment

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


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
    lowered = attachment.filename.lower()

    if lowered.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(page.strip() for page in pages if page.strip()).strip()
    else:
        try:
            text = data.decode("utf-8").strip()
        except UnicodeDecodeError as error:
            raise ValueError(f"UTF-8 텍스트로 읽지 못했습니다: {attachment.filename}") from error

    if not text:
        raise ValueError(f"텍스트를 추출하지 못했습니다: {attachment.filename}")
    if not has_meaningful_text(text):
        raise ValueError(f"저장할 만한 텍스트를 찾지 못했습니다: {attachment.filename}")

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
    lowered = file_path.name.lower()
    if lowered.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(page.strip() for page in pages if page.strip()).strip()
        content_type = "application/pdf"
    else:
        try:
            text = data.decode("utf-8").strip()
        except UnicodeDecodeError as error:
            raise ValueError(f"UTF-8 텍스트로 읽지 못했습니다: {file_path.name}") from error
        content_type = "text/markdown" if lowered.endswith(".md") else "text/plain"

    if not text:
        raise ValueError(f"텍스트를 추출하지 못했습니다: {file_path.name}")
    if not has_meaningful_text(text):
        raise ValueError(f"저장할 만한 텍스트를 찾지 못했습니다: {file_path.name}")

    return ExtractedAttachment(
        filename=file_path.name,
        content_type=content_type,
        text=text,
    )


def has_meaningful_text(text: str) -> bool:
    return bool(re.search(r"[0-9A-Za-z가-힣]", text))
