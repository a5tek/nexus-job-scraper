from typing import Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.models.raw_listing import RawListing
from app.repositories.listing_repo import ListingRepository
from app.llm.extractor import structured_extractor


class ExtractionProcessSummary(BaseModel):
    total_candidates: int
    extracted_count: int
    failed_count: int
    cache_hit_count: int
    duration_seconds: float


class ExtractionService:
    """
    Service responsible for transforming RawListing records into normalized Listings
    via structured LLM extraction and validation.
    """
    @staticmethod
    async def process_pending_raw_listings(
        db: AsyncSession,
        batch_size: int = 20,
    ) -> ExtractionProcessSummary:
        import time
        start_time = time.time()

        # Find pending raw listings
        stmt = (
            select(RawListing)
            .where(
                RawListing.extraction_status == "pending",
                RawListing.is_active == True,
            )
            .limit(batch_size)
        )
        res = await db.execute(stmt)
        pending_listings = res.scalars().all()

        extracted_count = 0
        failed_count = 0
        cache_hits = 0

        for raw in pending_listings:
            try:
                extracted, hit = await structured_extractor.extract(
                    db=db,
                    raw_content=raw.raw_content,
                    raw_content_hash=raw.content_hash,
                    raw_title=raw.raw_title,
                    source_url=raw.canonical_url,
                )

                if hit:
                    cache_hits += 1

                if extracted:
                    # Persist normalized listing
                    await ListingRepository.upsert_from_extraction(
                        db=db,
                        raw_listing_id=raw.id,
                        extracted=extracted,
                    )
                    raw.extraction_status = "extracted"
                    extracted_count += 1
                else:
                    raw.extraction_status = "failed"
                    failed_count += 1

                await db.commit()

            except Exception as exc:
                failed_count += 1
                raw.extraction_status = "failed"
                await db.commit()
                logger.error(f"Extraction failed for raw listing {raw.id}: {exc}")

        duration = round(time.time() - start_time, 2)
        summary = ExtractionProcessSummary(
            total_candidates=len(pending_listings),
            extracted_count=extracted_count,
            failed_count=failed_count,
            cache_hit_count=cache_hits,
            duration_seconds=duration,
        )

        logger.info(
            f"Extraction run complete: {extracted_count} extracted ({cache_hits} cached), "
            f"{failed_count} failed out of {len(pending_listings)} in {duration}s"
        )
        return summary
