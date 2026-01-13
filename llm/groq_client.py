from typing import Optional, List, Dict

from groq import Groq

from config.settings import settings
from llm.models import GroqReasoningModels


class GroqLLM:
    """
    Thin wrapper around Groq chat completion API.
    This class is ONLY for reasoning / generation models.
    """

    def __init__(
        self,
        model: Optional[GroqReasoningModels] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ):
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )

        self.client = Groq(api_key=settings.GROQ_API_KEY)

        # Default to env-defined reasoning model
        self.model: GroqReasoningModels = (
            model
            if model is not None
            else GroqReasoningModels(settings.DEFAULT_LLM_MODEL)
        )

        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate a natural-language response from a reasoning model.
        """

        messages: List[Dict[str, str]] = []

        if system_prompt:
            messages.append(
                {"role": "system", "content": system_prompt.strip()}
            )

        messages.append(
            {"role": "user", "content": prompt.strip()}
        )

        response = self.client.chat.completions.create(
            model=self.model.value,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content.strip()
