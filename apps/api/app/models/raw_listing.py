from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.source import Source
    from app.models.listing import Listing


class RawListing(Base, TimestampMixin):
    __tablename__ = "raw_listings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    source_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    source_listing_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    source_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )
    canonical_url: Mapped[str] = mapped_column(
        String(2048),
        index=True,
        nullable=False,
    )
    raw_title: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    raw_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    dedupe_key: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        index=True,
        nullable=False,
    )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    extraction_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",  # pending, extracted, failed
        nullable=False,
    )

    # Relationships
    source: Mapped[Optional["Source"]] = relationship(
        "Source",
        back_populates="raw_listings",
    )
    listing: Mapped[Optional["Listing"]] = relationship(
        "Listing",
        back_populates="raw_listing",
        uselist=False,
        cascade="all, delete-orphan",
    )
