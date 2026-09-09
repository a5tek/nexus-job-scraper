from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.provider import embedding_provider
from app.embeddings.templates import build_listing_embedding_text
from app.models.listing import Listing
from app.llm.schemas import ExtractedListing


from sqlalchemy.orm import selectinload


class ListingRepository:
    """
    Repository for managing normalized Listing records and semantic search.
    """
    @staticmethod
    async def get_by_id(db: AsyncSession, listing_id: str) -> Optional[Listing]:
        stmt = select(Listing).options(selectinload(Listing.raw_listing)).where(Listing.id == listing_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_raw_listing_id(db: AsyncSession, raw_listing_id: str) -> Optional[Listing]:
        stmt = select(Listing).options(selectinload(Listing.raw_listing)).where(Listing.raw_listing_id == raw_listing_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


    @staticmethod
    async def upsert_from_extraction(
        db: AsyncSession,
        raw_listing_id: str,
        extracted: ExtractedListing,
        raw_content: Optional[str] = None,
    ) -> Listing:
        existing = await ListingRepository.get_by_raw_listing_id(db, raw_listing_id)

        # Build embedding text and generate embedding
        embed_text = build_listing_embedding_text(
            title=extracted.title,
            company=extracted.company,
            location=extracted.location,
            remote_ok=extracted.remote_ok,
            experience_level=extracted.experience_level,
            required_skills=extracted.required_skills,
            description_snippet=raw_content,
        )
        vector = embedding_provider.embed_text(embed_text)

        if existing:
            existing.title = extracted.title or "Software Engineer"
            existing.company = extracted.company or "Company"
            existing.location = extracted.location
            existing.remote_ok = extracted.remote_ok
            existing.stipend = extracted.stipend
            existing.required_skills = extracted.required_skills
            existing.experience_level = extracted.experience_level
            existing.deadline = extracted.deadline
            existing.embedding = vector
            existing.extractor_version = settings.EXTRACTOR_VERSION
            await db.commit()
            await db.refresh(existing)
            return existing

        new_listing = Listing(
            raw_listing_id=raw_listing_id,
            title=extracted.title or "Software Engineer",
            company=extracted.company or "Company",
            location=extracted.location,
            remote_ok=extracted.remote_ok,
            stipend=extracted.stipend,
            required_skills=extracted.required_skills,
            experience_level=extracted.experience_level,
            deadline=extracted.deadline,
            embedding=vector,
            extractor_version=settings.EXTRACTOR_VERSION,
        )
        db.add(new_listing)
        await db.commit()
        await db.refresh(new_listing)
        return new_listing

    @staticmethod
    async def list_listings(
        db: AsyncSession,
        remote_only: Optional[bool] = None,
        experience_level: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Listing]:
        query = select(Listing).options(selectinload(Listing.raw_listing))
        if remote_only is not None:
            query = query.where(Listing.remote_ok == remote_only)
        if experience_level:
            query = query.where(Listing.experience_level.ilike(f"%{experience_level}%"))
        if company:
            query = query.where(Listing.company.ilike(f"%{company}%"))

        query = query.order_by(desc(Listing.created_at)).offset(offset).limit(limit)
        res = await db.execute(query)
        return res.scalars().all()

    @staticmethod
    async def semantic_search(
        db: AsyncSession,
        query_vector: List[float],
        limit: int = 20,
        remote_only: Optional[bool] = None,
    ) -> List[Tuple[Listing, float]]:
        """
        Executes semantic search by ranking listings against query_vector.
        Compatible across both PostgreSQL pgvector and SQLite test fallback.
        """
        query = select(Listing).options(selectinload(Listing.raw_listing)).where(Listing.embedding.isnot(None))

        if remote_only is not None:
            query = query.where(Listing.remote_ok == remote_only)

        res = await db.execute(query)
        listings = res.scalars().all()

        # Score with cosine similarity
        scored = []
        for l in listings:
            if l.embedding:
                sim = EmbeddingProvider.cosine_similarity(query_vector, l.embedding)
                scored.append((l, sim))

        # Sort descending by similarity
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]
