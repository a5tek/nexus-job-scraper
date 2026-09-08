from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        query = select(User).where(User.email == email.lower().strip())
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, email: str, password_hash: str, name: str) -> User:
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            name=name.strip(),
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
