from typing import List
from app.core.logging import logger
from app.scraping.base import BaseScraper
from app.scraping.dedupe import normalize_canonical_url
from app.scraping.schemas import ListingCandidate


class RemoteOKScraper(BaseScraper):
    """
    Source 3: RemoteOK Public API.
    A reliable, structured JSON API providing live remote tech roles.
    Demonstrably functions in production without brittle HTML parsing.
    """
    @property
    def source_key(self) -> str:
        return "remoteok"

    @property
    def source_name(self) -> str:
        return "RemoteOK"

    @property
    def base_url(self) -> str:
        return "https://remoteok.com"

    async def discover_pages(self, max_pages: int = 5) -> List[str]:
        # RemoteOK provides all current listings via its official JSON API endpoint
        return [f"{self.base_url}/api"][:max_pages]

    async def scrape_page(self, page_url: str) -> List[ListingCandidate]:
        """
        Fetches RemoteOK JSON listings and converts them into ListingCandidate records.
        """
        resp = await self.client.get(
            page_url,
            headers={"Accept": "application/json"},
            check_robots=True,
        )
        if not resp or resp.status_code != 200:
            logger.warning(f"Failed to fetch RemoteOK API: status={resp.status_code if resp else 'None'}")
            return []

        try:
            items = resp.json()
        except Exception as exc:
            logger.error(f"Error parsing RemoteOK JSON response: {exc}")
            return []

        if not isinstance(items, list):
            return []

        candidates: List[ListingCandidate] = []

        # Skip index 0 as RemoteOK serves legal metadata in the first element
        for job in items[1:]:
            if not isinstance(job, dict):
                continue

            company = (job.get("company") or "").strip()
            title = (job.get("position") or "").strip()
            if not company or not title:
                continue

            job_id = str(job.get("id")) if job.get("id") else None
            location = (job.get("location") or "Remote").strip()
            apply_url = job.get("apply_url") or job.get("url") or f"{self.base_url}/remote-jobs/{job_id}"
            source_url = normalize_canonical_url(apply_url)

            tags = job.get("tags") or []
            tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
            description = (job.get("description") or "").strip()
            # Clean basic HTML tags from description if present
            if "<" in description:
                from bs4 import BeautifulSoup
                description = BeautifulSoup(description, "html.parser").get_text(separator=" ", strip=True)

            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")
            salary_str = f"Salary: ${salary_min:,} - ${salary_max:,}" if salary_min and salary_max else ""

            raw_content = (
                f"Source: RemoteOK API\n"
                f"Company: {company}\n"
                f"Title: {title}\n"
                f"Location: {location}\n"
                f"{salary_str}\n"
                f"Tags: {tags_str}\n"
                f"Description: {description[:3000]}\n"
                f"Apply URL: {source_url}"
            ).strip()

            candidates.append(
                ListingCandidate(
                    source_name=self.source_name,
                    source_url=source_url,
                    source_listing_id=job_id,
                    raw_title=title,
                    raw_content=raw_content,
                    company_hint=company,
                    location_hint=location,
                )
            )

        return candidates
