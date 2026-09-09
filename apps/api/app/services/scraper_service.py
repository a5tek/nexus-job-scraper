from datetime import datetime, timezone
import time
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.repositories.raw_listing_repo import RawListingRepository
from app.scraping.registry import scraper_registry
from app.scraping.schemas import ScrapeSummary


class ScraperService:
    """
    Orchestration service for executing web scrapers, managing source records,
    and persisting raw job listings with deduplication and change detection.
    """
    @staticmethod
    async def run_scraper(
        db: AsyncSession,
        source_key: str,
        max_pages: int = 5,
    ) -> ScrapeSummary:
        scraper = scraper_registry.get(source_key)
        if not scraper:
            raise ValueError(f"Unknown scraper source key: '{source_key}'. Available: {scraper_registry.keys()}")

        started_at = datetime.now(timezone.utc)
        start_time = time.time()

        # Ensure source record exists in database
        source_record = await RawListingRepository.get_or_create_source(
            db=db,
            name=scraper.source_name,
            base_url=scraper.base_url,
            scraper_key=scraper.source_key,
        )

        inserted = 0
        updated = 0
        unchanged = 0
        errors = 0

        # Execute scraper run
        candidates = await scraper.run(max_pages=max_pages)

        for candidate in candidates:
            try:
                _, status = await RawListingRepository.upsert_candidate(
                    db=db,
                    source_id=source_record.id,
                    candidate=candidate,
                )
                if status == "inserted":
                    inserted += 1
                elif status == "updated":
                    updated += 1
                elif status == "unchanged":
                    unchanged += 1
            except Exception as exc:
                errors += 1
                logger.error(f"Failed to upsert candidate {candidate.source_url}: {exc}")

        completed_at = datetime.now(timezone.utc)
        duration = round(time.time() - start_time, 2)

        summary = ScrapeSummary(
            source_name=scraper.source_name,
            pages_scraped=max_pages,
            listings_found=len(candidates),
            inserted_count=inserted,
            updated_count=updated,
            unchanged_count=unchanged,
            errors_count=errors,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
        )

        logger.info(
            f"Scrape completed for [{scraper.source_name}]: "
            f"{inserted} inserted, {updated} updated, {unchanged} unchanged, {errors} errors in {duration}s"
        )
        return summary

    @staticmethod
    async def run_all_scrapers(
        db: AsyncSession,
        max_pages: int = 3,
    ) -> List[ScrapeSummary]:
        summaries: List[ScrapeSummary] = []
        for key in scraper_registry.keys():
            try:
                summary = await ScraperService.run_scraper(db, key, max_pages=max_pages)
                summaries.append(summary)
            except Exception as exc:
                logger.error(f"Scraper run failed for source '{key}': {exc}")
        return summaries
