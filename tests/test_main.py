import logging

from assistant_bot.main import configure_logging, parse_log_level


def test_parse_log_level_defaults_unknown_to_info() -> None:
    assert parse_log_level("debug") == logging.DEBUG
    assert parse_log_level("not-real") == logging.INFO


def test_configure_logging_writes_to_file(tmp_path) -> None:
    log_path = tmp_path / "logs" / "assistant.log"

    configure_logging(level_name="DEBUG", log_file=str(log_path))
    logger = logging.getLogger("assistant-test")
    logger.debug("로그 파일 테스트")
    for handler in logging.getLogger().handlers:
        handler.flush()

    assert "로그 파일 테스트" in log_path.read_text(encoding="utf-8")
