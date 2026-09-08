from datetime import datetime, timezone
import uuid
from typing import Any, Dict
from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ExtractionCache(Base):
    __tablename__ = "extraction_cache"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    cache_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    extractor_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    raw_content_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )
    structured_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
