from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.briefing import Briefing
from app.models.briefing_listing import BriefingListing


class BriefingRepository:
    """
    Data access repository for weekly audio/video executive briefings.
    Enforces user scoping and manages briefing-to-listing links.
    """

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: str,
        status: str = "queued",
        script: Optional[str] = None,
        provider: Optional[str] = None,
        provider_job_id: Optional[str] = None,
    ) -> Briefing:
        briefing = Briefing(
            user_id=user_id,
            status=status,
            script=script,
            provider=provider,
            provider_job_id=provider_job_id,
        )
        db.add(briefing)
        await db.flush()
        return briefing

    @staticmethod
    async def add_listing(
        db: AsyncSession,
        briefing_id: str,
        listing_id: str,
        rank: int,
    ) -> BriefingListing:
        link = BriefingListing(
            briefing_id=briefing_id,
            listing_id=listing_id,
            rank=rank,
        )
        db.add(link)
        await db.flush()
        return link

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        briefing_id: str,
        user_id: str,
    ) -> Optional[Briefing]:
        stmt = (
            select(Briefing)
            .where(Briefing.id == briefing_id, Briefing.user_id == user_id)
            .options(
                selectinload(Briefing.listing_links).selectinload(BriefingListing.listing)
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def list_for_user(
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
    ) -> List[Briefing]:
        stmt = (
            select(Briefing)
            .where(Briefing.user_id == user_id)
            .options(
                selectinload(Briefing.listing_links).selectinload(BriefingListing.listing)
            )
            .order_by(desc(Briefing.created_at))
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_queued_briefings(
        db: AsyncSession,
        limit: int = 10,
    ) -> List[Briefing]:
        stmt = (
            select(Briefing)
            .where(Briefing.status.in_(["queued", "processing"]))
            .options(
                selectinload(Briefing.listing_links).selectinload(BriefingListing.listing)
            )
            .order_by(Briefing.created_at.asc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def mark_done(
        db: AsyncSession,
        briefing: Briefing,
        media_url: str,
        script: Optional[str] = None,
    ) -> Briefing:
        briefing.status = "done"
        briefing.media_url = media_url
        if script:
            briefing.script = script
        briefing.completed_at = datetime.now(timezone.utc)
        briefing.error_message = None
        await db.commit()
        await db.refresh(briefing)
        return briefing

    @staticmethod
    async def mark_failed(
        db: AsyncSession,
        briefing: Briefing,
        error_message: str,
    ) -> Briefing:
        briefing.status = "failed"
        briefing.error_message = error_message
        await db.commit()
        await db.refresh(briefing)
        return briefing
