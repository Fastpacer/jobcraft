from typing import List, Optional

from schemas.job import Job
from tools.serp_search import SerpJobSearch


class JobDiscoveryAgent:
    """
    Agent responsible for discovering job listings
    based on search queries.
    """

    def __init__(self):
        self.search_tool = SerpJobSearch()

    def discover(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Job]:
        """
        Discover jobs using the search tool.
        """
        return self.search_tool.search(
            query=query,
            location=location,
            max_results=max_results,
        )