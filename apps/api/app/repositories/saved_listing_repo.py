from typing import List, Optional, Tuple
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.listing import Listing
from app.models.match import Match
from app.models.saved_listing import SavedListing
from app.repositories.base import enforce_user_scope


class SavedListingRepository:
    """
    Repository for managing user shortlists (saved listings).
    Enforces user isolation and idempotent saving.
    """
    @staticmethod
    async def get_by_user_and_listing(
        db: AsyncSession,
        user_id: str,
        listing_id: str,
    ) -> Optional[SavedListing]:
        query = select(SavedListing).where(
            SavedListing.user_id == user_id,
            SavedListing.listing_id == listing_id,
        )
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def save(
        db: AsyncSession,
        user_id: str,
        listing_id: str,
    ) -> SavedListing:
        """
        Idempotently saves a listing to user's shortlist.
        """
        existing = await SavedListingRepository.get_by_user_and_listing(db, user_id, listing_id)
        if existing:
            return existing

        saved = SavedListing(user_id=user_id, listing_id=listing_id)
        db.add(saved)
        await db.commit()
        await db.refresh(saved)
        return saved

    @staticmethod
    async def unsave(
        db: AsyncSession,
        user_id: str,
        listing_id: str,
    ) -> bool:
        """
        Removes a listing from user's shortlist.
        Returns True if deleted, False if it wasn't saved.
        """
        stmt = delete(SavedListing).where(
            SavedListing.user_id == user_id,
            SavedListing.listing_id == listing_id,
        )
        res = await db.execute(stmt)
        await db.commit()
        return res.rowcount > 0

    @staticmethod
    async def list_for_user(
        db: AsyncSession,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Tuple[SavedListing, Listing, Optional[Match]]]:
        """
        Returns saved listings joined with listing metadata and current user match score/justification.
        """
        query = (
            select(SavedListing, Listing, Match)
            .join(Listing, SavedListing.listing_id == Listing.id)
            .outerjoin(
                Match,
                (Match.listing_id == Listing.id) & (Match.user_id == user_id),
            )
            .where(SavedListing.user_id == user_id)
            .order_by(desc(SavedListing.created_at))
            .offset(offset)
            .limit(limit)
        )
        res = await db.execute(query)
        return res.all()
