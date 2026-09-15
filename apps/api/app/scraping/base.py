from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.logging import logger
from app.scraping.client import PoliteScraperClient
from app.scraping.browser_client import PlaywrightScraperClient
from app.scraping.schemas import ListingCandidate


class BaseScraper(ABC):
    """
    Contract for source scrapers.
    Each scraper targets a structurally distinct public website or repository.
    """
    def __init__(
        self,
        client: Optional[PoliteScraperClient] = None,
        use_browser: bool = False,
    ):
        self.client = client or PoliteScraperClient()
        self.use_browser = use_browser
        self.browser_client: Optional[PlaywrightScraperClient] = (
            PlaywrightScraperClient() if use_browser else None
        )
        self.last_scraped_pages_count: int = 0

    @property
    @abstractmethod
    def source_key(self) -> str:
        """Unique machine-readable key (e.g., 'yc_jobs', 'github_internships', 'remoteok')."""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Display name (e.g., 'YC Work at a Startup', 'GitHub Tech Internships', 'RemoteOK')."""
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
        successful_pages = 0

        for page in pages:
            try:
                candidates = await self.scrape_page(page)
                all_candidates.extend(candidates)
                successful_pages += 1
                logger.info(f"Scraped {len(candidates)} candidates from {page}")
            except Exception as exc:
                logger.error(f"Error scraping page {page} for {self.source_name}: {exc}")

        self.last_scraped_pages_count = successful_pages
        logger.info(f"Completed run for [{self.source_name}]: collected {len(all_candidates)} candidates across {successful_pages} pages.")
        return all_candidates

    async def close(self) -> None:
        """Closes any underlying network or browser resources."""
        await self.client.close()
        if self.browser_client:
            await self.browser_client.close()
