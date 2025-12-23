"""
Phase 6 Integration Tests
Tests the complete progress and gamification flow
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.services.progress_service import ProgressService
from app.services.certificate_service import CertificateService
from app.models.user import User, UserTier
from app.models.challenge import (
    Challenge,
    Submission,
    UserProgress,
    ChallengeTrack,
    ChallengeDifficulty,
    SubmissionStatus,
)
from app.models.certificate import Certificate, CertificateType


@pytest.mark.asyncio
async def test_complete_progress_and_gamification_flow(test_db_session):
    """Test the complete flow from user registration to certificate earning"""

    # 1. Create a new user
    user = User(email="test@example.com", name="Test User", tier=UserTier.FREE)
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    # 2. Create progress service
    progress_service = ProgressService(test_db_session)

    # 3. Create some web track challenges
    challenges = []
    for i in range(15):
        challenge = Challenge(
            slug=f"web-{i+1:03d}",
            title=f"Web Challenge {i+1}",
            description=f"Description for challenge {i+1}",
            track="web",
            difficulty=(
                "beginner" if i < 5 else "intermediate" if i < 10 else "advanced"
            ),
            order_index=i + 1,
            points=100,
        )
        challenges.append(challenge)
        test_db_session.add(challenge)

    await test_db_session.commit()

    # 4. Simulate user completing challenges over time
    completed_submissions = []

    for i, challenge in enumerate(challenges[:12]):  # Complete 12 out of 15 challenges
        submission = Submission(
            user_id=user.id,
            challenge_id=challenge.id,
            code=f"<h1>Solution {i+1}</h1>",
            status=SubmissionStatus.COMPLETED,
            passed=True,
            score=85 + (i % 15),  # Varying scores
            points_earned=challenge.points,
            completed_at=datetime.utcnow(),
        )
        completed_submissions.append(submission)
        test_db_session.add(submission)

        # Update progress for each submission
        await progress_service.update_progress_for_submission(submission)

    await test_db_session.commit()

    # 5. Verify progress tracking
    user_progress = await progress_service.get_user_progress(user.id)

    assert user_progress is not None
    assert user_progress.challenges_completed == 12
    assert user_progress.web_track_completed == 12
    assert user_progress.total_points == 1200  # 12 * 100 points
    assert (
        user_progress.ai_tier_unlocked == "haiku"
    )  # Should unlock haiku at 10+ challenges

    # 6. Get track progress
    web_track_data = await progress_service.get_track_progress(
        user.id, ChallengeTrack.WEB
    )

    assert web_track_data["track"] == "web"
    assert web_track_data["completed"] == 12
    assert web_track_data["total"] == 15
    assert web_track_data["percentage"] == 80.0  # 12/15 = 80%

    # 7. Check achievements
    achievements = await progress_service.get_achievements(user.id)

    # Should have earned some achievements
    earned_achievements = [a for a in achievements if a["earned"]]
    assert len(earned_achievements) > 0

    # Should have "first_steps" achievement
    first_steps = next(
        (a for a in earned_achievements if a["id"] == "first_steps"), None
    )
    assert first_steps is not None

    # 8. Check certificates - should have been awarded automatically
    cert_service = CertificateService(test_db_session)
    certificates = await cert_service.get_user_certificates(user.id)

    # Should have web track completion certificate (12/15 = 80% completion)
    track_cert = next(
        (c for c in certificates if c.type == CertificateType.TRACK_COMPLETION), None
    )
    assert track_cert is not None
    assert track_cert.achievement_data["track"] == "web"
    assert track_cert.achievement_data["challenges_completed"] == 12

    # Should have challenge mastery certificate (10 challenges milestone)
    mastery_cert = next(
        (
            c
            for c in certificates
            if c.type == CertificateType.CHALLENGE_MASTERY
            and c.achievement_data.get("milestone") == 10
        ),
        None,
    )
    assert mastery_cert is not None

    # 9. Test certificate verification
    track_cert_verification = await cert_service.verify_certificate(
        track_cert.verification_code
    )
    assert track_cert_verification is not None
    assert track_cert_verification.id == track_cert.id
    assert track_cert_verification.user.name == "Test User"

    # 10. Simulate building a streak
    updated_progress = await progress_service.get_user_progress(user.id)
    updated_progress.current_streak = 7
    updated_progress.longest_streak = 7
    await test_db_session.commit()

    # Check for streak milestone certificates
    new_certs = await cert_service.check_and_award_certificates(user.id)
    streak_certs = [c for c in new_certs if c.type == CertificateType.STREAK_MILESTONE]
    assert len(streak_certs) >= 1  # Should get 7-day streak certificate

    # 11. Test leaderboard
    leaderboard = await progress_service.get_leaderboard()
    assert len(leaderboard) >= 1
    assert leaderboard[0]["user_id"] == str(user.id)
    assert leaderboard[0]["points"] == 1200
    assert leaderboard[0]["rank"] == 1

    # 12. Test model tier progression
    model_tier = await progress_service.get_model_tier_for_challenge(
        user.id, challenges[0]
    )
    assert model_tier == "local"  # Beginner challenge always uses local

    model_tier_advanced = await progress_service.get_model_tier_for_challenge(
        user.id, challenges[-1]
    )
    assert (
        model_tier_advanced == "haiku"
    )  # Should use haiku for advanced with 10+ challenges

    # 13. Upgrade user to pro and complete more challenges
    user.tier = UserTier.PRO

    # Complete more challenges to reach 25 total
    for challenge in challenges[12:]:
        submission = Submission(
            user_id=user.id,
            challenge_id=challenge.id,
            code=f"<h1>Advanced Solution</h1>",
            status=SubmissionStatus.COMPLETED,
            passed=True,
            score=90,
            points_earned=challenge.points,
            completed_at=datetime.utcnow(),
        )
        test_db_session.add(submission)
        await progress_service.update_progress_for_submission(submission)

    # Add more challenges to reach 25 total
    for i in range(10):  # Add 10 more challenges
        challenge = Challenge(
            slug=f"web-{16+i:03d}",
            title=f"Web Challenge {16+i}",
            description=f"Description for challenge {16+i}",
            track="web",
            difficulty="advanced",
            order_index=16 + i,
            points=100,
        )
        test_db_session.add(challenge)
        await test_db_session.commit()
        await test_db_session.refresh(challenge)

        submission = Submission(
            user_id=user.id,
            challenge_id=challenge.id,
            code=f"<h1>Expert Solution {16+i}</h1>",
            status=SubmissionStatus.COMPLETED,
            passed=True,
            score=95,
            points_earned=challenge.points,
            completed_at=datetime.utcnow(),
        )
        test_db_session.add(submission)
        await progress_service.update_progress_for_submission(submission)

    await test_db_session.commit()

    # 14. Verify AI tier upgrade to Sonnet
    final_progress = await progress_service.get_user_progress(user.id)
    assert final_progress.challenges_completed >= 25
    assert final_progress.ai_tier_unlocked == "sonnet"

    # Test sonnet access for advanced challenge
    sonnet_tier = await progress_service.get_model_tier_for_challenge(
        user.id, challenges[-1]
    )
    assert sonnet_tier == "sonnet"

    # 15. Check final certificate count
    all_certificates = await cert_service.get_user_certificates(user.id)

    # Should have multiple certificates by now
    assert (
        len(all_certificates) >= 3
    )  # Track completion, 10 challenges, 25 challenges, streak

    # Should have 25-challenge mastery certificate
    mastery_25_cert = next(
        (
            c
            for c in all_certificates
            if c.type == CertificateType.CHALLENGE_MASTERY
            and c.achievement_data.get("milestone") == 25
        ),
        None,
    )
    assert mastery_25_cert is not None

    print(f"✅ Complete flow test passed!")
    print(f"   - User completed {final_progress.challenges_completed} challenges")
    print(f"   - Earned {final_progress.total_points} points")
    print(f"   - AI tier: {final_progress.ai_tier_unlocked}")
    print(f"   - Certificates earned: {len(all_certificates)}")
    print(f"   - Current streak: {final_progress.current_streak}")


@pytest.mark.asyncio
async def test_streak_calculation_and_certificates(test_db_session, sample_user):
    """Test streak calculation and streak milestone certificates"""

    progress_service = ProgressService(test_db_session)
    cert_service = CertificateService(test_db_session)

    # Create progress with various streak lengths
    progress = await progress_service.create_user_progress(sample_user.id)

    # Test different streak milestones
    streak_milestones = [7, 14, 30, 50, 100]

    for milestone in streak_milestones:
        progress.current_streak = milestone
        progress.longest_streak = max(progress.longest_streak, milestone)
        await test_db_session.commit()

        # Check for new certificates
        new_certs = await cert_service.check_and_award_certificates(sample_user.id)

        # Should award certificate for this milestone
        streak_cert = next(
            (
                c
                for c in new_certs
                if c.type == CertificateType.STREAK_MILESTONE
                and c.achievement_data.get("streak_days") == milestone
            ),
            None,
        )

        if milestone in [7, 30, 100]:  # Only these milestones award certificates
            assert streak_cert is not None
            assert f"{milestone}-Day" in streak_cert.title

    # Test streak info
    streak_info = await progress_service.get_user_streaks(sample_user.id)
    assert streak_info["current_streak"] == 100
    assert streak_info["longest_streak"] == 100


@pytest.mark.asyncio
async def test_certificate_pdf_generation_simulation(test_db_session, sample_user):
    """Test certificate PDF generation workflow (without actual PDF creation)"""

    cert_service = CertificateService(test_db_session)

    # Create a certificate
    certificate = Certificate(
        user_id=sample_user.id,
        type=CertificateType.TRACK_COMPLETION,
        title="Web Track Master",
        description="Successfully completed 12 challenges in the Web track",
        certificate_number="WTS-2024-01-TEST01",
        verification_code="VER-TEST01-AB",
        achievement_data={
            "track": "web",
            "challenges_completed": 12,
            "completion_date": datetime.utcnow().isoformat(),
        },
    )
    test_db_session.add(certificate)
    await test_db_session.commit()
    await test_db_session.refresh(certificate)

    # Test certificate properties
    assert certificate.display_achievement == "Web Track Completion"
    assert certificate.verification_url.endswith(
        f"/certificates/verify/{certificate.verification_code}"
    )
    assert not certificate.is_generated  # Not generated yet

    # Test certificate number generation
    new_cert_number = certificate.generate_certificate_number()
    assert new_cert_number.startswith("WTS-")

    # Test verification code generation
    new_verification_code = certificate.generate_verification_code()
    assert new_verification_code.startswith("VER-")

    print(f"✅ Certificate PDF workflow test passed!")
    print(f"   - Certificate ID: {certificate.id}")
    print(f"   - Certificate Number: {certificate.certificate_number}")
    print(f"   - Verification Code: {certificate.verification_code}")
    print(f"   - Verification URL: {certificate.verification_url}")
