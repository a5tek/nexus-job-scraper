import hashlib
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.models.extraction_cache import ExtractionCache
from app.llm.schemas import ExtractedListing


def compute_extraction_cache_key(
    raw_content_hash: str,
    extractor_version: Optional[str] = None,
    model_name: Optional[str] = None,
) -> str:
    """
    Computes content-addressed cache key:
    SHA256(extractor_version + model_name + raw_content_hash)
    """
    version = extractor_version or settings.EXTRACTOR_VERSION
    model = model_name or settings.GEMINI_MODEL
    composite = f"{version}:{model}:{raw_content_hash}"
    return hashlib.sha256(composite.encode("utf-8")).hexdigest()


class ExtractionCacheService:
    """
    Manages content-addressed cache for LLM extractions.
    Avoids duplicate inference costs for identical raw listings.
    """
    @staticmethod
    async def get(
        db: AsyncSession,
        cache_key: str,
    ) -> Optional[ExtractedListing]:
        stmt = select(ExtractionCache).where(ExtractionCache.cache_key == cache_key)
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            return None

        try:
            return ExtractedListing.model_validate(record.structured_payload)
        except Exception as exc:
            logger.warning(f"Failed to parse cached extraction payload for key {cache_key}: {exc}")
            return None

    @staticmethod
    async def set(
        db: AsyncSession,
        cache_key: str,
        raw_content_hash: str,
        payload: Dict[str, Any],
        model_name: Optional[str] = None,
        extractor_version: Optional[str] = None,
    ) -> ExtractionCache:
        record = ExtractionCache(
            cache_key=cache_key,
            model=model_name or settings.GEMINI_MODEL,
            extractor_version=extractor_version or settings.EXTRACTOR_VERSION,
            raw_content_hash=raw_content_hash,
            structured_payload=payload,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record
