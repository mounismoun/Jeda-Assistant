import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from assistant_bot import web_agent
from assistant_bot.web_agent import prepare_web_evidence, read_page, repo_file


def test_html_links_and_code_preserve_displayed_source():
    url = "https://example.org/manual/"
    body = '<h1>Manual</h1><pre>x\n    y</pre><table><tr><th>K</th><td>12 kg</td></tr></table><a href="next">More</a>'
    reader = SimpleNamespace(get=AsyncMock(return_value=(url, "text/html", body)))
    record = asyncio.run(read_page(reader, url))
    assert "x\n    y" in record["text"] and "K\t12 kg" in record["text"]
    assert record["links"] == {"https://example.org/manual/next": "More"}


@pytest.mark.parametrize(
    "ref, paths, line, expected",
    [
        ("v1", ["src/A.kt"], 2, "    sample()"),
        ("", ["src/A.kt"], 3, ""),
        ("", ["src/A.kt"], 4, None),
        ("", ["src/A.kt", "tests/A.kt"], 2, None),
    ],
)
def test_github_line_comes_from_a_pinned_file(ref, paths, line, expected):
    api = "https://api.github.com/repos/test/demo"
    commit = "a" * 40
    tree = {"tree": [{"type": "blob", "path": path} for path in paths], "truncated": False}
    reader = SimpleNamespace(
        get=AsyncMock(
            side_effect=[
                ("", "", json.dumps([{"sha": commit}])),
                ("", "", json.dumps(tree)),
                ("", "", "first\n    sample()\n\n"),
            ]
        )
    )
    record = asyncio.run(repo_file(reader, "https://github.com/test/demo", "A.kt", ref, line))
    assert reader.get.await_args_list[0].args[0].startswith(api + "/commits?")
    if ref:
        assert "sha=v1" in reader.get.await_args_list[0].args[0]
    if len(paths) > 1:
        assert record["kind"] == "candidates" and json.loads(record["text"]) == paths
        assert reader.get.await_count == 2
    elif expected is None:
        assert record["missing_line"] and record["line_count"] == 3
    else:
        assert record["line_text"] == expected and record["url"].endswith(f"{commit}/src/A.kt#L{line}")


def test_final_model_reads_each_chunk_and_keeps_conflicting_values(monkeypatch):
    monkeypatch.setattr(web_agent, "READ_BATCH", 25)
    value = "Allowance is 17 units.\n"
    other = "Exception: 23 units."
    ctx = {
        "current": {"text": "두 한도를 대조해줘"},
        "corrections": [],
        "referenced_work": [],
        "results": [
            {"records": [{"id": 1, "kind": "page", "text": value * 20}, {"id": 2, "kind": "page", "text": other}]}
        ],
    }
    review = AsyncMock(return_value={"excerpts": ["17 units", "fabricated"], "note": "17"})
    read = asyncio.run(prepare_web_evidence(ctx, SimpleNamespace(text=review), "final-model", "low"))
    bodies = [json.loads(c.args[3])["chunk"]["body"] for c in review.await_args_list] + [
        c["body"] for c in ctx["web_content"]
    ]
    assert "".join(bodies) == value * 20 + other and len(read) == len(bodies)
    assert all(c.args[0] == "final-model" for c in review.await_args_list)
    assert all("fabricated" not in n["excerpts"] for n in ctx["web_reading_notes"])
    assert read[-1]["source"] == "0.2"


def test_partial_read_reports_missing_chunks(monkeypatch):
    monkeypatch.setattr(web_agent, "READ_BATCH", 12)
    ctx = {
        "current": {"text": "질문"},
        "corrections": [],
        "referenced_work": [],
        "results": [{"records": [{"id": 1, "text": "one two three four five " * 24}]}],
    }
    model = SimpleNamespace(text=AsyncMock(side_effect=TimeoutError()))
    delivered = asyncio.run(prepare_web_evidence(ctx, model, "final", "low"))
    assert len(delivered) == 1 and ctx["web_unread_chunks"]
    assert len(delivered) + len(ctx["web_unread_chunks"]) == ctx["results"][0]["records"][0]["chunks"]


def test_render_sources_uses_verified_target_once_and_preserves_pinned_line():
    from assistant_bot.web_agent import render_web_citations

    page = "https://example.org/manual"
    pinned = "https://github.com/owner/repo/blob/commit/A.kt#L33"
    rendered, valid = render_web_citations(f"[근거 1]({page})와 [근거 2]", [page, pinned])
    assert valid and rendered.count(page) == 1 and rendered.count(pinned) == 1
    assert render_web_citations(page + "#section", [page]) == (page, True)
    assert not render_web_citations(pinned.replace("L33", "L34"), [pinned])[1]
    assert not render_web_citations("[근거 7]", [page])[1]
