"""
Tests for the progress service functionality
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.progress_service import ProgressService
from app.models.challenge import (
    Challenge,
    Submission,
    UserProgress,
    ChallengeTrack,
    ChallengeDifficulty,
    SubmissionStatus,
)
from app.models.user import User, UserTier


@pytest.mark.asyncio
async def test_create_user_progress(test_db_session):
    """Test creating initial user progress"""
    service = ProgressService(test_db_session)
    user_id = uuid4()

    progress = await service.create_user_progress(user_id)

    assert progress.user_id == user_id
    assert progress.total_points == 0
    assert progress.challenges_completed == 0
    assert progress.current_streak == 0
    assert progress.ai_tier_unlocked == "local"


@pytest.mark.asyncio
async def test_get_user_progress(test_db_session):
    """Test getting user progress"""
    service = ProgressService(test_db_session)
    user_id = uuid4()

    # First call should return None
    progress = await service.get_user_progress(user_id)
    assert progress is None

    # Create progress
    created_progress = await service.create_user_progress(user_id)

    # Second call should return the progress
    progress = await service.get_user_progress(user_id)
    assert progress is not None
    assert progress.user_id == user_id


@pytest.mark.asyncio
async def test_streak_calculation(test_db_session, sample_user):
    """Test streak calculation logic"""
    service = ProgressService(test_db_session)

    # Create a completed challenge
    challenge = Challenge(
        slug="test-challenge",
        title="Test Challenge",
        description="Test description",
        track="web",
        difficulty="beginner",
        order_index=1,
        points=100,
    )
    test_db_session.add(challenge)
    await test_db_session.commit()
    await test_db_session.refresh(challenge)

    # Create a successful submission
    submission = Submission(
        user_id=sample_user.id,
        challenge_id=challenge.id,
        code="<h1>Hello World</h1>",
        status=SubmissionStatus.COMPLETED,
        passed=True,
        score=100,
        points_earned=100,
        completed_at=datetime.utcnow(),
    )
    test_db_session.add(submission)
    await test_db_session.commit()
    await test_db_session.refresh(submission)

    # Update progress for submission
    progress = await service.update_progress_for_submission(submission)

    assert progress.challenges_completed == 1
    assert progress.current_streak >= 0  # Should be at least 0
    assert progress.total_points == 100


@pytest.mark.asyncio
async def test_ai_tier_unlock(test_db_session, sample_user):
    """Test AI tier unlocking logic"""
    service = ProgressService(test_db_session)

    # Create progress
    progress = await service.create_user_progress(sample_user.id)

    # Simulate completing 10 challenges
    progress.challenges_completed = 10
    await service._update_ai_tier(progress)

    assert progress.ai_tier_unlocked == "haiku"

    # Update user to pro tier and complete 25 challenges
    sample_user.tier = UserTier.PRO
    progress.challenges_completed = 25
    await service._update_ai_tier(progress)

    assert progress.ai_tier_unlocked == "sonnet"


@pytest.mark.asyncio
async def test_track_progress(test_db_session, sample_user):
    """Test track-specific progress tracking"""
    service = ProgressService(test_db_session)

    # Create web challenges
    for i in range(3):
        challenge = Challenge(
            slug=f"web-challenge-{i+1}",
            title=f"Web Challenge {i+1}",
            description="Test description",
            track="web",
            difficulty="beginner",
            order_index=i + 1,
            points=100,
        )
        test_db_session.add(challenge)

    await test_db_session.commit()

    # Get track progress (should show empty progress)
    track_data = await service.get_track_progress(sample_user.id, ChallengeTrack.WEB)

    assert track_data["track"] == "web"
    assert track_data["completed"] == 0
    assert track_data["total"] == 3
    assert track_data["percentage"] == 0.0
    assert len(track_data["challenges"]) == 3


@pytest.mark.asyncio
async def test_achievements(test_db_session, sample_user):
    """Test achievements system"""
    service = ProgressService(test_db_session)

    # Get achievements for new user
    achievements = await service.get_achievements(sample_user.id)

    # Should have achievements defined
    assert len(achievements) > 0

    # None should be earned initially
    earned = [a for a in achievements if a["earned"]]
    assert len(earned) == 0


@pytest.mark.asyncio
async def test_model_tier_for_challenge(test_db_session, sample_user):
    """Test model tier determination for challenges"""
    service = ProgressService(test_db_session)

    # Create challenges of different difficulties
    beginner_challenge = Challenge(
        slug="beginner-test",
        title="Beginner Test",
        description="Test",
        track="web",
        difficulty="beginner",
        order_index=1,
        points=100,
    )

    advanced_challenge = Challenge(
        slug="advanced-test",
        title="Advanced Test",
        description="Test",
        track="web",
        difficulty="advanced",
        order_index=2,
        points=100,
    )

    test_db_session.add(beginner_challenge)
    test_db_session.add(advanced_challenge)
    await test_db_session.commit()

    # Test model tier for beginner (should always be local)
    tier = await service.get_model_tier_for_challenge(
        sample_user.id, beginner_challenge
    )
    assert tier == "local"

    # Test model tier for advanced (should be local for new user)
    tier = await service.get_model_tier_for_challenge(
        sample_user.id, advanced_challenge
    )
    assert tier == "local"


@pytest.mark.asyncio
async def test_leaderboard(test_db_session, sample_user):
    """Test leaderboard functionality"""
    service = ProgressService(test_db_session)

    # Create progress for the user
    progress = await service.create_user_progress(sample_user.id)
    progress.total_points = 500
    progress.challenges_completed = 5
    await test_db_session.commit()

    # Get leaderboard
    leaderboard = await service.get_leaderboard()

    assert len(leaderboard) >= 1
    assert leaderboard[0]["user_id"] == str(sample_user.id)
    assert leaderboard[0]["points"] == 500
    assert leaderboard[0]["rank"] == 1
