"""
Certificate API endpoints for user achievements and PDF generation
"""

import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.certificates import (
    CertificateResponse,
    CertificateVerificationResponse,
)
from app.services.certificate_service import CertificateService

router = APIRouter(tags=["certificates"])


@router.get("/", response_model=list[CertificateResponse])
async def get_user_certificates(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get all certificates for the current user"""
    service = CertificateService(db)
    certificates = await service.get_user_certificates(current_user.id)

    return [
        CertificateResponse(
            id=cert.id,
            type=cert.type.value,
            title=cert.title,
            description=cert.description,
            certificate_number=cert.certificate_number,
            verification_code=cert.verification_code,
            status=cert.status.value,
            achievement_data=cert.achievement_data,
            earned_at=cert.earned_at,
            generated_at=cert.generated_at,
            verification_url=cert.verification_url,
            is_generated=cert.is_generated,
            display_achievement=cert.display_achievement,
        )
        for cert in certificates
    ]


@router.post("/check-awards")
async def check_certificate_awards(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Check if user qualifies for new certificates and award them"""
    service = CertificateService(db)
    new_certificates = await service.check_and_award_certificates(current_user.id)

    return {
        "new_certificates": len(new_certificates),
        "certificates": [
            {
                "id": str(cert.id),
                "type": cert.type.value,
                "title": cert.title,
                "achievement": cert.display_achievement,
            }
            for cert in new_certificates
        ],
    }


@router.get("/{certificate_id}/pdf")
async def get_certificate_pdf(
    certificate_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download certificate PDF"""
    service = CertificateService(db)

    # Get certificate and verify ownership
    certificate = await service.get_certificate_by_id(certificate_id)
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found"
        )

    if certificate.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this certificate",
        )

    # Generate PDF if not already generated
    if not certificate.is_generated:
        pdf_path = await service.generate_certificate_pdf(certificate_id)
        if not pdf_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate certificate PDF",
            )
    else:
        pdf_path = certificate.pdf_path

    # Verify file exists
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certificate PDF not found"
        )

    # Return file
    filename = (
        f"{certificate.title.replace(' ', '_')}_{certificate.certificate_number}.pdf"
    )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/{certificate_id}/generate")
async def generate_certificate_pdf(
    certificate_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate PDF for a certificate"""
    service = CertificateService(db)

    # Get certificate and verify ownership
    certificate = await service.get_certificate_by_id(certificate_id)
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found"
        )

    if certificate.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this certificate",
        )

    # Generate PDF
    pdf_path = await service.generate_certificate_pdf(certificate_id)
    if not pdf_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate certificate PDF",
        )

    return {
        "message": "Certificate PDF generated successfully",
        "certificate_id": str(certificate_id),
        "pdf_generated": True,
        "download_url": f"/api/v1/certificates/{certificate_id}/pdf",
    }


@router.get(
    "/verify/{verification_code}", response_model=CertificateVerificationResponse
)
async def verify_certificate(
    verification_code: str, db: AsyncSession = Depends(get_db)
):
    """Verify a certificate by its verification code (public endpoint)"""
    service = CertificateService(db)
    certificate = await service.verify_certificate(verification_code)

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found or invalid verification code",
        )

    return CertificateVerificationResponse(
        valid=True,
        certificate_id=certificate.id,
        certificate_number=certificate.certificate_number,
        title=certificate.title,
        recipient_name=certificate.user.name,
        issued_date=certificate.earned_at,
        issuer=certificate.issuer,
        type=certificate.type.value,
        description=certificate.description,
        achievement_data=certificate.achievement_data,
    )


@router.get("/public/stats")
async def get_certificate_stats(db: AsyncSession = Depends(get_db)):
    """Get public certificate statistics"""
    from sqlalchemy import func, select

    from app.models.certificate import Certificate, CertificateType

    # Get certificate counts by type
    result = await db.execute(
        select(Certificate.type, func.count(Certificate.id).label("count")).group_by(
            Certificate.type
        )
    )

    stats_by_type = {row.type.value: row.count for row in result.fetchall()}

    # Get total certificates
    result = await db.execute(select(func.count(Certificate.id)))
    total_certificates = result.scalar() or 0

    # Get recent certificates (last 30 days)
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=30)

    result = await db.execute(
        select(func.count(Certificate.id)).where(Certificate.earned_at >= cutoff)
    )
    recent_certificates = result.scalar() or 0

    return {
        "total_certificates": total_certificates,
        "recent_certificates": recent_certificates,
        "certificates_by_type": stats_by_type,
        "available_types": [t.value for t in CertificateType],
    }
