from typing import List, Optional, Tuple
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.listing import Listing
from app.models.match import Match


class MatchRepository:
    """
    Repository for user-scoped Match records and ranking queries.
    """
    @staticmethod
    async def get_match(
        db: AsyncSession,
        user_id: str,
        resume_id: str,
        listing_id: str,
    ) -> Optional[Match]:
        query = select(Match).where(
            Match.user_id == user_id,
            Match.resume_id == resume_id,
            Match.listing_id == listing_id,
        )
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def upsert_match(
        db: AsyncSession,
        user_id: str,
        resume_id: str,
        listing_id: str,
        similarity: float,
        display_score: int,
        justification: str,
        match_version: str = "1.0.0",
    ) -> Match:
        existing = await MatchRepository.get_match(db, user_id, resume_id, listing_id)
        if existing:
            existing.similarity = similarity
            existing.display_score = display_score
            existing.justification = justification
            existing.match_version = match_version
            await db.commit()
            await db.refresh(existing)
            return existing

        match = Match(
            user_id=user_id,
            resume_id=resume_id,
            listing_id=listing_id,
            similarity=similarity,
            display_score=display_score,
            justification=justification,
            match_version=match_version,
        )
        db.add(match)
        await db.commit()
        await db.refresh(match)
        return match

    @staticmethod
    async def get_top_matches_for_user(
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
    ) -> List[Tuple[Match, Listing]]:
        query = (
            select(Match, Listing)
            .join(Listing, Match.listing_id == Listing.id)
            .where(Match.user_id == user_id)
            .order_by(desc(Match.display_score))
            .limit(limit)
        )
        res = await db.execute(query)
        return res.all()
