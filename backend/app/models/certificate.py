"""
Certificate models for tracking user achievements
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class CertificateType(str, Enum):
    """Certificate types"""

    TRACK_COMPLETION = "track_completion"
    CHALLENGE_MASTERY = "challenge_mastery"
    STREAK_MILESTONE = "streak_milestone"
    ACHIEVEMENT = "achievement"


class CertificateStatus(str, Enum):
    """Certificate status"""

    PENDING = "pending"
    GENERATED = "generated"
    DELIVERED = "delivered"
    REVOKED = "revoked"


class Certificate(Base):
    """Certificate model for user achievements"""

    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # References
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Certificate details
    type: Mapped[CertificateType] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Achievement data
    achievement_data: Mapped[dict] = mapped_column(
        JSON, nullable=False
    )  # Track, challenges completed, etc.

    # Certificate metadata
    certificate_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    verification_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    # Status and generation
    status: Mapped[CertificateStatus] = mapped_column(
        String(20), default=CertificateStatus.PENDING, nullable=False
    )
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pdf_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metadata
    template_version: Mapped[str] = mapped_column(
        String(20), default="1.0", nullable=False
    )
    issuer: Mapped[str] = mapped_column(
        String(100), default="Weak-to-Strong Platform", nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="certificates")

    def __repr__(self) -> str:
        return f"<Certificate(id={self.id}, user_id={self.user_id}, type='{self.type.value}')>"

    @property
    def verification_url(self) -> str:
        """Get verification URL for this certificate"""
        from app.core.config import settings

        return f"{settings.api_url}/certificates/verify/{self.verification_code}"

    @property
    def is_generated(self) -> bool:
        """Check if certificate PDF has been generated"""
        return self.status in [CertificateStatus.GENERATED, CertificateStatus.DELIVERED]

    @property
    def display_achievement(self) -> str:
        """Get display text for the achievement"""
        if self.type == CertificateType.TRACK_COMPLETION:
            track = self.achievement_data.get("track", "").title()
            return f"{track} Track Completion"
        elif self.type == CertificateType.STREAK_MILESTONE:
            days = self.achievement_data.get("streak_days", 0)
            return f"{days}-Day Streak Milestone"
        elif self.type == CertificateType.CHALLENGE_MASTERY:
            count = self.achievement_data.get("challenges_completed", 0)
            return f"{count} Challenges Mastered"
        else:
            return self.title

    def generate_certificate_number(self) -> str:
        """Generate unique certificate number"""
        year = self.earned_at.year
        month = self.earned_at.month
        # Format: WTS-YYYY-MM-XXXXXX (last 6 chars of UUID)
        short_id = str(self.id).replace("-", "")[-6:].upper()
        return f"WTS-{year:04d}-{month:02d}-{short_id}"

    def generate_verification_code(self) -> str:
        """Generate unique verification code"""
        # Format: VER-XXXXXX-YYYY (6 chars from UUID + 4 random)
        import secrets

        short_id = str(self.id).replace("-", "")[-6:].upper()
        random_suffix = secrets.token_hex(2).upper()
        return f"VER-{short_id}-{random_suffix}"
