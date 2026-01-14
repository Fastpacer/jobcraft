from llm.groq_client import GroqLLM
from schemas.job import Job
from schemas.resume import Resume
from sentence_transformers import SentenceTransformer, util
import numpy as np


class OutreachAgent:
    """
    Agent responsible for generating highly personalized outreach messages.
    Uses RAG to retrieve and infuse relevant resume content.
    """

    # Class-level embedder to preload once
    _embedder = None

    @classmethod
    def get_embedder(cls):
        if cls._embedder is None:
            cls._embedder = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._embedder

    SYSTEM_PROMPT = """
You are an expert career consultant specializing in personalized job outreach.

Rules (must follow all):
- Write ONE concise outreach message (under 120 words).
- Reference 2-3 specific resume details (e.g., skills, projects, experiences) that match the job.
- Highlight how the candidate's background aligns with the job's requirements.
- Use a professional, enthusiastic tone.
- Do NOT repeat phrases, include explanations, or mention fit scores.
- Output ONLY the message text (no subject, no markdown).
- Make it unique: Avoid generic phrases like "I am excited to apply."
"""

    def __init__(self, llm: GroqLLM | None = None):
        self.llm = llm or GroqLLM()
        # Use class-level embedder
        self.embedder = self.get_embedder()

    def generate_message(
        self,
        resume: Resume,
        job: Job,
        fit_score: int,
    ) -> str:
        # Prepare resume chunks for retrieval
        resume_chunks = self._prepare_resume_chunks(resume)
        
        # Embed job description
        job_embedding = self.embedder.encode(job.description, convert_to_tensor=True)
        
        # Retrieve top-matching resume chunks
        relevant_chunks = self._retrieve_relevant_chunks(resume_chunks, job_embedding, top_k=3)
        
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
- Relevant Resume Snippets: {'; '.join(relevant_chunks)}

Job Details:
- Title: {job.title}
- Company: {job.company}
- Description: {job.description}

Tone: {tone}

Focus on matching skills/experiences to job needs, express genuine interest, and reference specific resume elements.
"""

        return self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )

    def _prepare_resume_chunks(self, resume: Resume) -> list[str]:
        """
        Break resume into meaningful chunks for embedding.
        """
        chunks = []
        if resume.summary:
            chunks.append(f"Summary: {resume.summary}")
        if resume.skills:
            chunks.append(f"Skills: {', '.join(resume.skills)}")
        if resume.roles:
            chunks.append(f"Roles: {', '.join(resume.roles)}")
        if resume.tools:
            chunks.append(f"Tools: {', '.join(resume.tools)}")
        # Add more if schema expands (e.g., projects)
        return chunks

    def _retrieve_relevant_chunks(self, chunks: list[str], job_embedding, top_k: int = 3) -> list[str]:
        """
        Retrieve top-k resume chunks most similar to job description.
        """
        if not chunks:
            return []
        
        chunk_embeddings = self.embedder.encode(chunks, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(job_embedding, chunk_embeddings)[0]
        top_indices = np.argsort(similarities.cpu().numpy())[-top_k:][::-1]  # Top similar
        return [chunks[i] for i in top_indices]

    def _extract_keywords(self, description: str) -> list[str]:
        """
        Simple keyword extraction from job description (can be enhanced with NLP).
        """
        words = description.lower().split()
        keywords = [word for word in words if len(word) > 3 and word not in ['with', 'and', 'the', 'for', 'are', 'you']]
        return list(set(keywords))[:10]