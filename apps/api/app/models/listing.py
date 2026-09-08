from datetime import date
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Date, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.db.types import CompatibleVector

if TYPE_CHECKING:
    from app.models.raw_listing import RawListing
    from app.models.match import Match
    from app.models.saved_listing import SavedListing
    from app.models.briefing_listing import BriefingListing


class Listing(Base, TimestampMixin):
    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    raw_listing_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("raw_listings.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    remote_ok: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        index=True,
    )
    stipend: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    required_skills: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    experience_level: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    deadline: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        CompatibleVector(384),
        nullable=True,
    )
    extractor_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Relationships
    raw_listing: Mapped["RawListing"] = relationship(
        "RawListing",
        back_populates="listing",
    )
    matches: Mapped[List["Match"]] = relationship(
        "Match",
        back_populates="listing",
        cascade="all, delete-orphan",
    )
    saved_by_users: Mapped[List["SavedListing"]] = relationship(
        "SavedListing",
        back_populates="listing",
        cascade="all, delete-orphan",
    )
    briefing_links: Mapped[List["BriefingListing"]] = relationship(
        "BriefingListing",
        back_populates="listing",
        cascade="all, delete-orphan",
    )
