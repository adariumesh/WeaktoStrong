"""
Certificate generation and management service
"""

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import qrcode
from reportlab.lib.colors import black, gold, navy
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.logging import get_logger
from app.models.certificate import Certificate, CertificateStatus, CertificateType
from app.models.challenge import ChallengeTrack
from app.models.user import User

logger = get_logger(__name__)


class CertificateService:
    """Service for certificate generation and management"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.certificates_dir = Path(settings.data_dir) / "certificates"
        self.certificates_dir.mkdir(parents=True, exist_ok=True)

    async def check_and_award_certificates(self, user_id: UUID) -> list[Certificate]:
        """Check if user qualifies for new certificates and award them"""
        new_certificates = []

        # Get user and progress
        result = await self.db_session.execute(
            select(User).options(selectinload(User.progress)).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.progress:
            return []

        progress = user.progress

        # Check for track completion certificates
        for track in [ChallengeTrack.WEB, ChallengeTrack.DATA, ChallengeTrack.CLOUD]:
            track_completed = getattr(progress, f"{track.value}_track_completed", 0)

            # Award certificate for completing 80% of track (12 out of 15 challenges)
            if track_completed >= 12:
                existing = await self._get_existing_certificate(
                    user_id, CertificateType.TRACK_COMPLETION, {"track": track.value}
                )

                if not existing:
                    cert = await self._create_track_completion_certificate(
                        user, track, track_completed
                    )
                    new_certificates.append(cert)

        # Check for challenge mastery certificates
        milestones = [10, 25, 50, 100]
        for milestone in milestones:
            if progress.challenges_completed >= milestone:
                existing = await self._get_existing_certificate(
                    user_id, CertificateType.CHALLENGE_MASTERY, {"milestone": milestone}
                )

                if not existing:
                    cert = await self._create_challenge_mastery_certificate(
                        user, milestone
                    )
                    new_certificates.append(cert)

        # Check for streak milestone certificates
        streak_milestones = [7, 30, 100]
        for milestone in streak_milestones:
            if progress.longest_streak >= milestone:
                existing = await self._get_existing_certificate(
                    user_id,
                    CertificateType.STREAK_MILESTONE,
                    {"streak_days": milestone},
                )

                if not existing:
                    cert = await self._create_streak_milestone_certificate(
                        user, milestone
                    )
                    new_certificates.append(cert)

        # Commit all new certificates
        if new_certificates:
            await self.db_session.commit()

            logger.info(
                f"Awarded {len(new_certificates)} certificates to user {user_id}",
                user_id=str(user_id),
                certificates=[cert.type.value for cert in new_certificates],
            )

        return new_certificates

    async def _get_existing_certificate(
        self,
        user_id: UUID,
        cert_type: CertificateType,
        achievement_data: dict[str, Any],
    ) -> Certificate | None:
        """Check if certificate already exists for this achievement"""
        result = await self.db_session.execute(
            select(Certificate).where(
                and_(
                    Certificate.user_id == user_id,
                    Certificate.type == cert_type,
                    Certificate.achievement_data.contains(achievement_data),
                )
            )
        )
        return result.scalar_one_or_none()

    async def _create_track_completion_certificate(
        self, user: User, track: ChallengeTrack, completed_count: int
    ) -> Certificate:
        """Create track completion certificate"""
        track_name = track.value.title()

        cert = Certificate(
            user_id=user.id,
            type=CertificateType.TRACK_COMPLETION,
            title=f"{track_name} Track Master",
            description=f"Successfully completed {completed_count} challenges in the {track_name} track",
            achievement_data={
                "track": track.value,
                "challenges_completed": completed_count,
                "completion_date": datetime.utcnow().isoformat(),
            },
        )

        # Generate unique identifiers
        cert.certificate_number = cert.generate_certificate_number()
        cert.verification_code = cert.generate_verification_code()

        self.db_session.add(cert)
        await self.db_session.flush()  # Get the ID

        return cert

    async def _create_challenge_mastery_certificate(
        self, user: User, milestone: int
    ) -> Certificate:
        """Create challenge mastery certificate"""
        cert = Certificate(
            user_id=user.id,
            type=CertificateType.CHALLENGE_MASTERY,
            title=f"Challenge Master - {milestone} Challenges",
            description=f"Successfully completed {milestone} coding challenges across all tracks",
            achievement_data={
                "milestone": milestone,
                "completion_date": datetime.utcnow().isoformat(),
            },
        )

        cert.certificate_number = cert.generate_certificate_number()
        cert.verification_code = cert.generate_verification_code()

        self.db_session.add(cert)
        await self.db_session.flush()

        return cert

    async def _create_streak_milestone_certificate(
        self, user: User, streak_days: int
    ) -> Certificate:
        """Create streak milestone certificate"""
        cert = Certificate(
            user_id=user.id,
            type=CertificateType.STREAK_MILESTONE,
            title=f"{streak_days}-Day Consistency Champion",
            description=f"Maintained a {streak_days}-day learning streak",
            achievement_data={
                "streak_days": streak_days,
                "achievement_date": datetime.utcnow().isoformat(),
            },
        )

        cert.certificate_number = cert.generate_certificate_number()
        cert.verification_code = cert.generate_verification_code()

        self.db_session.add(cert)
        await self.db_session.flush()

        return cert

    async def generate_certificate_pdf(self, certificate_id: UUID) -> str | None:
        """Generate PDF for a certificate"""
        # Get certificate with user data
        result = await self.db_session.execute(
            select(Certificate)
            .options(selectinload(Certificate.user))
            .where(Certificate.id == certificate_id)
        )
        certificate = result.scalar_one_or_none()

        if not certificate:
            return None

        # Generate PDF
        pdf_filename = f"certificate_{certificate.id}.pdf"
        pdf_path = self.certificates_dir / pdf_filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Build PDF content
        story = self._build_certificate_content(certificate)

        try:
            doc.build(story)

            # Update certificate record
            certificate.status = CertificateStatus.GENERATED
            certificate.generated_at = datetime.utcnow()
            certificate.pdf_path = str(pdf_path)
            certificate.pdf_size_bytes = os.path.getsize(pdf_path)

            await self.db_session.commit()

            logger.info(
                "Generated certificate PDF",
                certificate_id=str(certificate_id),
                pdf_path=str(pdf_path),
                size_bytes=certificate.pdf_size_bytes,
            )

            return str(pdf_path)

        except Exception as e:
            logger.error(f"Failed to generate certificate PDF: {e}")
            return None

    def _build_certificate_content(self, certificate: Certificate) -> list:
        """Build certificate content for PDF generation"""
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CertificateTitle",
            parent=styles["Heading1"],
            fontSize=28,
            textColor=navy,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName="Helvetica-Bold",
        )

        header_style = ParagraphStyle(
            "CertificateHeader",
            parent=styles["Normal"],
            fontSize=18,
            textColor=gold,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName="Helvetica-Bold",
        )

        recipient_style = ParagraphStyle(
            "RecipientName",
            parent=styles["Normal"],
            fontSize=24,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName="Helvetica-Bold",
        )

        body_style = ParagraphStyle(
            "CertificateBody",
            parent=styles["Normal"],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20,
        )

        story = []

        # Header
        story.append(Paragraph("CERTIFICATE OF ACHIEVEMENT", header_style))
        story.append(Spacer(1, 20))

        # Title
        story.append(Paragraph(certificate.title, title_style))
        story.append(Spacer(1, 30))

        # "This is to certify that"
        story.append(Paragraph("This is to certify that", body_style))
        story.append(Spacer(1, 10))

        # Recipient name
        story.append(Paragraph(certificate.user.name, recipient_style))
        story.append(Spacer(1, 20))

        # Achievement description
        story.append(Paragraph(certificate.description, body_style))
        story.append(Spacer(1, 30))

        # Date and certificate details
        date_issued = certificate.earned_at.strftime("%B %d, %Y")
        story.append(Paragraph(f"Issued on {date_issued}", body_style))
        story.append(Spacer(1, 40))

        # Signature section
        signature_data = [
            ["", ""],
            ["_" * 30, "_" * 30],
            ["Weak-to-Strong Platform", "Certificate ID"],
            ["Digital Signature", certificate.certificate_number],
        ]

        signature_table = Table(signature_data, colWidths=[3 * inch, 3 * inch])
        signature_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("FONTNAME", (0, 2), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )

        story.append(signature_table)
        story.append(Spacer(1, 30))

        # QR code for verification
        qr_img = self._generate_qr_code(certificate)
        if qr_img:
            story.append(qr_img)
            story.append(Spacer(1, 10))
            story.append(
                Paragraph(
                    f"Verify at: {certificate.verification_url}",
                    ParagraphStyle(
                        "QRText",
                        parent=styles["Normal"],
                        fontSize=8,
                        alignment=TA_CENTER,
                    ),
                )
            )

        return story

    def _generate_qr_code(self, certificate: Certificate) -> Image | None:
        """Generate QR code for certificate verification"""
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=4)
            qr.add_data(certificate.verification_url)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Convert to ReportLab Image
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            return Image(ImageReader(img_buffer), width=1 * inch, height=1 * inch)

        except Exception as e:
            logger.warning(f"Failed to generate QR code: {e}")
            return None

    async def get_user_certificates(self, user_id: UUID) -> list[Certificate]:
        """Get all certificates for a user"""
        result = await self.db_session.execute(
            select(Certificate)
            .where(Certificate.user_id == user_id)
            .order_by(Certificate.earned_at.desc())
        )
        return list(result.scalars().all())

    async def verify_certificate(self, verification_code: str) -> Certificate | None:
        """Verify a certificate by its verification code"""
        result = await self.db_session.execute(
            select(Certificate)
            .options(selectinload(Certificate.user))
            .where(Certificate.verification_code == verification_code)
        )
        return result.scalar_one_or_none()

    async def get_certificate_by_id(self, certificate_id: UUID) -> Certificate | None:
        """Get certificate by ID"""
        result = await self.db_session.execute(
            select(Certificate)
            .options(selectinload(Certificate.user))
            .where(Certificate.id == certificate_id)
        )
        return result.scalar_one_or_none()
