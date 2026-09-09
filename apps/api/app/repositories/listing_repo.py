from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.listing import Listing
from app.llm.schemas import ExtractedListing


class ListingRepository:
    """
    Repository for managing normalized Listing records.
    """
    @staticmethod
    async def get_by_id(db: AsyncSession, listing_id: str) -> Optional[Listing]:
        stmt = select(Listing).where(Listing.id == listing_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_raw_listing_id(db: AsyncSession, raw_listing_id: str) -> Optional[Listing]:
        stmt = select(Listing).where(Listing.raw_listing_id == raw_listing_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def upsert_from_extraction(
        db: AsyncSession,
        raw_listing_id: str,
        extracted: ExtractedListing,
    ) -> Listing:
        existing = await ListingRepository.get_by_raw_listing_id(db, raw_listing_id)

        if existing:
            existing.title = extracted.title or "Software Engineer"
            existing.company = extracted.company or "Company"
            existing.location = extracted.location
            existing.remote_ok = extracted.remote_ok
            existing.stipend = extracted.stipend
            existing.required_skills = extracted.required_skills
            existing.experience_level = extracted.experience_level
            existing.deadline = extracted.deadline
            existing.extractor_version = settings.EXTRACTOR_VERSION
            await db.commit()
            await db.refresh(existing)
            return existing

        new_listing = Listing(
            raw_listing_id=raw_listing_id,
            title=extracted.title or "Software Engineer",
            company=extracted.company or "Company",
            location=extracted.location,
            remote_ok=extracted.remote_ok,
            stipend=extracted.stipend,
            required_skills=extracted.required_skills,
            experience_level=extracted.experience_level,
            deadline=extracted.deadline,
            extractor_version=settings.EXTRACTOR_VERSION,
        )
        db.add(new_listing)
        await db.commit()
        await db.refresh(new_listing)
        return new_listing
