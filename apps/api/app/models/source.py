from datetime import datetime, timezone
import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.raw_listing import RawListing


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    base_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    scraper_key: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    raw_listings: Mapped[List["RawListing"]] = relationship(
        "RawListing",
        back_populates="source",
    )
