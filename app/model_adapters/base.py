
from abc import ABC, abstractmethod
from typing import Any


class BaseLLMAdapter(ABC):
    """
    Provider-independent interface for NOVA language models.

    All LLM providers must implement these methods.
    """

    @abstractmethod
    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate a natural-language response.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        """
        Generate a structured JSON response.
        """
        raise NotImplementedError
