from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ListingCandidate(BaseModel):
    """
    Candidate listing extracted by a scraper before database normalization.
    """
    source_name: str
    source_url: str
    source_listing_id: Optional[str] = None
    raw_title: Optional[str] = None
    raw_content: str
    company_hint: Optional[str] = None
    location_hint: Optional[str] = None


class ScrapeSummary(BaseModel):
    """
    Summary of a scraping run for a specific source.
    """
    source_name: str
    pages_scraped: int
    listings_found: int
    inserted_count: int
    updated_count: int
    unchanged_count: int
    errors_count: int
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
