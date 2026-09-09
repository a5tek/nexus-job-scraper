from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resume import Resume
from app.repositories.base import enforce_user_scope


class ResumeRepository:
    """
    Repository for candidate Resume records with strict user scoping.
    """
    @staticmethod
    async def get_active_by_user_id(db: AsyncSession, user_id: str) -> Optional[Resume]:
        query = select(Resume).where(
            Resume.user_id == user_id,
            Resume.is_active == True,
        ).order_by(Resume.created_at.desc())
        res = await db.execute(query)
        return res.scalars().first()

    @staticmethod
    async def get_by_id_and_user_id(db: AsyncSession, resume_id: str, user_id: str) -> Optional[Resume]:
        query = select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def deactivate_all_for_user(db: AsyncSession, user_id: str) -> None:
        stmt = (
            update(Resume)
            .where(Resume.user_id == user_id, Resume.is_active == True)
            .values(is_active=False)
        )
        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: str,
        file_name: str,
        file_url: str,
        extracted_text: str,
        content_hash: str,
        embedding: List[float],
        processing_status: str = "ready",
    ) -> Resume:
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            file_url=file_url,
            extracted_text=extracted_text,
            content_hash=content_hash,
            embedding=embedding,
            is_active=True,
            processing_status=processing_status,
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        return resume

    @staticmethod
    async def update_status(
        db: AsyncSession,
        resume_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> Optional[Resume]:
        stmt = select(Resume).where(Resume.id == resume_id)
        res = await db.execute(stmt)
        resume = res.scalar_one_or_none()
        if resume:
            resume.processing_status = status
            resume.error_message = error_message
            await db.commit()
            await db.refresh(resume)
        return resume
