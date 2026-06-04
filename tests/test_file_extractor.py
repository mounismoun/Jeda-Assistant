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
    assert not is_supported_attachment("image.png")
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

    with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
        extract_local_file_text(path, max_bytes=1024)


class FakeAttachment:
    def __init__(self, filename: str, data: bytes) -> None:
        self.filename = filename
        self._data = data
        self.size = len(data)
        self.content_type = "text/plain"

    async def read(self) -> bytes:
        return self._data
