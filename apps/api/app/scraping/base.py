from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.logging import logger
from app.scraping.client import PoliteScraperClient
from app.scraping.schemas import ListingCandidate


class BaseScraper(ABC):
    """
    Contract for source scrapers.
    Each scraper targets a structurally distinct public website or repository.
    """
    def __init__(self, client: Optional[PoliteScraperClient] = None):
        self.client = client or PoliteScraperClient()

    @property
    @abstractmethod
    def source_key(self) -> str:
        """Unique machine-readable key (e.g., 'yc_jobs', 'github_internships')."""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Display name (e.g., 'YC Work at a Startup', 'GitHub Tech Internships')."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Primary base URL for the source."""
        pass

    @abstractmethod
    async def discover_pages(self, max_pages: int = 5) -> List[str]:
        """Discovers listing page URLs to scrape."""
        pass

    @abstractmethod
    async def scrape_page(self, page_url: str) -> List[ListingCandidate]:
        """Fetches and parses candidates from a single page URL."""
        pass

    async def run(self, max_pages: int = 5) -> List[ListingCandidate]:
        """
        Executes discovery and parses candidates across all discovered pages.
        Fault-tolerant: failures on one page do not abort the entire run.
        """
        logger.info(f"Starting scrape run for [{self.source_name}] (max_pages={max_pages})")
        pages = await self.discover_pages(max_pages=max_pages)
        all_candidates: List[ListingCandidate] = []

        for page in pages:
            try:
                candidates = await self.scrape_page(page)
                all_candidates.extend(candidates)
                logger.info(f"Scraped {len(candidates)} candidates from {page}")
            except Exception as exc:
                logger.error(f"Error scraping page {page} for {self.source_name}: {exc}")

        logger.info(f"Completed run for [{self.source_name}]: collected {len(all_candidates)} candidates.")
        return all_candidates
