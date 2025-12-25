"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import auth_rate_limit
from app.models import User
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user"""
    auth_service = AuthService(db)
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limit),
) -> TokenResponse:
    """Login with email and password"""
    auth_service = AuthService(db)
    return await auth_service.login_user(login_data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Refresh access token"""
    auth_service = AuthService(db)
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    """Logout user (invalidate session)"""
    # In a real implementation, you would invalidate the token
    # For JWT tokens, you might maintain a blacklist in Redis
    # For now, we'll just return success
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.post("/oauth/github", response_model=TokenResponse)
async def github_oauth(
    oauth_data: dict, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Handle GitHub OAuth callback"""
    required_fields = ["github_id", "email", "name"]

    for field in required_fields:
        if field not in oauth_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}",
            )

    auth_service = AuthService(db)
    return await auth_service.oauth_login(
        provider="github",
        provider_id=str(oauth_data["github_id"]),
        email=oauth_data["email"],
        name=oauth_data["name"],
        avatar_url=oauth_data.get("avatar_url"),
    )


@router.post("/oauth/google", response_model=TokenResponse)
async def google_oauth(
    oauth_data: dict, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Handle Google OAuth callback"""
    required_fields = ["google_id", "email", "name"]

    for field in required_fields:
        if field not in oauth_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}",
            )

    auth_service = AuthService(db)
    return await auth_service.oauth_login(
        provider="google",
        provider_id=str(oauth_data["google_id"]),
        email=oauth_data["email"],
        name=oauth_data["name"],
        avatar_url=oauth_data.get("avatar_url"),
    )
