from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from openai import AsyncOpenAI

from assistant_bot.config import Config

T = TypeVar("T")


class OpenAIService:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            timeout=config.openai_timeout_seconds,
            max_retries=0,
        )

    async def text_response(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        temperature: float = 0.2,
    ) -> str:
        response = await self._with_retries(
            lambda: self.client.responses.create(
                model=model,
                instructions=instructions,
                input=input_text,
                temperature=temperature,
            )
        )

        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        return str(getattr(response, "output", "")).strip()

    async def embedding(self, text: str) -> list[float]:
        response = await self._with_retries(
            lambda: self.client.embeddings.create(
                model=self.config.embedding_model,
                input=text,
            )
        )
        if not response.data:
            return []
        return list(response.data[0].embedding)

    async def _with_retries(self, operation: Callable[[], Awaitable[T]]) -> T:
        attempts = max(1, self.config.openai_max_retries + 1)
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                return await operation()
            except Exception as error:
                last_error = error
                if attempt >= attempts - 1:
                    break
                await asyncio.sleep(min(0.25 * (2**attempt), 2.0))
        if last_error is not None:
            raise last_error
        raise RuntimeError("OpenAI 호출이 실행되지 않았습니다.")
