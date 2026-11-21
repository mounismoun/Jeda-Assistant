from assistant_bot.text_utils import chunk_text, cosine_similarity, split_discord_message


def test_chunk_text_preserves_content_order() -> None:
    text = "문장 하나입니다. " * 300
    chunks = chunk_text(text, max_chars=300, overlap_chars=30)

    assert len(chunks) > 1
    assert chunks[0].startswith("문장 하나입니다.")
    assert all(len(chunk) <= 330 for chunk in chunks)


def test_cosine_similarity_orders_related_vectors() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) > cosine_similarity(
        [1.0, 0.0], [0.0, 1.0]
    )


def test_split_discord_message_respects_limit() -> None:
    parts = split_discord_message("가" * 4500, limit=1900)

    assert len(parts) == 3
    assert all(len(part) <= 1900 for part in parts)



def test_discord_moves_the_whole_list_item_to_the_next_message():
    first = "- BPE는 자주 나오는 조각을 합칩니다."
    second = "- WordPiece는 현재 위치부터 가장 긴 조각을 찾습니다."
    assert split_discord_message(first + "\n" + second, limit=42) == [first, second]


def test_discord_keeps_even_an_early_newline_and_an_exact_fit_line():
    line = "긴 줄 " * 9 + "끝"
    assert split_discord_message("제목\r\n" + line + "\n끝", limit=len(line)) == ["제목", line, "끝"]


def test_discord_splits_an_oversized_line_after_a_sentence_before_using_spaces():
    first = "첫 문장입니다."
    second = "두 번째 문장이 여기서 끝납니다."
    assert split_discord_message(first + " " + second, limit=22) == [first, second]


def test_discord_keeps_citations_and_code_indentation():
    link = "[내용 확인](https://example.com)"
    assert split_discord_message("확인할 자료 " + link, limit=30) == ["확인할 자료", link]
    lines = ["    step_one()", "    step_two()"]
    source = "```py\n" + "\n".join(lines) + "\n```"
    assert split_discord_message(source, limit=24) == [f"```py\n{line}\n```" for line in lines]


def test_discord_hard_split_keeps_supplementary_characters_intact():
    text = "😀" * 24
    parts = split_discord_message(text, limit=15)
    assert "".join(parts) == text
    assert all(len(p.encode("utf-16-le")) <= 30 for p in parts)
