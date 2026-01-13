from llm.groq_client import GroqLLM
from schemas.job import Job
from schemas.resume import Resume


class OutreachAgent:
    """
    Agent responsible for generating highly personalized outreach messages.
    Analyzes resume details and job descriptions for tailored, professional communication.
    """

    SYSTEM_PROMPT = """
You are an expert career consultant specializing in personalized job outreach.

Rules (must follow all):
- Write ONE concise outreach message (under 100 words).
- Reference 2-3 specific resume details (e.g., skills, projects, experiences) that match the job.
- Highlight how the candidate's background aligns with the job's requirements.
- Use a professional, enthusiastic tone.
- Do NOT repeat phrases, include explanations, or mention fit scores.
- Output ONLY the message text (no subject, no markdown).
- Make it unique: Avoid generic phrases like "I am excited to apply."
"""

    def __init__(self, llm: GroqLLM | None = None):
        self.llm = llm or GroqLLM()

    def generate_message(
        self,
        resume: Resume,
        job: Job,
        fit_score: int,
    ) -> str:
        # Extract key job keywords from description
        job_keywords = self._extract_keywords(job.description)
        
        # Determine tone based on fit score
        tone = "confident and direct" if fit_score > 70 else "approachable and exploratory"
        
        prompt = f"""
Generate a personalized outreach message for a job application.

Candidate Resume Details:
- Name: {resume.name or 'Candidate'}
- Summary: {resume.summary or 'Experienced professional'}
- Skills: {', '.join(resume.skills)}
- Roles: {', '.join(resume.roles)}
- Tools: {', '.join(resume.tools)}
- Experience: {resume.total_experience_years} years

Job Details:
- Title: {job.title}
- Company: {job.company}
- Description: {job.description}
- Key Requirements: {', '.join(job_keywords)}

Tone: {tone}

Focus on matching skills/experiences to job needs, and express genuine interest in the role/company.
"""

        return self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )

    def _extract_keywords(self, description: str) -> list[str]:
        """
        Simple keyword extraction from job description (can be enhanced with NLP).
        """
        # Basic extraction: split and filter common words
        words = description.lower().split()
        keywords = [word for word in words if len(word) > 3 and word not in ['with', 'and', 'the', 'for', 'are', 'you']]
        return list(set(keywords))[:10]  # Top 10 unique keywords