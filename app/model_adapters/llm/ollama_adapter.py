
from typing import Any
import json

import httpx

from app.core.logging import get_logger
from app.model_adapters.base import BaseLLMAdapter


logger = get_logger("nova.llm.ollama")


class OllamaAdapter(BaseLLMAdapter):

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:9b",
        timeout: float = 180.0,
        think: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.think = think

    async def _generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        output_format: str | None = None,
    ) -> dict[str, Any]:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
            "think": self.think,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if output_format == "json":
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )

                response.raise_for_status()
                result = response.json()

            message = result.get("message", {})
            generated_text = message.get("content")

            if not isinstance(generated_text, str) or not generated_text.strip():
                raise ValueError(
                    "Ollama returned an empty or invalid message content."
                )

            return {
                "text": generated_text,
                "model": result.get("model", self.model),
                "done": result.get("done", False),
                "done_reason": result.get("done_reason"),
            }

        except httpx.HTTPError:
            logger.exception("Ollama API request failed.")
            raise

        except (ValueError, TypeError):
            logger.exception("Invalid response received from Ollama.")
            raise

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:

        result = await self._generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return result["text"].strip()

    async def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:

        result = await self._generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            output_format="json",
        )

        try:
            parsed = json.loads(result["text"])

        except json.JSONDecodeError as exc:
            logger.exception("Ollama generated invalid JSON.")
            raise ValueError(
                "Ollama did not generate valid JSON."
            ) from exc

        if not isinstance(parsed, dict):
            raise ValueError(
                "Ollama JSON response must be an object."
            )

        return parsed
