from assistant_bot.capabilities import capability_prompt_block, help_lines, unsupported_message


def test_capability_prompt_lists_supported_and_unsupported_work() -> None:
    prompt = capability_prompt_block()

    assert "현재 코드로 제공되는 기능" in prompt
    assert "현재 코드로 제공되지 않는 기능" in prompt
    assert "개인 할 일 추가" in prompt
    assert "Discord 음성 통화" in prompt
    assert "실시간 인터넷 검색" in prompt


def test_help_and_unsupported_messages_disclose_limits() -> None:
    help_text = "\n".join(help_lines())
    unsupported = unsupported_message()

    assert "리마인더가 있는 할 일 저장" in help_text
    assert "음성 통화/녹음" in help_text
    assert "실시간 웹 검색" in help_text
    assert "현재 코드로 직접 실행할 수 없어요" in unsupported
    assert "Discord 서버 관리" in unsupported
