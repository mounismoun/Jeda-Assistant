from assistant_bot.config import Config
from assistant_bot.model_selector import choose_model, detect_preference, judge_difficulty


def make_config() -> Config:
    return Config(
        discord_token="discord",
        discord_client_id=None,
        openai_api_key="openai",
        router_model="router",
        easy_model="easy",
        medium_model="medium",
        hard_model="hard",
        embedding_model="embedding",
        database_path=":memory:",
        max_attachment_bytes=1024,
        context_compression_chars=1000,
        retrieval_limit=4,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )


def test_detect_preference() -> None:
    assert detect_preference("빠르게 답해줘") == "fast"
    assert detect_preference("깊게 생각해서 답해줘") == "deep"


def test_judge_difficulty() -> None:
    assert judge_difficulty("안녕") == "easy"
    assert judge_difficulty("회의 문서 요약해줘") == "medium"
    assert judge_difficulty("상충되는 내용을 비교 분석해서 계획 세워줘") == "hard"


def test_choose_model_uses_preference_and_difficulty() -> None:
    config = make_config()

    assert choose_model(config, "빠르게 답해줘").model == "easy"
    assert choose_model(config, "깊게 생각해서 답해줘").model == "hard"
    assert choose_model(config, "회의 문서 요약해줘").model == "medium"
