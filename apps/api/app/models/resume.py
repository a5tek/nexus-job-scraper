import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.db.types import CompatibleVector

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.match import Match


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

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
    file_url: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    extracted_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        CompatibleVector(384),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    processing_status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",  # uploaded, reading, understanding, matching, ready, failed
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="resumes",
    )
    matches: Mapped[List["Match"]] = relationship(
        "Match",
        back_populates="resume",
        cascade="all, delete-orphan",
    )
