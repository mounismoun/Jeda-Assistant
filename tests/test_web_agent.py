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


def test_gallery_labels_stay_with_their_own_images():
    page = web_agent.Page("https://example.org/")
    page.feed(
        '<a href="one"><img src="1.png">One</a><a href="two"><img src="2.png">Two</a>'
        '<figure><img src="3.png"><figcaption>Three</figcaption></figure>'
    )
    first, second, third = page.images.values()
    assert (first["label"], second["label"], third["caption"]) == ("One", "Two", "Three")
    assert second["profile"].endswith("/two")


@pytest.mark.parametrize(("quote", "state"), [("Atlas II", "named_match"), ("Atlas IV", "unnamed")])
def test_unnamed_visual_match_follows_only_its_card_and_requires_verbatim_title(monkeypatch, quote, state):
    link = "https://example.org/products/42"
    page = dict(url=link, title="Example — Atlas II", text="An individual product")
    read = AsyncMock(return_value=page)
    monkeypatch.setattr(web_agent, "read_page", read)
    comparison = dict(
        verification="unnamed",
        page="https://example.org/gallery",
        match=2,
        candidates=[{"profile": "https://example.org/wrong"}, {"profile": link}],
    )
    model = SimpleNamespace(text=AsyncMock(return_value={"name": quote}))
    asyncio.run(web_agent.read_match_profile(comparison, None, model, SimpleNamespace(router="test")))
    read.assert_awaited_once_with(None, link)
    assert comparison["verification"] == state and comparison["profile_page"]["url"] == link


def test_negative_directory_comparison_can_open_a_linked_profile(monkeypatch):
    directory, profile = "https://example.org/gallery", "https://example.org/profile"
    read = AsyncMock(
        side_effect=[
            dict(kind="page", url=directory, text="Models", links={profile: "Profile"}, images=[{"url": directory}]),
            dict(kind="page", url=profile, text="Model A", links={}, images=[{"url": profile}]),
        ]
    )
    monkeypatch.setattr(web_agent, "read_page", read)
    compare = AsyncMock(side_effect=[dict(match=0, candidates=[]), dict(match=1, verification="named_match")])
    monkeypatch.setattr(web_agent, "compare_page", compare)
    task = dict(
        question="Which model?",
        start_urls=[directory],
        verify_urls=[directory],
        visual_history=[],
        visual_target="attachment",
    )
    model = SimpleNamespace(text=AsyncMock(return_value={"index": 0}))
    result = asyncio.run(
        web_agent.collect_web(model, SimpleNamespace(timeout=5, router="test"), task, load_original=AsyncMock())
    )
    assert [r["url"] for r in result["records"]] == [directory, profile]
    assert result["status"] == "success" and result["visual_attempt"]["matched"]


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


def test_visual_round_reuses_evidence_without_opening_tracking_alias(monkeypatch):
    prior = "https://example.org/series"
    attempt = dict(approach="roster", query="group members", hypothesis="members", seeds=[])
    monkeypatch.setattr(web_agent, "plan_visual_search", AsyncMock(return_value=attempt))
    search = AsyncMock(
        return_value=dict(
            kind="hosted_search",
            text="seen",
            urls=[prior + "?utm_source=other"],
            consulted=[],
            feeds=[],
            queries=["members list"],
        )
    )
    monkeypatch.setattr(web_agent, "discover", search)
    read = AsyncMock()
    monkeypatch.setattr(web_agent, "read_page", read)
    result = asyncio.run(
        web_agent.collect_web(
            SimpleNamespace(),
            SimpleNamespace(timeout=5),
            dict(question="question", start_urls=[], visual_target="photo", visual_history=[dict(pages=[prior])]),
            load_original=AsyncMock(),
        )
    )
    search.assert_awaited_once()
    read.assert_not_called()
    assert result["visual_attempt"]["queries"] == ["members list"]
    assert result["unread"] and result["records"][0]["text"] == "seen"


def test_visual_web_notes_batch_short_records_and_keep_sources(monkeypatch):
    monkeypatch.setattr(web_agent, "READ_BATCH", 100)
    records = [dict(id=i, text="blue " * 13 + str(i)) for i in range(12)]
    # Combined source text exceeds the prompt budget, but two small records fit in one request.
    ctx = dict(
        identify_image=True,
        current={"text": "identify"},
        corrections=[],
        referenced_work=[],
        results=[dict(records=records)],
    )
    model = SimpleNamespace(text=AsyncMock(return_value=dict(excerpts=["blue"], note="shared")))
    delivered = asyncio.run(prepare_web_evidence(ctx, model, "final", "low"))
    assert len(delivered) == 12
    assert 0 < model.text.await_count < 11
    assert ctx["web_reading_notes"][0]["attribution"][:2] == [["blue", "0.0", 1], ["blue", "0.1", 1]]


def test_reviewer_verifies_new_product_manual_without_another_discovery(monkeypatch):
    url = "https://manufacturer.example/manual"
    plan = AsyncMock()
    monkeypatch.setattr(web_agent, "plan_visual_search", plan)
    monkeypatch.setattr(web_agent, "discover", AsyncMock(side_effect=AssertionError("unexpected search")))
    read = AsyncMock(return_value=dict(kind="page", url=url, links={}, images=[{"url": url}], text="Model X"))
    monkeypatch.setattr(web_agent, "read_page", read)
    monkeypatch.setattr(web_agent, "compare_page", AsyncMock(return_value={"match": 1}))
    result = asyncio.run(
        web_agent.collect_web(
            SimpleNamespace(),
            SimpleNamespace(timeout=5),
            dict(
                question="compare the serial plate",
                start_urls=[url],
                verify_urls=[url],
                visual_history=[],
                visual_target="machine",
            ),
            load_original=AsyncMock(),
        )
    )
    assert [a["action"] for a in result["actions"]] == ["open"]
    assert result["visual_attempt"]["matched"]
    plan.assert_not_called()


@pytest.mark.parametrize("error", [TimeoutError(), ValueError("max_output_tokens")])
def test_incomplete_visual_plan_uses_available_search_and_skips_second_slow_plan(monkeypatch, error):
    plan = AsyncMock(side_effect=error)
    monkeypatch.setattr(web_agent, "plan_visual_search", plan)
    search = AsyncMock(return_value=dict(kind="hosted_search", text="no candidate", urls=[], consulted=[], feeds=[]))
    monkeypatch.setattr(web_agent, "discover", search)
    task = dict(question="camera lens engraving", start_urls=[], visual_target="lens", visual_history=[])
    for query in ("camera lens engraving", "museum photographic equipment catalogue"):
        task["question"] = query
        result = asyncio.run(
            web_agent.collect_web(SimpleNamespace(), SimpleNamespace(timeout=5), task, load_original=AsyncMock())
        )
        task["visual_history"].append(result["visual_attempt"])
        assert result["actions"][0]["term"] == query
    assert search.await_count == 2
    plan.assert_awaited_once()


def test_render_sources_uses_verified_target_once_and_preserves_pinned_line():
    from assistant_bot.web_agent import render_web_citations

    page = "https://example.org/manual"
    pinned = "https://github.com/owner/repo/blob/commit/A.kt#L33"
    rendered, valid = render_web_citations(f"[근거 1]({page})와 [근거 2]", [page, pinned])
    assert valid and rendered.count(page) == 1 and rendered.count(pinned) == 1
    assert render_web_citations(page + "#section", [page]) == (page, True)
    assert not render_web_citations(pinned.replace("L33", "L34"), [pinned])[1]
    assert not render_web_citations("[근거 7]", [page])[1]
