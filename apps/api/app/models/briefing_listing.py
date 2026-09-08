import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.briefing import Briefing
    from app.models.listing import Listing


class BriefingListing(Base):
    __tablename__ = "briefing_listings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    briefing_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("briefings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    listing_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("listings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Relationships
    briefing: Mapped["Briefing"] = relationship(
        "Briefing",
        back_populates="listing_links",
    )
    listing: Mapped["Listing"] = relationship(
        "Listing",
        back_populates="briefing_links",
    )
