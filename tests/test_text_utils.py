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

