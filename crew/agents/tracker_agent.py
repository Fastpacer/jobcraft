from schemas.application import Application
from storage.db import save_application


class TrackerAgent:
    """
    Agent responsible for persisting application state.
    """

    def track(
        self,
        job_id: str | None,
        job_title: str,
        company: str,
        fit_score: int,
        outreach_message: str | None = None,
    ) -> None:
        application = Application(
            job_id=job_id,
            job_title=job_title,
            company=company,
            fit_score=fit_score,
            outreach_message=outreach_message,
        )

        save_application(application)