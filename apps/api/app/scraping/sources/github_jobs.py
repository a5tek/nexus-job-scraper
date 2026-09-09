import re
from typing import List, Optional
from bs4 import BeautifulSoup
from app.core.logging import logger
from app.scraping.base import BaseScraper
from app.scraping.dedupe import normalize_canonical_url
from app.scraping.schemas import ListingCandidate


class GitHubInternshipsScraper(BaseScraper):
    """
    Source 2: GitHub hiring repositories & tabular internship aggregators.
    Targets structured markdown tables or HTML table layouts (e.g. Pitt CSC / Simplify repo).
    Layout is tabular: Company | Role | Location | Application Link | Date Posted
    Structurally different from the card-based startup boards.
    """
    @property
    def source_key(self) -> str:
        return "github_internships"

    @property
    def source_name(self) -> str:
        return "GitHub Tech Internships"

    @property
    def base_url(self) -> str:
        return "https://raw.githubusercontent.com/pittcsc/Summer2025-Internships/dev"

    async def discover_pages(self, max_pages: int = 5) -> List[str]:
        # Target markdown/HTML tables from repositories
        pages = [
            f"{self.base_url}/README.md",
        ]
        return pages[:max_pages]

    def parse_markdown_table(self, markdown_text: str, page_url: str) -> List[ListingCandidate]:
        """
        Parses Markdown table rows:
        | Company | Role | Location | Application Link | Date Posted |
        """
        candidates: List[ListingCandidate] = []
        lines = markdown_text.splitlines()
        in_table = False

        for line in lines:
            trimmed = line.strip()
            if not trimmed.startswith("|"):
                continue

            # Check if this is a header separator (e.g. |--|--|)
            if re.match(r"^\|(\s*:?-+:?\s*\|)+$", trimmed):
                in_table = True
                continue

            if not in_table:
                # Check for header row
                if "Company" in trimmed or "Role" in trimmed or "Name" in trimmed:
                    continue

            # Split cells
            cells = [c.strip() for c in trimmed.strip("|").split("|")]
            if len(cells) < 3:
                continue

            # Usually: Company, Role, Location, Links, Date
            company_raw = cells[0] if len(cells) > 0 else ""
            role_raw = cells[1] if len(cells) > 1 else ""
            location_raw = cells[2] if len(cells) > 2 else ""
            link_raw = cells[3] if len(cells) > 3 else ""

            # Extract markdown link: [Text](URL)
            link_match = re.search(r"\[(.*?)\]\((https?://[^\s\)]+)\)", link_raw)
            if not link_match:
                # Try company column for link
                link_match = re.search(r"\[(.*?)\]\((https?://[^\s\)]+)\)", company_raw)

            # Clean company name from markdown link if any
            company = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", company_raw).replace("**", "").strip()
            role = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", role_raw).replace("**", "").strip()
            location = location_raw.replace("**", "").strip()

            if not company or company.lower() in ("company", "name") or not role:
                continue

            # Extract application URL
            source_url = link_match.group(2) if link_match else page_url
            source_url = normalize_canonical_url(source_url)

            raw_content = (
                f"Source: GitHub Tech Internships Aggregator\n"
                f"Company: {company}\n"
                f"Role: {role}\n"
                f"Location: {location}\n"
                f"Application: {source_url}\n"
                f"Notes: Extracted from community tech internship tracker table."
            )

            candidates.append(
                ListingCandidate(
                    source_name=self.source_name,
                    source_url=source_url,
                    source_listing_id=None,  # Tabular rows rely on canonical URL / content hash for dedupe
                    raw_title=role,
                    raw_content=raw_content,
                    company_hint=company,
                    location_hint=location,
                )
            )

        return candidates

    def parse_html_table(self, html: str, page_url: str) -> List[ListingCandidate]:
        """
        Parses HTML <table> rows when rendered as HTML.
        """
        soup = BeautifulSoup(html, "html.parser")
        candidates: List[ListingCandidate] = []

        rows = soup.select("table tbody tr") or soup.select("table tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < 3 or row.find("th"):
                continue

            company = cells[0].get_text(strip=True)
            role = cells[1].get_text(strip=True)
            location = cells[2].get_text(strip=True)

            link_elem = row.find("a", href=True)
            source_url = link_elem["href"] if link_elem else page_url
            source_url = normalize_canonical_url(source_url)

            if not company or not role:
                continue

            raw_content = (
                f"Source: GitHub Tech Internships Aggregator\n"
                f"Company: {company}\n"
                f"Role: {role}\n"
                f"Location: {location}\n"
                f"Application: {source_url}"
            )

            candidates.append(
                ListingCandidate(
                    source_name=self.source_name,
                    source_url=source_url,
                    source_listing_id=None,
                    raw_title=role,
                    raw_content=raw_content,
                    company_hint=company,
                    location_hint=location,
                )
            )

        return candidates

    async def scrape_page(self, page_url: str) -> List[ListingCandidate]:
        resp = await self.client.get(page_url, check_robots=True)
        if not resp or resp.status_code != 200:
            logger.warning(f"Could not fetch {page_url}")
            return []

        text = resp.text
        if "<table" in text:
            return self.parse_html_table(text, page_url)
        return self.parse_markdown_table(text, page_url)
