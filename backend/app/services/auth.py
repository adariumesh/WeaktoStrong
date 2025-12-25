"""
Authentication service for user registration, login, and OAuth
"""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_session_tokens, get_password_hash, verify_password
from app.models import User, UserTier
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        """Register a new user with email and password"""

        # Check if user already exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            password_hash=hashed_password,
            name=user_data.name,
            tier="free",
            tokens_used_today=0,
            is_active=True,
            is_verified=False,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # Create tokens
        tokens = create_session_tokens(str(new_user.id))

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse.model_validate(new_user),
        )

    async def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user with email and password"""

        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Verify password
        if not user.password_hash or not verify_password(
            login_data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Account is disabled"
            )

        # Update last login
        user.last_login = datetime.now(UTC)
        await self.db.commit()

        # Create tokens
        tokens = create_session_tokens(str(user.id))

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse.model_validate(user),
        )

    async def oauth_login(
        self,
        provider: str,
        provider_id: str,
        email: str,
        name: str,
        avatar_url: str | None = None,
    ) -> TokenResponse:
        """Handle OAuth login (GitHub, Google, etc.)"""

        # Try to find existing user by provider ID
        if provider == "github":
            result = await self.db.execute(
                select(User).where(User.github_id == provider_id)
            )
        elif provider == "google":
            result = await self.db.execute(
                select(User).where(User.google_id == provider_id)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}",
            )

        user = result.scalar_one_or_none()

        if user:
            # Update user info and last login
            user.name = name
            user.avatar_url = avatar_url or user.avatar_url
            user.last_login = datetime.now(UTC)
        else:
            # Check if user exists with same email
            result = await self.db.execute(select(User).where(User.email == email))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                # Link the OAuth account to existing user
                if provider == "github":
                    existing_user.github_id = provider_id
                elif provider == "google":
                    existing_user.google_id = provider_id

                existing_user.avatar_url = avatar_url or existing_user.avatar_url
                existing_user.last_login = datetime.now(UTC)
                user = existing_user
            else:
                # Create new user
                user = User(
                    id=uuid.uuid4(),
                    email=email,
                    name=name,
                    avatar_url=avatar_url,
                    tier=UserTier.FREE,
                    tokens_used_today=0,
                    is_active=True,
                    is_verified=True,  # OAuth users are auto-verified
                    last_login=datetime.now(UTC),
                )

                if provider == "github":
                    user.github_id = provider_id
                elif provider == "google":
                    user.google_id = provider_id

                self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        # Create tokens
        tokens = create_session_tokens(str(user.id))

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse.model_validate(user),
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        from app.core.auth import verify_token

        # Verify refresh token
        payload = verify_token(refresh_token, "refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Get user
        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Create new tokens
        tokens = create_session_tokens(str(user.id))

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse.model_validate(user),
        )
