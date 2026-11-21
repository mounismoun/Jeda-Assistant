from __future__ import annotations

import logging
import os
from pathlib import Path

from assistant_bot.bot import JedaDiscord
from assistant_bot.openai_service import Models, Settings
from assistant_bot.runtime import Engine
from assistant_bot.stores import JedaStore


def main() -> None:
    config = Settings.load()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("Discord에서 실행하려면 DISCORD_TOKEN을 설정하세요.")
    configure_logging()
    bot = JedaDiscord(Engine(config, JedaStore(config.database), Models(config)))
    bot.run(token)


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
