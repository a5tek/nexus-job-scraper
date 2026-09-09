from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.listing_repo import ListingRepository
from app.repositories.saved_listing_repo import SavedListingRepository
from app.schemas.listing import OpportunityFeedItem
from app.schemas.shortlist import ShortlistItemResponse

router = APIRouter(prefix="/shortlist", tags=["Shortlist"])


@router.get("", response_model=List[ShortlistItemResponse])
async def get_user_shortlist(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the authenticated user's saved listings, match scores, and explanations.
    """
    saved_records = await SavedListingRepository.list_for_user(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    items = []
    for saved, listing, match in saved_records:
        items.append(
            ShortlistItemResponse(
                id=saved.id,
                user_id=saved.user_id,
                listing_id=saved.listing_id,
                created_at=saved.created_at,
                listing=OpportunityFeedItem(
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
                    is_saved=True,
                    source_url=listing.raw_listing.source_url if listing.raw_listing else None,
                ),
            )
        )
    return items


@router.post("/{listing_id}", status_code=status.HTTP_201_CREATED)
async def save_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Idempotently saves a listing to the user's personal shortlist.
    """
    listing = await ListingRepository.get_by_id(db, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "LISTING_NOT_FOUND", "message": "Job listing not found."}},
        )

    await SavedListingRepository.save(db, user_id=current_user.id, listing_id=listing_id)
    return {"status": "saved", "listing_id": listing_id}


@router.delete("/{listing_id}", status_code=status.HTTP_200_OK)
async def unsave_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Removes a listing from the user's personal shortlist.
    """
    deleted = await SavedListingRepository.unsave(db, user_id=current_user.id, listing_id=listing_id)
    return {"status": "unsaved" if deleted else "not_found", "listing_id": listing_id}
