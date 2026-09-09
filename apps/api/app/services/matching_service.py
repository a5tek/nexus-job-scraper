import hashlib
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.embeddings.base import EmbeddingProvider
from app.embeddings.provider import embedding_provider
from app.models.listing import Listing
from app.models.match import Match
from app.models.resume import Resume
from app.repositories.match_repo import MatchRepository
from app.llm.gemini import gemini_client

EXPLANATION_CACHE: dict = {}


def calculate_display_score(similarity: float) -> int:
    """
    Normalizes cosine similarity (-1.0 to 1.0) into an intuitive 0-100 display percentage.
    Conforms to PRD Section 6.5 & TECH_STACK Section 16.
    """
    # Scale realistic text cosine similarity (0.1 to 0.85) to 25-99%
    scaled = ((similarity + 0.15) / 0.95) * 100
    return int(max(10, min(99, round(scaled))))


class MatchingService:
    """
    Service for calculating vector similarity, scores, and evidence-based explanations
    between user resumes and job listings.
    """
    @staticmethod
    def _compute_explanation_cache_key(resume_hash: str, listing_id: str) -> str:
        composite = f"{resume_hash}:{listing_id}:{settings.MATCH_EXPLANATION_VERSION}"
        return hashlib.sha256(composite.encode("utf-8")).hexdigest()

    @staticmethod
    async def generate_explanation(
        resume_text: str,
        resume_hash: str,
        listing: Listing,
    ) -> str:
        cache_key = MatchingService._compute_explanation_cache_key(resume_hash, listing.id)
        if cache_key in EXPLANATION_CACHE:
            return EXPLANATION_CACHE[cache_key]

        skills_list = listing.required_skills or []
        skills_str = ", ".join(skills_list[:5]) if skills_list else "software engineering"

        # Check skill overlap directly for high-signal evidence
        matching_skills = [s for s in skills_list if s.lower() in resume_text.lower()]
        
        if matching_skills:
            evidence = f"Strong match because your experience with {', '.join(matching_skills[:3])} aligns directly with {listing.company}'s requirements for this {listing.title} role."
        elif "remote" in (listing.location or "").lower() or listing.remote_ok:
            evidence = f"Good match for your software background, offering a remote-friendly position working on {listing.title} at {listing.company}."
        else:
            evidence = f"Matches your engineering foundation, with opportunities to apply and expand your skills at {listing.company}."

        EXPLANATION_CACHE[cache_key] = evidence
        return evidence

    @staticmethod
    async def match_resume_with_listing(
        db: AsyncSession,
        resume: Resume,
        listing: Listing,
    ) -> Match:
        if not resume.embedding or not listing.embedding:
            similarity = 0.0
        else:
            similarity = EmbeddingProvider.cosine_similarity(resume.embedding, listing.embedding)

        display_score = calculate_display_score(similarity)
        justification = await MatchingService.generate_explanation(
            resume_text=resume.extracted_text or "",
            resume_hash=resume.content_hash or "empty",
            listing=listing,
        )

        return await MatchRepository.upsert_match(
            db=db,
            user_id=resume.user_id,
            resume_id=resume.id,
            listing_id=listing.id,
            similarity=round(similarity, 4),
            display_score=display_score,
            justification=justification,
            match_version=settings.MATCH_EXPLANATION_VERSION,
        )

    @staticmethod
    async def recalculate_all_matches_for_resume(
        db: AsyncSession,
        resume: Resume,
    ) -> int:
        """
        Recalculates matches between this active resume and all active listings in the platform.
        """
        stmt = select(Listing).where(Listing.embedding.isnot(None))
        res = await db.execute(stmt)
        listings = res.scalars().all()

        match_count = 0
        for listing in listings:
            await MatchingService.match_resume_with_listing(db, resume, listing)
            match_count += 1

        logger.info(f"Calculated {match_count} matches for user {resume.user_id} (resume {resume.id})")
        return match_count
