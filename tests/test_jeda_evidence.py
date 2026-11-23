import asyncio
import json
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock

import fitz
import pytest
from PIL import Image
from pptx import Presentation

from assistant_bot.document_reader import read_parts
from assistant_bot.openai_service import CitationMismatch, Models, extract_web


def test_grouped_slide_shapes_and_notes_keep_their_location():
    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    shapes = slide.shapes.add_group_shape().shapes.add_group_shape().shapes
    shapes.add_textbox(0, 0, 300, 200).text = "group value"
    slide.notes_slide.notes_text_frame.text = "notes value"
    data = BytesIO()
    deck.save(data)
    parts = list(read_parts("deck.pptx", data.getvalue()))
    assert [(p.location, p.text) for p in parts] == [
        ("deck.pptx · 슬라이드 1", "group value"),
        ("deck.pptx · 슬라이드 1 · 발표자 노트", "notes value"),
    ]


def test_multiframe_image_selection_and_unread_range():
    frames = [Image.new("RGB", (5, 5), (i, 0, 0)) for i in range(17)]
    data = BytesIO()
    frames[0].save(data, format="TIFF", save_all=True, append_images=frames[1:])
    parts = list(read_parts("pages.tiff", data.getvalue()))
    assert sum(bool(p.image) for p in parts) == 16
    assert parts[-1].unread and "17–17" in parts[-1].text
    (selected,) = read_parts("pages.tiff", data.getvalue(), first=17)
    with Image.open(BytesIO(selected.image)) as image:
        assert image.getpixel((0, 0)) == (16, 0, 0)


def test_plain_text_can_contain_the_extractor_version():
    (part,) = read_parts("manifest.txt", b"format: structured-v1\nmanifest ID: JX-6352")
    assert "JX-6352" in part.text


def test_chapter_excludes_other_chapters_and_includes_vector_chart():
    with fitz.open() as doc:
        for i in [3, 4, 5]:
            page = doc.new_page()
            page.insert_text((30, 40), f"Chapter {i}")
            if i == 4:
                page.draw_line((50, 90), (150, 60))
        doc.set_toc([[1, f"Chapter {i}", i - 2] for i in [3, 4, 5]])
        data = doc.tobytes()
    parts = list(read_parts("manual.pdf", data, chapter=4))
    assert len(parts) == 1
    assert "Chapter 4" in parts[0].text and parts[0].image
    assert "2쪽" in parts[0].location


@pytest.mark.parametrize(
    "output",
    [
        [],
        [{"type": "message", "content": [{"type": "output_text", "text": "출처 없는 결론"}]}],
        [{"type": "web_search_call", "status": "completed", "action": {"type": "search"}}],
    ],
)
def test_unverified_web_answer_rejected(output):
    with pytest.raises(ValueError):
        extract_web({"output": output})


def test_search_result_is_not_direct_url_access():
    with pytest.raises(ValueError, match="직접 열람"):
        extract_web(
            {"output": [{"type": "web_search_call", "status": "completed", "action": {"type": "search"}}]},
            ["https://example.org/manual"],
        )


def cited_page(body, url):
    return {
        "output": [
            {"type": "web_search_call", "status": "completed", "action": {"type": "search"}},
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": body,
                        "annotations": [{"type": "url_citation", "url": url, "start_index": 0, "end_index": len(body)}],
                    }
                ],
            },
        ]
    }


def test_existing_citation_uses_verified_url_once():
    url = "https://example.org/manual?id=3&utm_source=openai"
    body = "내용은 없습니다. [공식 문서](https://example.org/manual?id=3#section)"
    result = extract_web(cited_page(body, url))
    assert result["text"] == f"내용은 없습니다. [공식 문서]({url})"
    assert result["urls"] == [url]


def test_direct_page_requires_both_open_and_citation_for_the_same_document():
    page = "https://example.org/manual?id=3"
    response = cited_page("결론", page + "&utm_source=example")
    response["output"][0]["action"] = {"type": "open_page", "url": page}
    assert extract_web(response, [page + "#details"])["urls"]
    with pytest.raises(ValueError, match="직접 열람"):
        extract_web(response, ["https://example.org/manual?id=4#details"])
    response["output"][0]["action"]["url"] = "https://example.org/manual?id=4"
    with pytest.raises(ValueError, match="직접 인용"):
        extract_web(response, ["https://example.org/manual?id=4"])


@pytest.mark.parametrize("unverified", ["https://example.org/manual?id=4", "https://other.example/manual?id=3"])
def test_citation_cannot_substitute_another_source(unverified):
    with pytest.raises(ValueError, match="대조"):
        extract_web(cited_page(f"결과 [자료]({unverified})", "https://example.org/manual?id=3"))


def test_repeated_source_only_link_is_omitted_but_new_claims_are_kept():
    url = "https://example.org/manual?id=3"
    first = f"첫 근거 [문서]({url})"
    second = f"[문서]({url})에서 확인한 두 번째 조건."
    response = cited_page(f"{first}\n\n공식 원문: [문서]({url})\n\n{second}", url)
    assert extract_web(response)["text"] == f"{first}\n\n{second}"


def test_adjacent_source_badge_does_not_repeat_verified_link():
    url = "https://example.org/manual"
    link = f"[공식 원문]({url})"
    body = f"{link} ([example.org]({url}))"
    assert extract_web(cited_page(body, url))["text"] == link


@pytest.mark.parametrize("recovers", [True, False])
def test_search_rechecks_mismatched_citation_only_once(recovers):
    source = "https://example.org/manual"
    invalid = cited_page("본문 [다른 문서](https://elsewhere.example/other)", source)
    valid = cited_page("검증한 결론", source)
    create = AsyncMock(
        side_effect=[
            SimpleNamespace(content=json.dumps({"status": "completed", **body}).encode())
            for body in (invalid, valid if recovers else invalid)
        ]
    )
    model = object.__new__(Models)
    model.client = SimpleNamespace(responses=SimpleNamespace(with_raw_response=SimpleNamespace(create=create)))
    task = model.search("model", "low", "근거 확인", "원래 질문")
    if recovers:
        result = asyncio.run(task)
        assert source in result["text"] and "elsewhere" not in result["text"]
    else:
        with pytest.raises(CitationMismatch):
            asyncio.run(task)
    assert create.await_count == 2
    payload = create.await_args.kwargs["input"]
    assert source in payload and "원래 질문" in payload and "elsewhere" not in payload


def test_source_file_locations_and_whitespace():
    from assistant_bot.file_extractor import CODE_EXTENSIONS

    source = "\n" * 100 + "    return 17"
    for ext in CODE_EXTENSIONS:
        parts = list(read_parts("sample" + ext.upper(), source.encode()))
        assert parts[-1].text == "101 |     return 17"
        assert "101–101행" in parts[-1].location


@pytest.mark.parametrize("ext", ["heic", "heif"])
def test_heif_image_reaches_vision_reader(ext):
    data = BytesIO()
    Image.new("RGB", (128, 80), "red").save(data, format="HEIF")
    (part,) = read_parts("camera." + ext, data.getvalue())
    with Image.open(BytesIO(part.image)) as decoded:
        assert decoded.size == (128, 80) and decoded.getpixel((50, 40))[0] > 230


def test_vtt_ignores_note_and_keeps_cue_time_with_text():
    data = "WEBVTT\n\nNOTE not a cue\n00:11.000 --> 00:13.000\nignore\n\n\nA\n00:14.000 --> 00:16.000\n안녕"
    (part,) = read_parts("video.vtt", data.encode("utf-16"))
    assert part.text == "안녕" and "00:14.000 --> 00:16.000" in part.location


def test_odp_inline_picture_stays_with_slide_without_base64_in_text():
    import base64
    import zipfile

    data, picture = BytesIO(), BytesIO()
    Image.new("RGB", (16, 16), "red").save(picture, "PNG")
    encoded = base64.b64encode(picture.getvalue()).decode()
    with zipfile.ZipFile(data, "w") as archive:
        archive.writestr(
            "content.xml",
            f"""<o:document-content xmlns:o="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
          xmlns:d="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"><o:body><o:presentation>
          <d:page><title>First</title></d:page><d:page><title>Second</title><d:image><o:binary-data>{encoded}</o:binary-data>
          </d:image></d:page></o:presentation></o:body></o:document-content>""",
        )
    first, second, image = read_parts("test.odp", data.getvalue())
    assert first.text == "First" and second.text == "Second"
    assert image.image and image.location == second.location == "test.odp · 슬라이드 2"
