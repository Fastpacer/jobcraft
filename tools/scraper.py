import requests
from bs4 import BeautifulSoup
from typing import Optional

from schemas.job import Job


class JobScraper:
    """
    Fallback scraper for individual job posting URLs.
    Best-effort extraction only.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )

    def scrape(self, url: str, timeout: int = 15) -> Optional[Job]:
        headers = {"User-Agent": self.USER_AGENT}

        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # ---- Best-effort extraction ----

        title = self._extract_title(soup)
        company = self._extract_company(soup)
        description = self._extract_description(soup)

        if not title or not description:
            return None

        return Job(
            title=title,
            company=company or "Unknown",
            description=description,
            source="scraper",
            url=url,
        )

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        if soup.title:
            return soup.title.get_text(strip=True)
        return None

    def _extract_company(self, soup: BeautifulSoup) -> Optional[str]:
        # Common patterns (very heuristic)
        meta = soup.find("meta", property="og:site_name")
        if meta and meta.get("content"):
            return meta["content"]

        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        # Try common job description containers
        candidates = soup.find_all(
            ["section", "div"],
            class_=lambda x: x and "description" in x.lower()
        )
        if candidates:
            return candidates[0].get_text(strip=True)
        return None