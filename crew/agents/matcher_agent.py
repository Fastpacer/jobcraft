from typing import List, Tuple
import re

from llm.groq_client import GroqLLM
from schemas.job import Job
from schemas.resume import Resume

from sentence_transformers import SentenceTransformer, util
import numpy as np


class MatcherAgent:
    """
    Agent responsible for matching jobs to a resume and scoring fit.
    Uses lightweight RAG + LLM refinement.
    """

    _embedder = None

    @classmethod
    def get_embedder(cls):
        if cls._embedder is None:
            cls._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._embedder

    # -----------------------------
    # PROMPTS
    # -----------------------------

    SYSTEM_PROMPT = """
You are an expert technical recruiter.

Your task:
- Evaluate how well a candidate fits a job role.
- Use the provided resume information and relevant snippets.
- Return ONLY an integer score from 0 to 100.
- Do NOT explain your reasoning.
- Do NOT return any text other than the number.
"""

    USER_PROMPT_TEMPLATE = """
Resume Summary:
{resume_summary}

Skills:
{resume_skills}

Roles:
{resume_roles}

Tools:
{resume_tools}

Most Relevant Resume Snippets:
{relevant_snippets}

Job Title: {job_title}
Company: {company}

Job Description:
{description}

Fit score (0–100, integer only):
"""

    # -----------------------------
    # INIT
    # -----------------------------

    def __init__(self, llm: GroqLLM | None = None):
        self.llm = llm or GroqLLM()

    # -----------------------------
    # PUBLIC API
    # -----------------------------

    def score(self, resume: Resume, jobs: List[Job]) -> List[Tuple[Job, int]]:
        embedder = self.get_embedder()
        scored: List[Tuple[Job, int]] = []

        resume_chunks = self._prepare_resume_chunks(resume)
        if not resume_chunks:
            return [(job, 0) for job in jobs]

        # Aggregate resume embedding
        resume_emb = (
            embedder.encode(resume_chunks, convert_to_tensor=True)
            .mean(dim=0)
            .unsqueeze(0)
        )

        for job in jobs:
            job_text = job.description or ""
            job_emb = embedder.encode(job_text, convert_to_tensor=True).unsqueeze(0)

            # Base semantic similarity score
            sim = util.pytorch_cos_sim(resume_emb, job_emb).item()
            base_score = max(0, min(100, int(sim * 100)))

            # Retrieve top-k relevant resume chunks
            relevant = self._retrieve_relevant_chunks(
                resume_chunks, job_emb, top_k=3
            )

            prompt = self.USER_PROMPT_TEMPLATE.format(
                resume_summary=resume.summary or "",
                resume_skills=", ".join(resume.skills),
                resume_roles=", ".join(resume.roles),
                resume_tools=", ".join(resume.tools),
                relevant_snippets="; ".join(relevant),
                job_title=job.title,
                company=job.company,
                description=job_text,
            )

            response = (
                self.llm.generate(
                    prompt=prompt,
                    system_prompt=self.SYSTEM_PROMPT,
                )
                or ""
            )

            match = re.search(r"\d+", response)
            llm_score = int(match.group()) if match else base_score

            final_score = max(base_score, llm_score)
            scored.append((job, min(100, final_score)))

        return scored

    # -----------------------------
    # INTERNAL HELPERS
    # -----------------------------

    def _prepare_resume_chunks(self, resume: Resume) -> List[str]:
        chunks = []
        if resume.summary:
            chunks.append(f"Summary: {resume.summary}")
        if resume.skills:
            chunks.append(f"Skills: {', '.join(resume.skills)}")
        if resume.roles:
            chunks.append(f"Roles: {', '.join(resume.roles)}")
        if resume.tools:
            chunks.append(f"Tools: {', '.join(resume.tools)}")
        return chunks

    def _retrieve_relevant_chunks(
        self, chunks: List[str], job_emb, top_k: int = 3
    ) -> List[str]:
        if not chunks:
            return []

        embedder = self.get_embedder()
        chunk_embs = embedder.encode(chunks, convert_to_tensor=True)

        sims = util.pytorch_cos_sim(job_emb, chunk_embs)[0]
        top_indices = np.argsort(sims.cpu().numpy())[-top_k:][::-1]

        return [chunks[i] for i in top_indices]
