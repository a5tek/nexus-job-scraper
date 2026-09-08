from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.listing import Listing


class SavedListing(Base):
    __tablename__ = "saved_listings"
    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_saved_listing"),
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
    listing_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("listings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="saved_listings",
    )
    listing: Mapped["Listing"] = relationship(
        "Listing",
        back_populates="saved_by_users",
    )
