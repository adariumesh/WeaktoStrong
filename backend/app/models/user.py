"""
User model for authentication system
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class User(Base):
    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Null for OAuth-only users

    # Profile fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(Text, nullable=True)

    # Subscription & usage
    tier: Mapped[UserTier] = mapped_column(
        ENUM(UserTier, name="user_tier"), default=UserTier.FREE, nullable=False
    )
    tokens_used_today: Mapped[int] = mapped_column(Integer, default=0)

    # OAuth fields
    github_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    google_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)

    # Status flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # AI-related relationships
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    token_usage = relationship(
        "TokenUsage", back_populates="user", cascade="all, delete-orphan"
    )

    # Challenge-related relationships
    submissions = relationship(
        "Submission", back_populates="user", cascade="all, delete-orphan"
    )
    progress = relationship(
        "UserProgress",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    certificates = relationship(
        "Certificate", back_populates="user", cascade="all, delete-orphan"
    )

    # Payment-related relationships
    subscription = relationship(
        "Subscription",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    payments = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', tier='{self.tier.value}')>"

    @property
    def subscription_tier(self) -> str:
        """Get subscription tier as string for AI routing"""
        return self.tier.value

    async def get_daily_token_usage(self, db_session, target_date=None) -> dict:
        """Get AI token usage for a specific date"""
        from .token_usage import TokenUsage

        return await TokenUsage.get_daily_usage(db_session, str(self.id), target_date)

    async def add_token_usage(self, db_session, model: str, tokens: int):
        """Add token usage for this user"""
        from .token_usage import TokenUsage

        await TokenUsage.add_usage(db_session, str(self.id), model, tokens)
