from typing import Any, Type, TypeVar, Optional
from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

T = TypeVar("T", bound=Base)


class MultiTenancyViolationError(HTTPException):
    def __init__(self, message: str = "Resource not found or unauthorized access."):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,  # Return 404 to avoid leaking existence
            detail={"error": {"code": "NOT_FOUND", "message": message}}
        )


def enforce_user_scope(query: Select, model: Type[T], user_id: str) -> Select:
    """
    Appends strict user_id filtering to any query against a user-owned model.
    Guarantees user isolation at the repository query level.
    """
    if not hasattr(model, "user_id"):
        raise ValueError(f"Model {model.__name__} does not have a user_id attribute for scoping.")
    return query.where(model.user_id == user_id)
