"""
Tests for certificate service functionality
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.services.certificate_service import CertificateService
from app.models.certificate import Certificate, CertificateType, CertificateStatus
from app.models.challenge import UserProgress, ChallengeTrack
from app.models.user import User, UserTier


@pytest.mark.asyncio
async def test_check_and_award_track_completion_certificates(
    test_db_session, sample_user
):
    """Test awarding certificates for track completion"""
    service = CertificateService(test_db_session)

    # Create user progress with completed web track
    progress = UserProgress(
        user_id=sample_user.id,
        web_track_completed=12,  # Completed 12 challenges (80% of 15)
        total_points=1200,
    )
    test_db_session.add(progress)
    await test_db_session.commit()

    # Check for new certificates
    certificates = await service.check_and_award_certificates(sample_user.id)

    # Should award web track completion certificate
    assert len(certificates) >= 1

    web_cert = next(
        (c for c in certificates if c.type == CertificateType.TRACK_COMPLETION), None
    )
    assert web_cert is not None
    assert "Web Track Master" in web_cert.title
    assert web_cert.achievement_data["track"] == "web"
    assert web_cert.achievement_data["challenges_completed"] == 12


@pytest.mark.asyncio
async def test_check_and_award_challenge_mastery_certificates(
    test_db_session, sample_user
):
    """Test awarding certificates for challenge mastery milestones"""
    service = CertificateService(test_db_session)

    # Create user progress with 25 completed challenges
    progress = UserProgress(
        user_id=sample_user.id, challenges_completed=25, total_points=2500
    )
    test_db_session.add(progress)
    await test_db_session.commit()

    # Check for new certificates
    certificates = await service.check_and_award_certificates(sample_user.id)

    # Should award mastery certificates for 10 and 25 challenges
    mastery_certs = [
        c for c in certificates if c.type == CertificateType.CHALLENGE_MASTERY
    ]
    assert len(mastery_certs) >= 2  # 10 and 25 milestones

    # Check for 25-challenge certificate
    cert_25 = next(
        (c for c in mastery_certs if c.achievement_data.get("milestone") == 25), None
    )
    assert cert_25 is not None
    assert "25 Challenges" in cert_25.title


@pytest.mark.asyncio
async def test_check_and_award_streak_milestone_certificates(
    test_db_session, sample_user
):
    """Test awarding certificates for streak milestones"""
    service = CertificateService(test_db_session)

    # Create user progress with long streak
    progress = UserProgress(
        user_id=sample_user.id, longest_streak=30, current_streak=30, total_points=500
    )
    test_db_session.add(progress)
    await test_db_session.commit()

    # Check for new certificates
    certificates = await service.check_and_award_certificates(sample_user.id)

    # Should award streak certificates for 7 and 30 days
    streak_certs = [
        c for c in certificates if c.type == CertificateType.STREAK_MILESTONE
    ]
    assert len(streak_certs) >= 2  # 7 and 30 day milestones

    # Check for 30-day certificate
    cert_30 = next(
        (c for c in streak_certs if c.achievement_data.get("streak_days") == 30), None
    )
    assert cert_30 is not None
    assert "30-Day" in cert_30.title


@pytest.mark.asyncio
async def test_no_duplicate_certificates(test_db_session, sample_user):
    """Test that duplicate certificates are not awarded"""
    service = CertificateService(test_db_session)

    # Create user progress
    progress = UserProgress(
        user_id=sample_user.id, web_track_completed=12, total_points=1200
    )
    test_db_session.add(progress)
    await test_db_session.commit()

    # Award certificates first time
    certificates_1 = await service.check_and_award_certificates(sample_user.id)
    assert len(certificates_1) >= 1

    # Award certificates second time - should not create duplicates
    certificates_2 = await service.check_and_award_certificates(sample_user.id)
    assert len(certificates_2) == 0  # No new certificates


@pytest.mark.asyncio
async def test_certificate_number_and_verification_code_generation(
    test_db_session, sample_user
):
    """Test certificate number and verification code generation"""
    service = CertificateService(test_db_session)

    # Create user progress
    progress = UserProgress(
        user_id=sample_user.id, challenges_completed=10, total_points=1000
    )
    test_db_session.add(progress)
    await test_db_session.commit()

    # Award certificate
    certificates = await service.check_and_award_certificates(sample_user.id)
    certificate = certificates[0]

    # Check certificate number format: WTS-YYYY-MM-XXXXXX
    assert certificate.certificate_number.startswith("WTS-")
    assert len(certificate.certificate_number.split("-")) == 3

    # Check verification code format: VER-XXXXXX-YYYY
    assert certificate.verification_code.startswith("VER-")
    assert len(certificate.verification_code.split("-")) == 3


@pytest.mark.asyncio
async def test_get_user_certificates(test_db_session, sample_user):
    """Test getting user's certificates"""
    service = CertificateService(test_db_session)

    # Create a certificate
    certificate = Certificate(
        user_id=sample_user.id,
        type=CertificateType.CHALLENGE_MASTERY,
        title="Test Certificate",
        description="Test description",
        certificate_number="WTS-2024-01-ABC123",
        verification_code="VER-ABC123-XY",
        achievement_data={"milestone": 10},
    )
    test_db_session.add(certificate)
    await test_db_session.commit()

    # Get user certificates
    certificates = await service.get_user_certificates(sample_user.id)

    assert len(certificates) == 1
    assert certificates[0].title == "Test Certificate"
    assert certificates[0].user_id == sample_user.id


@pytest.mark.asyncio
async def test_verify_certificate(test_db_session, sample_user):
    """Test certificate verification"""
    service = CertificateService(test_db_session)

    # Create a certificate
    verification_code = "VER-ABC123-XY"
    certificate = Certificate(
        user_id=sample_user.id,
        type=CertificateType.CHALLENGE_MASTERY,
        title="Test Certificate",
        description="Test description",
        certificate_number="WTS-2024-01-ABC123",
        verification_code=verification_code,
        achievement_data={"milestone": 10},
    )
    test_db_session.add(certificate)
    await test_db_session.commit()

    # Verify certificate
    verified_cert = await service.verify_certificate(verification_code)

    assert verified_cert is not None
    assert verified_cert.id == certificate.id
    assert verified_cert.user.id == sample_user.id

    # Test invalid verification code
    invalid_cert = await service.verify_certificate("INVALID-CODE")
    assert invalid_cert is None


@pytest.mark.asyncio
async def test_get_certificate_by_id(test_db_session, sample_user):
    """Test getting certificate by ID"""
    service = CertificateService(test_db_session)

    # Create a certificate
    certificate = Certificate(
        user_id=sample_user.id,
        type=CertificateType.CHALLENGE_MASTERY,
        title="Test Certificate",
        description="Test description",
        certificate_number="WTS-2024-01-ABC123",
        verification_code="VER-ABC123-XY",
        achievement_data={"milestone": 10},
    )
    test_db_session.add(certificate)
    await test_db_session.commit()

    # Get certificate by ID
    retrieved_cert = await service.get_certificate_by_id(certificate.id)

    assert retrieved_cert is not None
    assert retrieved_cert.id == certificate.id
    assert retrieved_cert.user.id == sample_user.id

    # Test invalid ID
    invalid_cert = await service.get_certificate_by_id(uuid4())
    assert invalid_cert is None
