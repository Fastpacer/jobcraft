import requests
from typing import List, Optional

from config.settings import settings
from schemas.job import Job


class SerpJobSearch:
    """
    Job search tool powered by SerpAPI (Google Jobs).
    """

    BASE_URL = "https://serpapi.com/search"

    def __init__(self):
        if not settings.SERPAPI_API_KEY:
            raise RuntimeError(
                "SERPAPI_API_KEY is not set. Add it to your .env file."
            )

        self.api_key = settings.SERPAPI_API_KEY

    def search(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Job]:
        """
        Search for jobs and return structured Job objects.
        """

        params = {
            "engine": "google_jobs",
            "q": query,
            "hl": "en",
            "api_key": self.api_key,
        }

        if location:
            params["location"] = location

        response = requests.get(self.BASE_URL, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()

        jobs: List[Job] = []

        for item in data.get("jobs_results", [])[:max_results]:
            job = Job(
                job_id=item.get("job_id"),
                title=item.get("title", ""),
                company=item.get("company_name", ""),
                location=item.get("location"),
                employment_type=item.get("employment_type"),
                description=item.get("description", ""),
                source="google_jobs",
                url=item.get("related_links", [{}])[0].get("link"),
            )
            jobs.append(job)

        return jobs
