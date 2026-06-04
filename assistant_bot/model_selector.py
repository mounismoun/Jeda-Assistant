from __future__ import annotations

from assistant_bot.config import Config
from assistant_bot.models import Difficulty, ModelChoice, Preference


def detect_preference(text: str) -> Preference:
    lowered = text.lower()
    if any(word in lowered for word in ["빠르게", "빨리", "간단히", "fast"]):
        return "fast"
    if any(word in lowered for word in ["저렴", "싸게", "비용", "cheap"]):
        return "cheap"
    if any(word in lowered for word in ["정확", "꼼꼼", "검증", "precise"]):
        return "precise"
    if any(word in lowered for word in ["깊게", "자세히", "생각해서", "deep"]):
        return "deep"
    return "balanced"


def judge_difficulty(text: str, context_chars: int = 0, result_count: int = 0) -> Difficulty:
    lowered = text.lower()
    hard_markers = ["계획", "비교", "종합", "분석", "설계", "충돌", "상충", "deep", "architecture"]
    medium_markers = ["요약", "정리", "여러", "근거", "문서", "파일", "회의", "summary"]

    if context_chars > 8000 or result_count >= 6 or any(marker in lowered for marker in hard_markers):
        return "hard"
    if context_chars > 2500 or result_count >= 3 or any(marker in lowered for marker in medium_markers):
        return "medium"
    return "easy"


def choose_model(config: Config, text: str, context_chars: int = 0, result_count: int = 0) -> ModelChoice:
    preference = detect_preference(text)
    difficulty = judge_difficulty(text, context_chars=context_chars, result_count=result_count)

    if preference in {"fast", "cheap"}:
        return ModelChoice("easy", config.easy_model, f"{preference} 선호가 있어 저비용 모델을 선택")
    if preference == "deep":
        return ModelChoice("hard", config.hard_model, "깊은 추론 선호가 있어 고난도 모델을 선택")
    if preference == "precise" and difficulty == "easy":
        difficulty = "medium"

    model_by_difficulty = {
        "easy": config.easy_model,
        "medium": config.medium_model,
        "hard": config.hard_model,
    }
    return ModelChoice(difficulty, model_by_difficulty[difficulty], f"{difficulty} 난이도로 판단")

