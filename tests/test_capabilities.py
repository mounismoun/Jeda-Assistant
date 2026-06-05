from assistant_bot.capabilities import capability_prompt_block, help_lines, unsupported_message


def test_capability_prompt_lists_supported_and_unsupported_work() -> None:
    prompt = capability_prompt_block()

    assert "현재 코드로 제공되는 기능" in prompt
    assert "현재 코드로 제공되지 않는 기능" in prompt
    assert "개인 할 일 추가" in prompt
    assert "현재 날짜와 시간 안내" in prompt
    assert "Discord 음성 통화" in prompt
    assert "Naver Search API 기반 웹검색" in prompt
    assert "동적 페이지 렌더링 우회" in prompt


def test_help_and_unsupported_messages_disclose_limits() -> None:
    help_text = "\n".join(help_lines())
    unsupported = unsupported_message()

    assert "할 일과 분리된 DM 알림 예약" in help_text
    assert "웹검색 결과와 선별 본문을 출처와 함께 요약" in help_text
    assert "현재 날짜와 시간 확인" in help_text
    assert "음성 통화/녹음" in help_text
    assert "로그인이나 웹 조작이 필요한 페이지 처리" in help_text
    assert "현재 코드로 직접 실행할 수 없어요" in unsupported
    assert "Naver 웹검색" in unsupported
    assert "Discord 서버 관리" in unsupported
