from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.briefings.media_provider import get_media_provider
from app.briefings.script_generator import ScriptGenerator
from app.models.briefing import Briefing
from app.models.listing import Listing
from app.models.match import Match
from app.repositories.briefing_repo import BriefingRepository
from app.schemas.briefing import BriefingListingItem, BriefingResponse


class BriefingService:
    """
    Orchestrates the generation, tracking, and retrieval of executive audio/video briefings.
    """

    @staticmethod
    async def create_briefing(
        db: AsyncSession,
        user_id: str,
        user_name: str,
    ) -> Briefing:
        # 1. Fetch top 3 matches for the user
        stmt = (
            select(Match, Listing)
            .join(Listing, Match.listing_id == Listing.id)
            .where(Match.user_id == user_id)
            .order_by(desc(Match.display_score))
            .limit(3)
        )
        res = await db.execute(stmt)
        matched_pairs = res.all()

        top_matches_data = []
        top_listings = []
        for match, listing in matched_pairs:
            top_listings.append((listing, match.display_score))
            top_matches_data.append({
                "title": listing.title,
                "company": listing.company,
                "display_score": match.display_score,
                "justification": match.justification,
                "skills": listing.required_skills or [],
                "deadline": str(listing.deadline) if listing.deadline else "Not stated",
            })

        # Fallback: if user has no resume matches yet, pull top 3 recent listings
        if not top_listings:
            fallback_stmt = select(Listing).order_by(desc(Listing.created_at)).limit(3)
            fallback_res = await db.execute(fallback_stmt)
            for listing in fallback_res.scalars().all():
                top_listings.append((listing, None))
                top_matches_data.append({
                    "title": listing.title,
                    "company": listing.company,
                    "display_score": None,
                    "justification": "Recently published opportunity matching general engineering profiles.",
                    "skills": listing.required_skills or [],
                    "deadline": str(listing.deadline) if listing.deadline else "Not stated",
                })

        # 2. Synthesize editorial script
        script = ScriptGenerator.generate_script(
            user_name=user_name,
            top_matches=top_matches_data,
        )

        # 3. Create Briefing record
        provider = get_media_provider()
        briefing = await BriefingRepository.create(
            db=db,
            user_id=user_id,
            status="queued",
            script=script,
            provider=provider.provider_name,
        )

        # 4. Link top listings with ranks 1..3
        for rank, (listing, _) in enumerate(top_listings, start=1):
            await BriefingRepository.add_listing(
                db=db,
                briefing_id=briefing.id,
                listing_id=listing.id,
                rank=rank,
            )

        # 5. Process through media provider
        try:
            submission = await provider.submit_job(script=script, user_id=user_id)
            briefing.provider_job_id = submission.job_id
            
            if submission.status == "done":
                poll_res = await provider.poll_job(submission.job_id)
                briefing = await BriefingRepository.mark_done(
                    db=db,
                    briefing=briefing,
                    media_url=poll_res.media_url or "https://cdn.nexus.internal/briefing.mp3",
                    script=script,
                )
            else:
                briefing.status = "processing"
                await db.commit()
                await db.refresh(briefing)
        except Exception as exc:
            briefing = await BriefingRepository.mark_failed(
                db=db,
                briefing=briefing,
                error_message=f"Media generation failed: {exc}",
            )

        return briefing

    @staticmethod
    def format_briefing_response(
        briefing: Briefing,
        match_map: Optional[dict] = None,
    ) -> BriefingResponse:
        listings_items: List[BriefingListingItem] = []
        match_map = match_map or {}

        for link in briefing.listing_links:
            listing = link.listing
            if listing:
                listings_items.append(
                    BriefingListingItem(
                        rank=link.rank,
                        listing_id=listing.id,
                        title=listing.title,
                        company=listing.company,
                        location=listing.location,
                        match_score=match_map.get(listing.id),
                        deadline=str(listing.deadline) if listing.deadline else None,
                    )
                )

        return BriefingResponse(
            id=briefing.id,
            user_id=briefing.user_id,
            status=briefing.status,
            script=briefing.script,
            media_url=briefing.media_url,
            provider=briefing.provider,
            error_message=briefing.error_message,
            completed_at=briefing.completed_at,
            created_at=briefing.created_at,
            listings=listings_items,
        )

    @staticmethod
    async def get_briefing(
        db: AsyncSession,
        briefing_id: str,
        user_id: str,
    ) -> Optional[BriefingResponse]:
        briefing = await BriefingRepository.get_by_id(db, briefing_id=briefing_id, user_id=user_id)
        if not briefing:
            return None

        # Fetch match scores for linked listings for this user
        listing_ids = [l.listing_id for l in briefing.listing_links]
        match_map = {}
        if listing_ids:
            stmt = select(Match).where(
                Match.user_id == user_id,
                Match.listing_id.in_(listing_ids),
            )
            res = await db.execute(stmt)
            for m in res.scalars().all():
                match_map[m.listing_id] = m.display_score

        return BriefingService.format_briefing_response(briefing, match_map)

    @staticmethod
    async def list_user_briefings(
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
    ) -> List[BriefingResponse]:
        briefings = await BriefingRepository.list_for_user(db, user_id=user_id, limit=limit)
        
        # Batch load match scores
        all_listing_ids = set()
        for b in briefings:
            for link in b.listing_links:
                all_listing_ids.add(link.listing_id)

        match_map = {}
        if all_listing_ids:
            stmt = select(Match).where(
                Match.user_id == user_id,
                Match.listing_id.in_(list(all_listing_ids)),
            )
            res = await db.execute(stmt)
            for m in res.scalars().all():
                match_map[m.listing_id] = m.display_score

        return [
            BriefingService.format_briefing_response(b, match_map)
            for b in briefings
        ]
