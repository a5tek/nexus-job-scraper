from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.source import Source
from app.models.raw_listing import RawListing
from app.scraping.dedupe import compute_content_hash, compute_dedupe_key, normalize_canonical_url
from app.scraping.schemas import ListingCandidate


class RawListingRepository:
    """
    Repository for managing RawListing records and Source entities.
    Enforces deduplication, canonical URL storage, content hashing, and upsert logic.
    """
    @staticmethod
    async def get_or_create_source(
        db: AsyncSession,
        name: str,
        base_url: str,
        scraper_key: str,
    ) -> Source:
        stmt = select(Source).where(Source.name == name)
        res = await db.execute(stmt)
        source = res.scalar_one_or_none()

        if not source:
            source = Source(
                name=name,
                base_url=base_url,
                scraper_key=scraper_key,
                is_enabled=True,
            )
            db.add(source)
            await db.commit()
            await db.refresh(source)
        return source

    @staticmethod
    async def upsert_candidate(
        db: AsyncSession,
        source_id: str,
        candidate: ListingCandidate,
    ) -> Tuple[RawListing, str]:
        """
        Upserts a candidate listing:
        Returns (RawListing, status) where status is:
          - 'inserted': Newly created record
          - 'updated': Content hash changed -> raw content updated, extraction_status reset to pending
          - 'unchanged': Same content hash -> only last_seen_at refreshed
        """
        now = datetime.now(timezone.utc)
        canonical_url = normalize_canonical_url(candidate.source_url)
        content_hash = compute_content_hash(candidate.raw_content)

        dedupe_key = compute_dedupe_key(
            source_name=candidate.source_name,
            source_listing_id=candidate.source_listing_id,
            canonical_url=canonical_url,
            content_hash=content_hash,
        )

        # Check for existing listing by dedupe_key
        stmt = select(RawListing).where(RawListing.dedupe_key == dedupe_key)
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing is None:
            # Insert unseen listing
            raw = RawListing(
                source_id=source_id,
                source_listing_id=candidate.source_listing_id,
                source_url=candidate.source_url,
                canonical_url=canonical_url,
                raw_title=candidate.raw_title,
                raw_content=candidate.raw_content,
                dedupe_key=dedupe_key,
                content_hash=content_hash,
                scraped_at=now,
                first_seen_at=now,
                last_seen_at=now,
                is_active=True,
                extraction_status="pending",
            )
            db.add(raw)
            await db.commit()
            await db.refresh(raw)
            return raw, "inserted"

        # Check if content changed
        if existing.content_hash != content_hash:
            # Content changed: update raw content, reset extraction status to pending, mark stale
            existing.raw_content = candidate.raw_content
            existing.raw_title = candidate.raw_title
            existing.content_hash = content_hash
            existing.last_seen_at = now
            existing.is_active = True
            existing.extraction_status = "pending"
            await db.commit()
            await db.refresh(existing)
            return existing, "updated"
        else:
            # Identical existing listing: update last_seen_at
            existing.last_seen_at = now
            existing.is_active = True
            await db.commit()
            await db.refresh(existing)
            return existing, "unchanged"
