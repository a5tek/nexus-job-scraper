from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
from app.llm.schemas import ExtractedListing


class LLMProvider(ABC):
    """
    Abstract interface for LLM operations.
    Allows transparent switching between Gemini, Claude, OpenAI, or local models.
    """
    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], int, int]:
        """
        Generates a JSON response.
        Returns: (parsed_json_dict, input_tokens, output_tokens)
        """
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> Tuple[str, int, int]:
        """
        Generates freeform text.
        Returns: (response_text, input_tokens, output_tokens)
        """
        pass
