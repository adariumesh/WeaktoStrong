"""
Pydantic schemas for certificate API responses
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CertificateResponse(BaseModel):
    """Certificate response model"""

    id: UUID
    type: str = Field(
        description="Certificate type (track_completion, challenge_mastery, etc.)"
    )
    title: str = Field(description="Certificate title")
    description: str = Field(description="Achievement description")
    certificate_number: str = Field(description="Unique certificate number")
    verification_code: str = Field(
        description="Verification code for public validation"
    )
    status: str = Field(
        description="Certificate status (pending, generated, delivered)"
    )
    achievement_data: dict[str, Any] = Field(description="Achievement details")
    earned_at: datetime = Field(description="When the certificate was earned")
    generated_at: datetime | None = Field(description="When the PDF was generated")
    verification_url: str = Field(description="URL for public verification")
    is_generated: bool = Field(description="Whether PDF has been generated")
    display_achievement: str = Field(
        description="Human-readable achievement description"
    )

    class Config:
        from_attributes = True


class CertificateVerificationResponse(BaseModel):
    """Certificate verification response for public verification"""

    valid: bool = Field(description="Whether the certificate is valid")
    certificate_id: UUID = Field(description="Certificate ID")
    certificate_number: str = Field(description="Certificate number")
    title: str = Field(description="Certificate title")
    recipient_name: str = Field(description="Name of certificate recipient")
    issued_date: datetime = Field(description="Date certificate was issued")
    issuer: str = Field(description="Certificate issuer")
    type: str = Field(description="Certificate type")
    description: str = Field(description="Achievement description")
    achievement_data: dict[str, Any] = Field(description="Achievement details")

    class Config:
        from_attributes = True


class CertificateListResponse(BaseModel):
    """Response for listing certificates"""

    certificates: list[CertificateResponse]
    total_count: int = Field(description="Total number of certificates")
    generated_count: int = Field(
        description="Number of certificates with PDFs generated"
    )

    class Config:
        from_attributes = True


class CertificateAwardRequest(BaseModel):
    """Request to manually award a certificate (admin only)"""

    user_id: UUID = Field(description="User to award certificate to")
    type: str = Field(description="Certificate type")
    title: str = Field(description="Certificate title")
    description: str = Field(description="Achievement description")
    achievement_data: dict[str, Any] = Field(description="Achievement details")


class CertificateStatsResponse(BaseModel):
    """Public certificate statistics"""

    total_certificates: int = Field(description="Total certificates issued")
    recent_certificates: int = Field(description="Certificates issued in last 30 days")
    certificates_by_type: dict[str, int] = Field(
        description="Breakdown by certificate type"
    )
    available_types: list[str] = Field(description="Available certificate types")

    class Config:
        from_attributes = True
