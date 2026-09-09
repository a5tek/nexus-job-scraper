from typing import List
from bs4 import BeautifulSoup
from app.core.logging import logger
from app.scraping.base import BaseScraper
from app.scraping.dedupe import normalize_canonical_url
from app.scraping.schemas import ListingCandidate


class YCJobsScraper(BaseScraper):
    """
    Source 1: Startup job board with card-based layouts.
    Target: Y Combinator Work at a Startup / startup ecosystem.
    Parses nested card structures, roles, company tags, and compensation.
    """
    @property
    def source_key(self) -> str:
        return "yc_jobs"

    @property
    def source_name(self) -> str:
        return "YC Work at a Startup"

    @property
    def base_url(self) -> str:
        return "https://www.workatastartup.com"

    async def discover_pages(self, max_pages: int = 5) -> List[str]:
        # Typical discovery points: main jobs index and role/domain filtered pages
        pages = [
            f"{self.base_url}/jobs",
            f"{self.base_url}/jobs?job_type=internship",
            f"{self.base_url}/jobs?job_type=full_time",
        ]
        return pages[:max_pages]

    def parse_html_content(self, html: str, page_url: str) -> List[ListingCandidate]:
        """
        Parses card-based HTML structures into ListingCandidate objects.
        """
        soup = BeautifulSoup(html, "html.parser")
        candidates: List[ListingCandidate] = []

        # Find card containers (supports common startup board layouts)
        cards = soup.select(".job-card, .company-job-listing, .job-listing, [data-testid='job-card']")
        
        # If standard classes aren't matched, try semantic article/card elements
        if not cards:
            cards = soup.select("div.job, div.role-card, article.job, div[class*='JobCard']")

        for card in cards:
            try:
                # Title
                title_elem = card.select_one("h2, h3, h4, .job-title, [class*='title']")
                raw_title = title_elem.get_text(strip=True) if title_elem else "Software Engineer"

                # Company
                company_elem = card.select_one(".company-name, [class*='company'], [class*='Company']")
                company = company_elem.get_text(strip=True) if company_elem else "YC Startup"

                # Location / Remote
                location_elem = card.select_one(".location, [class*='location'], .tags")
                location = location_elem.get_text(strip=True) if location_elem else "Remote"

                # Direct link or ID
                link_elem = card.select_one("a[href*='/jobs/'], a[href*='/companies/'], a[href]")
                href = link_elem.get("href", "") if link_elem else ""
                
                source_url = href if href.startswith("http") else f"{self.base_url.rstrip('/')}/{href.lstrip('/')}"
                source_url = normalize_canonical_url(source_url) if source_url else page_url

                # Stable listing ID from URL or attribute
                listing_id = card.get("data-job-id") or card.get("id")
                if not listing_id and "/jobs/" in source_url:
                    parts = source_url.split("/jobs/")[-1].split("?")[0].strip("/").split("/")
                    if parts:
                        listing_id = parts[0]

                # Raw description/content
                desc_elem = card.select_one(".job-details, .description, p")
                desc = desc_elem.get_text(strip=True) if desc_elem else card.get_text(separator=" ", strip=True)

                raw_content = f"Company: {company}\nTitle: {raw_title}\nLocation: {location}\nDescription: {desc}"

                candidates.append(
                    ListingCandidate(
                        source_name=self.source_name,
                        source_url=source_url,
                        source_listing_id=listing_id,
                        raw_title=raw_title,
                        raw_content=raw_content,
                        company_hint=company,
                        location_hint=location,
                    )
                )
            except Exception as exc:
                logger.warning(f"Failed to parse YC job card: {exc}")

        return candidates

    async def scrape_page(self, page_url: str) -> List[ListingCandidate]:
        resp = await self.client.get(page_url, check_robots=True)
        if not resp or resp.status_code != 200:
            logger.warning(f"Could not fetch {page_url} (status: {resp.status_code if resp else 'No response'})")
            return []

        return self.parse_html_content(resp.text, page_url)
