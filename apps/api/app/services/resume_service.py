import os
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.embeddings.provider import embedding_provider
from app.embeddings.templates import build_resume_embedding_text
from app.models.resume import Resume
from app.repositories.resume_repo import ResumeRepository
from app.services.matching_service import MatchingService
from app.services.pdf_service import PDFService


class ResumeService:
    """
    Coordinates PDF resume parsing, embedding generation, versioning,
    and automatic matching recalculation.
    """
    @staticmethod
    async def process_resume_upload(
        db: AsyncSession,
        user_id: str,
        file_name: str,
        pdf_bytes: bytes,
    ) -> Tuple[Resume, int]:
        # 1. Extract text using PyMuPDF
        extracted_text, content_hash = PDFService.extract_text_from_pdf_bytes(pdf_bytes)

        # 2. Deactivate previous active resumes
        await ResumeRepository.deactivate_all_for_user(db, user_id)

        # 3. Generate 384-dimensional vector embedding
        embed_input = build_resume_embedding_text(extracted_text)
        embedding = embedding_provider.embed_text(embed_input)

        # 4. Save file locally in storage directory if configured
        storage_dir = settings.STORAGE_LOCAL_DIR
        os.makedirs(storage_dir, exist_ok=True)
        safe_file_name = f"{user_id}_{content_hash[:12]}_{file_name}"
        file_path = os.path.join(storage_dir, safe_file_name)
        try:
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)
            file_url = f"/storage/resumes/{safe_file_name}"
        except Exception as exc:
            logger.warning(f"Could not persist PDF file to disk: {exc}")
            file_url = f"inline://{safe_file_name}"

        # 5. Persist Resume record
        resume = await ResumeRepository.create(
            db=db,
            user_id=user_id,
            file_name=file_name,
            file_url=file_url,
            extracted_text=extracted_text,
            content_hash=content_hash,
            embedding=embedding,
            processing_status="ready",
        )

        # 6. Recalculate matches across active listings
        matches_count = await MatchingService.recalculate_all_matches_for_resume(db, resume)

        logger.info(f"Processed resume for user {user_id}: {matches_count} listings matched.")
        return resume, matches_count
