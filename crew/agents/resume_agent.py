import json
from typing import Any

from llm.groq_client import GroqLLM
from schemas.resume import Resume


class ResumeAgent:
    """
    Agent responsible for converting raw resume text
    into a structured Resume schema.
    """

    SYSTEM_PROMPT = """
You are an expert resume analyst.

Your task:
- Extract structured information from a resume.
- Return ONLY valid JSON.
- Do NOT include explanations or markdown.

The JSON must match this schema exactly:

{
  "name": string | null,
  "total_experience_years": number | null,
  "roles": string[],
  "skills": string[],
  "tools": string[],
  "summary": string | null
}
"""

    USER_PROMPT_TEMPLATE = """
Resume text:
{resume_text}
"""

    def __init__(self, llm: GroqLLM | None = None):
        self.llm = llm or GroqLLM()

    def parse(self, resume_text: str) -> Resume:
        """
        Parse raw resume text into a Resume schema.
        """
        prompt = self.USER_PROMPT_TEMPLATE.format(
            resume_text=resume_text.strip()
        )

        response = self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )

        try:
            data: Any = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"LLM did not return valid JSON:\n{response}"
            ) from e

        return Resume.model_validate(data)
