import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.resume import Resume
    from app.models.listing import Listing


class Match(Base, TimestampMixin):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("user_id", "resume_id", "listing_id", name="uq_user_resume_listing_match"),
    )

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
    resume_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    listing_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("listings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    similarity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    display_score: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )
    justification: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    match_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="matches",
    )
    resume: Mapped["Resume"] = relationship(
        "Resume",
        back_populates="matches",
    )
    listing: Mapped["Listing"] = relationship(
        "Listing",
        back_populates="matches",
    )
