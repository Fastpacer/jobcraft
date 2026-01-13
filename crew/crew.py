from crew.agents.resume_agent import ResumeAgent
from crew.agents.job_discovery import JobDiscoveryAgent
from crew.agents.matcher_agent import MatcherAgent
from crew.agents.outreach_agent import OutreachAgent
from crew.agents.tracker_agent import TrackerAgent
from storage.db import init_db
from utils import dedupe_text  # Import from utils


def run():
    init_db()

    resume_text = """
Atharva Salpekar
Machine Learning Intern

Skills: Python, NLP, Deep Learning, SQL
Experience:
- ML Intern at XYZ Labs
- Research Assistant

Worked on fraud detection and NLP systems.
"""

    resume_agent = ResumeAgent()
    job_agent = JobDiscoveryAgent()
    matcher_agent = MatcherAgent()
    outreach_agent = OutreachAgent()
    tracker_agent = TrackerAgent()

    resume = resume_agent.parse(resume_text)

    jobs = job_agent.discover(
        query="machine learning intern",
        location="India",
        max_results=3,
    )

    scored = matcher_agent.score(resume, jobs)

    for job, score in scored:
        # ---- Fit-score gate (important) ----
        if score < 50:
            continue

        message = outreach_agent.generate_message(
            resume, job, score
        )

        # ---- Output stabilization ----
        message = dedupe_text(message)

        tracker_agent.track(
            job_id=job.job_id,
            job_title=job.title,
            company=job.company,
            fit_score=score,
            outreach_message=message,
        )

        print(f"\nApplied Logic Preview → {job.title} @ {job.company}")
        print(f"Fit score: {score}")
        print(message)
        print("-" * 60)


if __name__ == "__main__":
    run()