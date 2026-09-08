import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.saved_listing import SavedListing
    from app.models.match import Match
    from app.models.briefing import Briefing
    from app.models.usage_event import UsageEvent


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    resumes: Mapped[List["Resume"]] = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    saved_listings: Mapped[List["SavedListing"]] = relationship(
        "SavedListing",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    matches: Mapped[List["Match"]] = relationship(
        "Match",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    briefings: Mapped[List["Briefing"]] = relationship(
        "Briefing",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    usage_events: Mapped[List["UsageEvent"]] = relationship(
        "UsageEvent",
        back_populates="user",
    )
