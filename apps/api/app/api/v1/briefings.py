from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.briefing import BriefingResponse
from app.services.briefing_service import BriefingService

router = APIRouter(prefix="/briefings", tags=["Briefings"])


@router.post("", response_model=BriefingResponse, status_code=status.HTTP_201_CREATED)
async def create_briefing(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates a personalized audio/video weekly executive briefing synthesizing
    the user's top 3 matched opportunities with script and media.
    """
    briefing = await BriefingService.create_briefing(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
    )
    res = await BriefingService.get_briefing(db=db, briefing_id=briefing.id, user_id=current_user.id)
    if not res:
        raise HTTPException(status_code=500, detail={"error": {"code": "BRIEFING_ERROR", "message": "Failed to create briefing."}})
    return res


@router.get("", response_model=List[BriefingResponse])
async def list_briefings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves all past and active briefings generated for the authenticated user.
    """
    return await BriefingService.list_user_briefings(db=db, user_id=current_user.id)


@router.get("/{briefing_id}", response_model=BriefingResponse)
async def get_briefing(
    briefing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves a specific briefing by ID with linked top-ranked opportunities.
    """
    briefing = await BriefingService.get_briefing(
        db=db,
        briefing_id=briefing_id,
        user_id=current_user.id,
    )
    if not briefing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Briefing not found."}},
        )
    return briefing


@router.post("/{briefing_id}/retry", response_model=BriefingResponse)
async def retry_briefing(
    briefing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retries generation for a failed briefing.
    """
    existing = await BriefingService.get_briefing(db=db, briefing_id=briefing_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Briefing not found."}},
        )

    # Re-generate
    briefing = await BriefingService.create_briefing(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
    )
    return await BriefingService.get_briefing(db=db, briefing_id=briefing.id, user_id=current_user.id)
