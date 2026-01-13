from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from crew.agents.resume_agent import ResumeAgent
from crew.agents.job_discovery import JobDiscoveryAgent
from crew.agents.matcher_agent import MatcherAgent
from crew.agents.outreach_agent import OutreachAgent
from crew.agents.tracker_agent import TrackerAgent
from storage.db import init_db
from utils import dedupe_text


# -----------------------------
# API Schemas (Request / Response)
# -----------------------------

class RunRequest(BaseModel):
    resume_text: str
    query: str
    location: Optional[str] = None
    max_results: int = 5
    min_score: int = 50


class JobResult(BaseModel):
    job_id: Optional[str]
    title: str
    company: str
    fit_score: int
    outreach_message: str
    url: Optional[str] = None


class RunResponse(BaseModel):
    results: List[JobResult]


# -----------------------------
# App initialization
# -----------------------------

app = FastAPI(title="Multi-Agent Job Search Backend")

init_db()  # Initialize DB on startup


# -----------------------------
# Routes
# -----------------------------

@app.get("/")
def root():
    return {"message": "Multi-Agent Job Search API is running. Use /docs for Swagger UI."}


@app.post("/run-pipeline", response_model=RunResponse)
def run_pipeline(payload: RunRequest):
    try:
        # Initialize agents per request (avoids startup failures)
        resume_agent = ResumeAgent()
        job_agent = JobDiscoveryAgent()
        matcher_agent = MatcherAgent()
        outreach_agent = OutreachAgent()
        tracker_agent = TrackerAgent()

        resume = resume_agent.parse(payload.resume_text)

        jobs = job_agent.discover(
            query=payload.query,
            location=payload.location,
            max_results=payload.max_results,
        )

        scored = matcher_agent.score(resume, jobs)

        results: List[JobResult] = []

        for job, score in scored:
            if score < payload.min_score:
                continue

            message = outreach_agent.generate_message(
                resume, job, score
            )
            message = dedupe_text(message)

            tracker_agent.track(
                job_id=job.job_id,
                job_title=job.title,
                company=job.company,
                fit_score=score,
                outreach_message=message,
            )

            results.append(
                JobResult(
                    job_id=job.job_id,
                    title=job.title,
                    company=job.company,
                    fit_score=score,
                    outreach_message=message,
                    url=job.url,
                )
            )

        return RunResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
