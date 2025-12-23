"""
Unit tests for database models
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import select

from app.models.user import User, UserTier
from app.models.token_usage import TokenUsage
from app.models.challenge import Challenge, Submission, UserProgress


class TestUserModel:
    """Test cases for User model"""

    @pytest.mark.unit
    async def test_user_creation(self, test_db_session):
        """Test creating a user with all fields"""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
            tier=UserTier.FREE,
            is_active=True,
        )

        test_db_session.add(user)
        await test_db_session.commit()

        # Verify user was created
        stmt = select(User).where(User.email == "test@example.com")
        result = await test_db_session.execute(stmt)
        saved_user = result.scalar_one()

        assert saved_user.id == user_id
        assert saved_user.email == "test@example.com"
        assert saved_user.tier == UserTier.FREE
        assert saved_user.is_active == True

    @pytest.mark.unit
    async def test_user_tier_enum(self):
        """Test UserTier enum values"""
        assert UserTier.FREE.value == "free"
        assert UserTier.PRO.value == "pro"
        assert UserTier.TEAM.value == "team"
        assert UserTier.ENTERPRISE.value == "enterprise"

    @pytest.mark.unit
    async def test_user_oauth_fields(self, test_db_session):
        """Test user creation with OAuth fields"""
        user = User(
            id=uuid4(),
            email="oauth@example.com",
            hashed_password="hashed_password",
            full_name="OAuth User",
            github_id="github123",
            google_id="google456",
        )

        test_db_session.add(user)
        await test_db_session.commit()

        stmt = select(User).where(User.email == "oauth@example.com")
        result = await test_db_session.execute(stmt)
        saved_user = result.scalar_one()

        assert saved_user.github_id == "github123"
        assert saved_user.google_id == "google456"

    @pytest.mark.unit
    async def test_user_subscription_fields(self, test_db_session):
        """Test user subscription-related fields"""
        user = User(
            id=uuid4(),
            email="subscription@example.com",
            hashed_password="hashed_password",
            full_name="Subscription User",
            subscription_tier="pro",
            subscription_status="active",
            stripe_customer_id="cus_test123",
        )

        test_db_session.add(user)
        await test_db_session.commit()

        stmt = select(User).where(User.email == "subscription@example.com")
        result = await test_db_session.execute(stmt)
        saved_user = result.scalar_one()

        assert saved_user.subscription_tier == "pro"
        assert saved_user.subscription_status == "active"
        assert saved_user.stripe_customer_id == "cus_test123"


class TestTokenUsageModel:
    """Test cases for TokenUsage model"""

    @pytest.fixture
    async def test_user(self, test_db_session):
        """Create a test user"""
        user = User(
            id=uuid4(),
            email="tokenuser@example.com",
            hashed_password="hashed_password",
            full_name="Token User",
        )
        test_db_session.add(user)
        await test_db_session.commit()
        return user

    @pytest.mark.unit
    async def test_token_usage_creation(self, test_db_session, test_user):
        """Test creating token usage record"""
        token_usage = TokenUsage(
            user_id=str(test_user.id),
            date=datetime.utcnow().date(),
            model="claude-haiku",
            tokens_used=1500,
        )

        test_db_session.add(token_usage)
        await test_db_session.commit()

        # Verify token usage was created
        stmt = select(TokenUsage).where(TokenUsage.user_id == str(test_user.id))
        result = await test_db_session.execute(stmt)
        saved_usage = result.scalar_one()

        assert saved_usage.user_id == str(test_user.id)
        assert saved_usage.model == "claude-haiku"
        assert saved_usage.tokens_used == 1500

    @pytest.mark.unit
    async def test_add_usage_new_record(self, test_db_session, test_user):
        """Test adding usage creates new record"""
        await TokenUsage.add_usage(
            db_session=test_db_session,
            user_id=str(test_user.id),
            model="claude-sonnet",
            tokens=2000,
        )

        stmt = select(TokenUsage).where(
            TokenUsage.user_id == str(test_user.id), TokenUsage.model == "claude-sonnet"
        )
        result = await test_db_session.execute(stmt)
        usage = result.scalar_one()

        assert usage.tokens_used == 2000

    @pytest.mark.unit
    async def test_add_usage_update_existing(self, test_db_session, test_user):
        """Test adding usage updates existing record"""
        # Create initial record
        await TokenUsage.add_usage(
            db_session=test_db_session,
            user_id=str(test_user.id),
            model="local",
            tokens=1000,
        )

        # Add more usage to same user/date/model
        await TokenUsage.add_usage(
            db_session=test_db_session,
            user_id=str(test_user.id),
            model="local",
            tokens=500,
        )

        stmt = select(TokenUsage).where(
            TokenUsage.user_id == str(test_user.id), TokenUsage.model == "local"
        )
        result = await test_db_session.execute(stmt)
        usage = result.scalar_one()

        assert usage.tokens_used == 1500  # 1000 + 500


class TestChallengeModels:
    """Test cases for Challenge-related models"""

    @pytest.fixture
    async def test_user(self, test_db_session):
        """Create a test user"""
        user = User(
            id=uuid4(),
            email="challengeuser@example.com",
            hashed_password="hashed_password",
            full_name="Challenge User",
        )
        test_db_session.add(user)
        await test_db_session.commit()
        return user

    @pytest.fixture
    async def test_challenge(self, test_db_session):
        """Create a test challenge"""
        challenge = Challenge(
            id="test-challenge-1",
            title="Test Challenge",
            description="A test challenge",
            track="web",
            difficulty="beginner",
            points=100,
            requirements=["Requirement 1", "Requirement 2"],
            starter_code="// Start here",
            test_config={"type": "jest", "file": "test.js"},
        )
        test_db_session.add(challenge)
        await test_db_session.commit()
        return challenge

    @pytest.mark.unit
    async def test_challenge_creation(self, test_challenge):
        """Test challenge model creation"""
        assert test_challenge.id == "test-challenge-1"
        assert test_challenge.title == "Test Challenge"
        assert test_challenge.track == "web"
        assert test_challenge.difficulty == "beginner"
        assert test_challenge.points == 100
        assert isinstance(test_challenge.requirements, list)

    @pytest.mark.unit
    async def test_submission_creation(
        self, test_db_session, test_user, test_challenge
    ):
        """Test submission model creation"""
        submission = Submission(
            id=uuid4(),
            challenge_id=test_challenge.id,
            user_id=str(test_user.id),
            code="console.log('solution');",
            language="javascript",
            status="submitted",
            score=85.5,
            passed=True,
        )

        test_db_session.add(submission)
        await test_db_session.commit()

        # Verify submission was created
        stmt = select(Submission).where(
            Submission.challenge_id == test_challenge.id,
            Submission.user_id == str(test_user.id),
        )
        result = await test_db_session.execute(stmt)
        saved_submission = result.scalar_one()

        assert saved_submission.code == "console.log('solution');"
        assert saved_submission.language == "javascript"
        assert saved_submission.score == 85.5
        assert saved_submission.passed == True

    @pytest.mark.unit
    async def test_user_progress_creation(self, test_db_session, test_user):
        """Test user progress model creation"""
        progress = UserProgress(
            user_id=str(test_user.id),
            challenges_completed=5,
            ai_tier_unlocked="haiku",
            total_points=500,
            current_streak=3,
            longest_streak=7,
        )

        test_db_session.add(progress)
        await test_db_session.commit()

        # Verify progress was created
        stmt = select(UserProgress).where(UserProgress.user_id == str(test_user.id))
        result = await test_db_session.execute(stmt)
        saved_progress = result.scalar_one()

        assert saved_progress.challenges_completed == 5
        assert saved_progress.ai_tier_unlocked == "haiku"
        assert saved_progress.total_points == 500
        assert saved_progress.current_streak == 3

    @pytest.mark.unit
    async def test_submission_relationships(
        self, test_db_session, test_user, test_challenge
    ):
        """Test submission model relationships"""
        submission = Submission(
            id=uuid4(),
            challenge_id=test_challenge.id,
            user_id=str(test_user.id),
            code="test code",
            language="javascript",
            status="completed",
        )

        test_db_session.add(submission)
        await test_db_session.commit()
        await test_db_session.refresh(submission)

        # Test relationships (if properly configured)
        assert submission.challenge_id == test_challenge.id
        assert submission.user_id == str(test_user.id)
