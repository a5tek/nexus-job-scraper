from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.scraping.registry import scraper_registry
from app.scraping.schemas import ScrapeSummary
from app.services.scraper_service import ScraperService

router = APIRouter(prefix="/internal", tags=["Internal / Ingestion"])


class ScrapeTriggerRequest(BaseModel):
    source_key: Optional[str] = None
    max_pages: int = 3


@router.post("/scrape", response_model=List[ScrapeSummary])
async def trigger_scrape(
    request: ScrapeTriggerRequest = ScrapeTriggerRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers an on-demand scraper run for one or all registered sources.
    Respects robots.txt, rate limits per origin, and deduplicates against existing raw listings.
    """
    if request.source_key:
        if request.source_key not in scraper_registry.keys():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_SOURCE",
                        "message": f"Source '{request.source_key}' not found. Available: {scraper_registry.keys()}",
                    }
                },
            )
        summary = await ScraperService.run_scraper(
            db=db,
            source_key=request.source_key,
            max_pages=request.max_pages,
        )
        return [summary]

    # Run all registered scrapers
    return await ScraperService.run_all_scrapers(db=db, max_pages=request.max_pages)


@router.get("/sources")
async def list_sources():
    """Returns all available scraper sources in the registry."""
    return [
        {
            "source_key": scraper.source_key,
            "source_name": scraper.source_name,
            "base_url": scraper.base_url,
        }
        for scraper in scraper_registry.list_all()
    ]
