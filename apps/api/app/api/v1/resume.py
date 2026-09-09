from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.match import Match
from app.models.user import User
from app.repositories.resume_repo import ResumeRepository
from app.schemas.resume import ResumeResponse, ResumeStatusResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Uploads a candidate PDF resume.
    Extracts text using PyMuPDF, computes vector embedding, and updates job matches.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_FILE_TYPE", "message": "Only PDF files are supported."}},
        )

    # Read up to 10MB
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error": {"code": "FILE_TOO_LARGE", "message": "Resume file size exceeds the 10MB limit."}},
        )

    resume, _ = await ResumeService.process_resume_upload(
        db=db,
        user_id=current_user.id,
        file_name=file.filename,
        pdf_bytes=contents,
    )
    return ResumeResponse.model_validate(resume)


@router.get("", response_model=ResumeResponse)
async def get_active_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the candidate's active resume.
    """
    resume = await ResumeRepository.get_active_by_user_id(db, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "RESUME_NOT_FOUND", "message": "No active resume uploaded."}},
        )
    return ResumeResponse.model_validate(resume)


@router.get("/status", response_model=ResumeStatusResponse)
async def get_resume_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the processing status of the active resume.
    """
    resume = await ResumeRepository.get_active_by_user_id(db, current_user.id)
    if not resume:
        return ResumeStatusResponse(
            id="",
            has_active_resume=False,
            file_name=None,
            processing_status="none",
            is_active=False,
            matches_calculated=0,
        )

    # Count calculated matches
    count_stmt = select(func.count(Match.id)).where(Match.user_id == current_user.id)
    res = await db.execute(count_stmt)
    match_count = res.scalar() or 0

    return ResumeStatusResponse(
        id=resume.id,
        has_active_resume=True,
        file_name=resume.file_name,
        processing_status=resume.processing_status,
        is_active=resume.is_active,
        error_message=resume.error_message,
        matches_calculated=match_count,
    )


@router.post("/match", response_model=ResumeStatusResponse)
async def rematch_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Forces recalculation of semantic matches across all opportunities for the active resume.
    """
    resume = await ResumeRepository.get_active_by_user_id(db, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "RESUME_NOT_FOUND", "message": "No active resume to match against."}},
        )

    match_count = await ResumeService.recalculate_matches_for_user(db, current_user.id)
    return ResumeStatusResponse(
        id=resume.id,
        has_active_resume=True,
        file_name=resume.file_name,
        processing_status="ready",
        is_active=True,
        matches_calculated=match_count,
    )
