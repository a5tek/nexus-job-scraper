from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_current_user_optional
from app.db.session import get_db
from app.embeddings.provider import embedding_provider
from app.models.listing import Listing
from app.models.match import Match
from app.models.raw_listing import RawListing
from app.models.saved_listing import SavedListing
from app.models.user import User
from app.repositories.listing_repo import ListingRepository
from app.schemas.listing import OpportunityFeedItem, SemanticSearchRequest

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.get("", response_model=List[OpportunityFeedItem])
async def get_opportunity_feed(
    remote_only: Optional[bool] = None,
    experience_level: Optional[str] = None,
    company: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the opportunity feed.
    If authenticated, results are personalized and ranked by semantic match score.
    """
    if current_user:
        query = (
            select(Listing, Match, SavedListing, RawListing.source_url)
            .join(RawListing, Listing.raw_listing_id == RawListing.id)
            .outerjoin(
                Match,
                (Match.listing_id == Listing.id) & (Match.user_id == current_user.id),
            )
            .outerjoin(
                SavedListing,
                (SavedListing.listing_id == Listing.id) & (SavedListing.user_id == current_user.id),
            )
        )
    else:
        query = (
            select(Listing, RawListing.source_url)
            .join(RawListing, Listing.raw_listing_id == RawListing.id)
        )

    if remote_only is not None:
        query = query.where(Listing.remote_ok == remote_only)
    if experience_level:
        query = query.where(Listing.experience_level.ilike(f"%{experience_level}%"))
    if company:
        query = query.where(Listing.company.ilike(f"%{company}%"))

    if current_user:
        query = query.order_by(desc(Match.display_score), desc(Listing.created_at)).offset(offset).limit(limit)
    else:
        query = query.order_by(desc(Listing.created_at)).offset(offset).limit(limit)

    res = await db.execute(query)
    rows = res.all()

    items = []
    if current_user:
        for listing, match, saved, source_url in rows:
            items.append(
                OpportunityFeedItem(
                    id=listing.id,
                    title=listing.title,
                    company=listing.company,
                    location=listing.location,
                    remote_ok=listing.remote_ok,
                    stipend=listing.stipend,
                    required_skills=listing.required_skills or [],
                    experience_level=listing.experience_level,
                    deadline=listing.deadline,
                    match_score=match.display_score if match else None,
                    match_explanation=match.justification if match else None,
                    is_saved=saved is not None,
                    source_url=source_url,
                )
            )
    else:
        for listing, source_url in rows:
            items.append(
                OpportunityFeedItem(
                    id=listing.id,
                    title=listing.title,
                    company=listing.company,
                    location=listing.location,
                    remote_ok=listing.remote_ok,
                    stipend=listing.stipend,
                    required_skills=listing.required_skills or [],
                    experience_level=listing.experience_level,
                    deadline=listing.deadline,
                    match_score=None,
                    match_explanation=None,
                    is_saved=False,
                    source_url=source_url,
                )
            )
    return items


@router.get("/{listing_id}", response_model=OpportunityFeedItem)
async def get_listing_detail(
    listing_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves detailed information for a single opportunity.
    """
    if current_user:
        query = (
            select(Listing, Match, SavedListing, RawListing.source_url)
            .join(RawListing, Listing.raw_listing_id == RawListing.id)
            .outerjoin(
                Match,
                (Match.listing_id == Listing.id) & (Match.user_id == current_user.id),
            )
            .outerjoin(
                SavedListing,
                (SavedListing.listing_id == Listing.id) & (SavedListing.user_id == current_user.id),
            )
            .where(Listing.id == listing_id)
        )
        res = await db.execute(query)
        row = res.first()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "LISTING_NOT_FOUND", "message": "Listing not found."}},
            )
        listing, match, saved, source_url = row
        return OpportunityFeedItem(
            id=listing.id,
            title=listing.title,
            company=listing.company,
            location=listing.location,
            remote_ok=listing.remote_ok,
            stipend=listing.stipend,
            required_skills=listing.required_skills or [],
            experience_level=listing.experience_level,
            deadline=listing.deadline,
            match_score=match.display_score if match else None,
            match_explanation=match.justification if match else None,
            is_saved=saved is not None,
            source_url=source_url,
        )
    else:
        query = (
            select(Listing, RawListing.source_url)
            .join(RawListing, Listing.raw_listing_id == RawListing.id)
            .where(Listing.id == listing_id)
        )
        res = await db.execute(query)
        row = res.first()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "LISTING_NOT_FOUND", "message": "Listing not found."}},
            )
        listing, source_url = row
        return OpportunityFeedItem(
            id=listing.id,
            title=listing.title,
            company=listing.company,
            location=listing.location,
            remote_ok=listing.remote_ok,
            stipend=listing.stipend,
            required_skills=listing.required_skills or [],
            experience_level=listing.experience_level,
            deadline=listing.deadline,
            match_score=None,
            match_explanation=None,
            is_saved=False,
            source_url=source_url,
        )


@router.post("/search", response_model=List[OpportunityFeedItem])
async def search_listings(
    request: SemanticSearchRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes semantic search using vector cosine similarity.
    Retrieves conceptually related roles even without exact literal keyword matches.
    """
    # 1. Embed query text
    query_vector = embedding_provider.embed_text(request.query)

    # 2. Semantic vector lookup
    scored_listings = await ListingRepository.semantic_search(
        db=db,
        query_vector=query_vector,
        limit=request.limit,
        remote_only=request.remote_only,
    )

    items = []
    for listing, _ in scored_listings:
        match = None
        is_saved = False
        if current_user:
            match_stmt = select(Match).where(
                Match.listing_id == listing.id,
                Match.user_id == current_user.id,
            )
            match_res = await db.execute(match_stmt)
            match = match_res.scalar_one_or_none()

            saved_stmt = select(SavedListing).where(
                SavedListing.listing_id == listing.id,
                SavedListing.user_id == current_user.id,
            )
            saved_res = await db.execute(saved_stmt)
            is_saved = saved_res.scalar_one_or_none() is not None

        items.append(
            OpportunityFeedItem(
                id=listing.id,
                title=listing.title,
                company=listing.company,
                location=listing.location,
                remote_ok=listing.remote_ok,
                stipend=listing.stipend,
                required_skills=listing.required_skills or [],
                experience_level=listing.experience_level,
                deadline=listing.deadline,
                match_score=match.display_score if match else None,
                match_explanation=match.justification if match else None,
                is_saved=is_saved,
                source_url=listing.raw_listing.source_url if listing.raw_listing else None,
            )
        )
    return items
