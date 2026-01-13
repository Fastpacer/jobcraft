from typing import List, Tuple

from llm.groq_client import GroqLLM
from schemas.job import Job
from schemas.resume import Resume


class MatcherAgent:
    """
    Agent responsible for matching jobs to a resume
    and scoring fit.
    """

    SYSTEM_PROMPT = """
You are an expert recruiter.

Analyze the resume and job description.
Return ONLY an integer fit score from 0 to 100.
No explanations, no text—just the number.
Consider skills, experience, and relevance.
Be strict but fair.
"""

    USER_PROMPT_TEMPLATE = """
Resume:
{resume}

Job Title: {job_title}
Company: {company}
Description: {description}

Fit Score (0-100, integer only):
"""

    def __init__(self, llm: GroqLLM | None = None):
        self.llm = llm or GroqLLM()

    def score(self, resume: Resume, jobs: List[Job]) -> List[Tuple[Job, int]]:
        """
        Score each job against the resume.
        Returns list of (job, score) tuples.
        """
        scored: List[Tuple[Job, int]] = []

        for job in jobs:
            prompt = self.USER_PROMPT_TEMPLATE.format(
                resume=resume.model_dump_json(),
                job_title=job.title,
                company=job.company,
                description=job.description,
            )

            response = self.llm.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
            )

            # Extract the first integer from the response
            import re
            match = re.search(r'\d+', response.strip())
            if match:
                score = int(match.group())
                score = max(0, min(100, score))  # Clamp to 0-100
            else:
                score = 0  # Default if no number found

            scored.append((job, score))

        return scored