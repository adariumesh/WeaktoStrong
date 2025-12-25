"""
Pydantic schemas for authentication
"""

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserTier


class UserCreate(BaseModel):
    """Schema for user registration"""

    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Custom email validation that allows .local domains for testing"""
        import re

        # Basic email pattern that allows .local domains
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")

        # Convert to lowercase for consistency
        return v.lower()


class UserLogin(BaseModel):
    """Schema for user login"""

    email: str = Field(..., description="Email address")
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Custom email validation that allows .local domains for testing"""
        import re

        # Basic email pattern that allows .local domains
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")

        # Convert to lowercase for consistency
        return v.lower()


class UserResponse(BaseModel):
    """Schema for user data in responses"""

    id: uuid.UUID
    email: str
    name: str
    avatar_url: str | None = None
    tier: str
    tokens_used_today: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile"""

    name: str | None = Field(None, min_length=1, max_length=255)
    avatar_url: str | None = None


class TokenResponse(BaseModel):
    """Schema for authentication token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_in: int  # seconds
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request"""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
