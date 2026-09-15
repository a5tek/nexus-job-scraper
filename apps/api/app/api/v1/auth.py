from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    response: Response,
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new candidate account and receive an access token and HttpOnly cookie."""
    token_response = await AuthService.register(db, data)
    response.set_cookie(
        key="nexus_token",
        value=token_response.access_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return token_response


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Log in with email and password to receive an access token and HttpOnly cookie."""
    token_response = await AuthService.login(db, data)
    response.set_cookie(
        key="nexus_token",
        value=token_response.access_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return token_response


@router.post("/logout")
async def logout(response: Response):
    """Clear the authentication session cookie."""
    response.delete_cookie(key="nexus_token", path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get the authenticated user's profile."""
    return UserResponse.model_validate(current_user)
