from __future__ import annotations

from assistant_bot.web_page_reader import ReadableHtmlParser, normalize_naver_blog_url


def test_readable_html_parser_extracts_readable_text_and_skips_noise() -> None:
    parser = ReadableHtmlParser()
    parser.feed(
        """
        <html>
          <head><title>문서 제목</title><style>.x{}</style><script>bad()</script></head>
          <body>
            <nav>메뉴</nav>
            <article>
              <h1>본문 제목</h1>
              <p>첫 번째 문장입니다.</p>
              <p>두 번째 문장입니다.</p>
            </article>
            <footer>푸터</footer>
          </body>
        </html>
        """
    )

    assert parser.title == "문서 제목"
    assert "본문 제목" in parser.text
    assert "첫 번째 문장입니다." in parser.text
    assert "bad()" not in parser.text
    assert "메뉴" not in parser.text


def test_normalize_naver_blog_url_uses_mobile_url_for_post() -> None:
    assert (
        normalize_naver_blog_url("https://blog.naver.com/example/223000000000")
        == "https://m.blog.naver.com/example/223000000000"
    )
    assert normalize_naver_blog_url("https://example.com/a") == "https://example.com/a"
