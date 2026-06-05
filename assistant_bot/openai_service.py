from __future__ import annotations

import asyncio
import base64
import json
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from openai import AsyncOpenAI, BadRequestError

from assistant_bot.config import Config
from assistant_bot.tool_calling import ToolSpec

T = TypeVar("T")


class OpenAIService:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            timeout=None,
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
        payload = {
            "model": model,
            "instructions": instructions,
            "input": input_text,
            "temperature": temperature,
        }
        payload = normalize_response_payload(payload)
        response = await self._with_retries(
            lambda: self._create_response_with_temperature_fallback(payload)
        )

        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        return str(getattr(response, "output", "")).strip()

    async def vision_text_response(
        self,
        *,
        model: str,
        instructions: str,
        prompt: str,
        images: list[tuple[str, bytes]],
        detail: str = "auto",
        temperature: float = 0.0,
    ) -> str:
        content: list[dict[str, object]] = [{"type": "input_text", "text": prompt}]
        for filename, data in images:
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{_image_mime_type(filename)};base64,{base64.b64encode(data).decode()}",
                    "detail": detail,
                }
            )
        payload = {
            "model": model,
            "instructions": instructions,
            "input": [{"role": "user", "content": content}],
            "temperature": temperature,
        }
        payload = normalize_response_payload(payload)
        response = await self._with_retries(
            lambda: self._create_response_with_temperature_fallback(payload)
        )
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()
        return str(getattr(response, "output", "")).strip()

    async def tool_response(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        tools: list[ToolSpec],
        temperature: float = 0.2,
        tool_choice: str | dict[str, object] = "auto",
        parallel_tool_calls: bool = False,
        max_tool_rounds: int = 3,
    ) -> str:
        if not tools:
            return await self.text_response(
                model=model,
                instructions=instructions,
                input_text=input_text,
                temperature=temperature,
            )

        tool_by_name = {tool.name: tool for tool in tools}
        input_items: list[Any] = [{"role": "user", "content": input_text}]
        for _ in range(max(1, max_tool_rounds)):
            payload = {
                "model": model,
                "instructions": instructions,
                "input": input_items,
                "tools": [tool.schema() for tool in tools],
                "tool_choice": tool_choice,
                "parallel_tool_calls": parallel_tool_calls,
                "temperature": temperature,
            }
            payload = normalize_response_payload(payload)
            response = await self._with_retries(
                lambda payload=payload: self._create_response_with_temperature_fallback(payload)
            )

            output_items = list(getattr(response, "output", []) or [])
            function_calls = [item for item in output_items if _response_item_value(item, "type") == "function_call"]
            if not function_calls:
                output_text = getattr(response, "output_text", None)
                if isinstance(output_text, str) and output_text.strip():
                    return output_text.strip()
                return str(output_items).strip()

            input_items.extend(output_items)
            for call in function_calls:
                name = str(_response_item_value(call, "name") or "")
                call_id = str(_response_item_value(call, "call_id") or "")
                arguments_text = str(_response_item_value(call, "arguments") or "{}")
                output = await self._run_tool_call(
                    name=name,
                    arguments_text=arguments_text,
                    tool_by_name=tool_by_name,
                )
                input_items.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": output,
                    }
                )

        return "도구 호출이 너무 여러 번 이어져서 안전하게 중단했어요. 요청을 조금 더 구체적으로 다시 말해 주세요."

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

    async def _run_tool_call(
        self,
        *,
        name: str,
        arguments_text: str,
        tool_by_name: dict[str, ToolSpec],
    ) -> str:
        tool = tool_by_name.get(name)
        if tool is None:
            return json.dumps(
                {"ok": False, "error": f"허용되지 않은 tool입니다: {name}"},
                ensure_ascii=False,
            )
        try:
            arguments = json.loads(arguments_text)
        except json.JSONDecodeError as error:
            return json.dumps(
                {"ok": False, "error": f"tool arguments JSON 파싱 실패: {error.msg}"},
                ensure_ascii=False,
            )
        if not isinstance(arguments, dict):
            return json.dumps(
                {"ok": False, "error": "tool arguments는 JSON object여야 합니다."},
                ensure_ascii=False,
            )
        try:
            result = await tool.run(arguments)
        except Exception as error:
            return json.dumps(
                {"ok": False, "error": f"tool 실행 실패: {error}"},
                ensure_ascii=False,
            )
        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=False)

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

    async def _create_response_with_temperature_fallback(self, payload: dict[str, Any]) -> Any:
        try:
            return await self.client.responses.create(**payload)
        except BadRequestError as error:
            if not _is_unsupported_temperature_error(error) or "temperature" not in payload:
                raise
            retry_payload = dict(payload)
            retry_payload.pop("temperature", None)
            return await self.client.responses.create(**retry_payload)


def _response_item_value(item: Any, field: str) -> Any:
    if isinstance(item, dict):
        return item.get(field)
    return getattr(item, field, None)


def _is_unsupported_temperature_error(error: BadRequestError) -> bool:
    message = str(error).lower()
    return "unsupported parameter" in message and "temperature" in message


def normalize_response_payload(payload: dict[str, Any]) -> dict[str, Any]:
    model = str(payload.get("model", "")).lower()
    if model.startswith("gpt-5"):
        normalized = dict(payload)
        normalized.pop("temperature", None)
        return normalized
    return payload


def _image_mime_type(filename: str) -> str:
    lowered = filename.lower()
    if lowered.endswith(".webp"):
        return "image/webp"
    if lowered.endswith(".png"):
        return "image/png"
    return "image/jpeg"
