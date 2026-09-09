from typing import Dict, List, Optional
from app.scraping.base import BaseScraper
from app.scraping.sources.yc_jobs import YCJobsScraper
from app.scraping.sources.github_jobs import GitHubInternshipsScraper


class ScraperRegistry:
    """
    Registry for source scrapers.
    Manages available scrapers and enables modular source additions.
    """
    def __init__(self):
        self._scrapers: Dict[str, BaseScraper] = {}
        # Register default sources
        self.register(YCJobsScraper())
        self.register(GitHubInternshipsScraper())

    def register(self, scraper: BaseScraper) -> None:
        self._scrapers[scraper.source_key] = scraper

    def get(self, source_key: str) -> Optional[BaseScraper]:
        return self._scrapers.get(source_key)

    def list_all(self) -> List[BaseScraper]:
        return list(self._scrapers.values())

    def keys(self) -> List[str]:
        return list(self._scrapers.keys())


scraper_registry = ScraperRegistry()
