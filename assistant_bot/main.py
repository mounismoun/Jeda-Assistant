from __future__ import annotations

import logging
from pathlib import Path

from assistant_bot.bot import AssistantBot
from assistant_bot.config import load_config


def main() -> None:
    config = load_config()
    configure_logging(level_name=config.log_level, log_file=config.log_file)
    bot = AssistantBot(config)
    bot.run(config.discord_token)


def configure_logging(*, level_name: str = "INFO", log_file: str | None = None) -> None:
    level = parse_log_level(level_name)
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=handlers,
        force=True,
    )


def parse_log_level(level_name: str) -> int:
    normalized = level_name.strip().upper()
    level = logging.getLevelName(normalized)
    if isinstance(level, int):
        return level
    return logging.INFO


if __name__ == "__main__":
    main()
