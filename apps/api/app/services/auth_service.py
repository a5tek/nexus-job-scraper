from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, data: UserRegister) -> TokenResponse:
        existing = await UserRepository.get_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "EMAIL_ALREADY_EXISTS", "message": "An account with this email already exists."}}
            )

        hashed_pwd = hash_password(data.password)
        user = await UserRepository.create(
            db=db,
            email=data.email,
            password_hash=hashed_pwd,
            name=data.name,
        )

        token = create_access_token(subject=user.id)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin) -> TokenResponse:
        user = await UserRepository.get_by_email(db, data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}}
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "ACCOUNT_DISABLED", "message": "Your account has been deactivated."}}
            )

        token = create_access_token(subject=user.id)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
