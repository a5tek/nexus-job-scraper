from datetime import datetime
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.briefing_listing import BriefingListing


class Briefing(Base, TimestampMixin):
    __tablename__ = "briefings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="queued",  # queued, processing, done, failed
        index=True,
        nullable=False,
    )
    script: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    provider_job_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    media_url: Mapped[Optional[str]] = mapped_column(
        String(2048),
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="briefings",
    )
    listing_links: Mapped[List["BriefingListing"]] = relationship(
        "BriefingListing",
        back_populates="briefing",
        cascade="all, delete-orphan",
        order_by="BriefingListing.rank",
    )
