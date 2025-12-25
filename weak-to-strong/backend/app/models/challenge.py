"""
SQLAlchemy models for challenges and submissions system
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class Track(Base):
    """Track model - learning tracks like Web, Data, Cloud"""

    __tablename__ = "tracks"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )

    # Relationships
    challenges = relationship("Challenge", back_populates="track")


class ChallengeTrack(str, Enum):
    """Available challenge tracks"""

    WEB = "web"
    DATA = "data"
    CLOUD = "cloud"


class ChallengeDifficulty(str, Enum):
    """Challenge difficulty levels"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SubmissionStatus(str, Enum):
    """Submission status states"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Challenge(Base):
    """Challenge model - individual coding challenges"""

    __tablename__ = "challenges"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    # Challenge metadata
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # Classification
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=False)
    difficulty = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    order_index = Column(Integer, nullable=False)  # Position in track

    # Requirements and testing
    requirements = Column(JSON, nullable=True)  # List of requirement strings
    constraints = Column(JSON, nullable=True)  # List of constraint strings
    test_config = Column(JSON, nullable=True)  # Test configuration
    validation_rules = Column(JSON, nullable=True)  # Data analysis validation rules

    # Points and progress
    points = Column(Integer, default=100, nullable=False)
    estimated_time_minutes = Column(Integer, nullable=True)  # Minutes

    # Model and red team settings
    model_tier = Column(
        String(20), nullable=False, default="local"
    )  # local, haiku, sonnet
    is_red_team = Column(Boolean, default=False, nullable=True)

    # Content
    hints = Column(JSON, nullable=True)  # List of hint strings

    # Status
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )

    # Relationships
    track = relationship("Track", back_populates="challenges")
    submissions = relationship(
        "Submission", back_populates="challenge", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "track IN ('web', 'data', 'cloud')", name="valid_challenge_track"
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="valid_challenge_difficulty",
        ),
    )

    def __repr__(self):
        return f"<Challenge(id={self.id}, slug='{self.slug}', track='{self.track}')>"

    @property
    def completion_rate(self) -> float:
        """Calculate percentage of users who completed this challenge"""
        if not self.submissions:
            return 0.0

        completed = len(
            [
                s
                for s in self.submissions
                if s.status == SubmissionStatus.COMPLETED and s.passed
            ]
        )
        total = len(self.submissions)
        return (completed / total) * 100 if total > 0 else 0.0

    @property
    def average_time(self) -> int | None:
        """Calculate average completion time in minutes"""
        completed_submissions = [
            s
            for s in self.submissions
            if s.status == SubmissionStatus.COMPLETED and s.passed and s.completion_time
        ]

        if not completed_submissions:
            return None

        times = [s.completion_time for s in completed_submissions]
        return sum(times) // len(times)

    def get_next_challenge(self):
        """Get the next challenge in the same track"""
        return (
            Challenge.query.filter(
                Challenge.track == self.track,
                Challenge.order_index > self.order_index,
                Challenge.is_active == True,
            )
            .order_by(Challenge.order_index)
            .first()
        )

    def get_previous_challenge(self):
        """Get the previous challenge in the same track"""
        return (
            Challenge.query.filter(
                Challenge.track == self.track,
                Challenge.order_index < self.order_index,
                Challenge.is_active == True,
            )
            .order_by(Challenge.order_index.desc())
            .first()
        )


class Submission(Base):
    """User submission for a challenge"""

    __tablename__ = "submissions"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    # References
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    challenge_id = Column(
        UUID(as_uuid=True),
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Submission data
    code = Column(Text, nullable=False)  # User's submitted code
    status = Column(String(20), nullable=False, default=SubmissionStatus.PENDING.value)

    # Results
    passed = Column(Boolean, default=False, nullable=False)
    score = Column(Integer, default=0, nullable=False)  # 0-100
    points_earned = Column(Integer, default=0, nullable=False)

    # Timing
    completion_time = Column(Integer, nullable=True)  # Minutes to complete
    submitted_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Test results and feedback
    test_results = Column(JSON, nullable=True)  # Detailed test output
    error_message = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)  # AI-generated feedback

    # AI interaction tracking
    ai_requests = Column(
        Integer, default=0, nullable=False
    )  # Number of AI help requests
    hints_used = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="submissions")
    challenge = relationship("Challenge", back_populates="submissions")
    test_results_detail = relationship(
        "TestResult", back_populates="submission", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'timeout')",
            name="valid_submission_status",
        ),
    )

    def __repr__(self):
        return f"<Submission(id={self.id}, user_id={self.user_id}, challenge_id={self.challenge_id}, passed={self.passed})>"

    @property
    def is_completed(self) -> bool:
        """Check if this submission is completed (regardless of pass/fail)"""
        return self.status == SubmissionStatus.COMPLETED

    @property
    def duration_minutes(self) -> int | None:
        """Get submission duration in minutes"""
        if self.completed_at:
            duration = self.completed_at - self.submitted_at
            return int(duration.total_seconds() / 60)
        return None

    def mark_completed(self, passed: bool, score: int, test_results: dict = None):
        """Mark submission as completed with results"""
        self.status = SubmissionStatus.COMPLETED
        self.passed = passed
        self.score = score
        self.completed_at = datetime.utcnow()
        self.test_results = test_results

        # Calculate points based on score and challenge difficulty
        if passed:
            base_points = self.challenge.points
            # Bonus for first attempt, penalty for multiple attempts
            attempt_count = len(
                [s for s in self.challenge.submissions if s.user_id == self.user_id]
            )
            if attempt_count == 1:
                self.points_earned = base_points
            else:
                # Reduce points by 10% for each additional attempt, minimum 50%
                penalty = min(0.5, (attempt_count - 1) * 0.1)
                self.points_earned = int(base_points * (1 - penalty))
        else:
            self.points_earned = 0


class TestResult(Base):
    """Individual test case results for a submission"""

    __tablename__ = "test_results"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    # References
    submission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Test details
    test_name = Column(String(200), nullable=False)
    test_type = Column(
        String(50), nullable=False
    )  # "html_structure", "css_styling", "js_functionality"
    description = Column(Text, nullable=True)

    # Results
    passed = Column(Boolean, nullable=False)
    score = Column(Integer, default=0, nullable=False)  # 0-100 for this test
    execution_time = Column(Integer, nullable=True)  # Milliseconds

    # Output and errors
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    actual_output = Column(Text, nullable=True)

    # Metadata
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    submission = relationship("Submission", back_populates="test_results_detail")

    def __repr__(self):
        return f"<TestResult(id={self.id}, test_name='{self.test_name}', passed={self.passed})>"


class UserProgress(Base):
    """User progress tracking across challenges and tracks"""

    __tablename__ = "user_progress"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    # References
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Overall progress
    total_points = Column(Integer, default=0, nullable=False)
    challenges_completed = Column(Integer, default=0, nullable=False)
    challenges_attempted = Column(Integer, default=0, nullable=False)

    # Track-specific progress
    web_track_completed = Column(Integer, default=0, nullable=False)
    data_track_completed = Column(Integer, default=0, nullable=False)
    cloud_track_completed = Column(Integer, default=0, nullable=False)

    # AI usage tracking
    ai_requests_total = Column(Integer, default=0, nullable=False)
    ai_tier_unlocked = Column(
        String(20), default="local", nullable=False
    )  # local, haiku, sonnet

    # Streaks and engagement
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity = Column(DateTime(timezone=True), nullable=True)

    # Achievements and milestones
    achievements = Column(JSON, nullable=True)  # List of achievement IDs
    badges = Column(JSON, nullable=True)  # List of badge IDs

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="progress")

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, total_points={self.total_points}, completed={self.challenges_completed})>"

    def update_for_submission(self, submission: Submission):
        """Update progress based on a new submission"""
        if submission.is_completed:
            self.challenges_attempted = max(
                self.challenges_attempted,
                len(
                    set(
                        s.challenge_id
                        for s in submission.user.submissions
                        if s.is_completed
                    )
                ),
            )

            if submission.passed:
                # Count unique completed challenges
                completed_challenge_ids = set(
                    s.challenge_id
                    for s in submission.user.submissions
                    if s.is_completed and s.passed
                )
                self.challenges_completed = len(completed_challenge_ids)

                # Update points
                self.total_points += submission.points_earned

                # Update track-specific progress
                if submission.challenge.track == ChallengeTrack.WEB:
                    self.web_track_completed += 1
                elif submission.challenge.track == ChallengeTrack.DATA:
                    self.data_track_completed += 1
                elif submission.challenge.track == ChallengeTrack.CLOUD:
                    self.cloud_track_completed += 1

                # Update AI tier based on progress
                self._update_ai_tier()

                # Update streaks
                self._update_streak()

        self.last_activity = datetime.utcnow()

    def _update_ai_tier(self):
        """Update AI tier based on completed challenges"""
        if self.challenges_completed >= 25:
            self.ai_tier_unlocked = "sonnet"
        elif self.challenges_completed >= 10:
            self.ai_tier_unlocked = "haiku"
        else:
            self.ai_tier_unlocked = "local"

    def _update_streak(self):
        """Update current and longest streaks"""
        # This would be implemented with more complex logic
        # For now, simple increment for completed challenges
        if hasattr(self, "_last_completion_date"):
            days_diff = (datetime.utcnow().date() - self._last_completion_date).days
            if days_diff == 1:  # Consecutive days
                self.current_streak += 1
            elif days_diff > 1:  # Streak broken
                self.current_streak = 1
        else:
            self.current_streak = 1

        self.longest_streak = max(self.longest_streak, self.current_streak)
        self._last_completion_date = datetime.utcnow().date()

    @property
    def completion_rate(self) -> float:
        """Calculate overall completion rate"""
        if self.challenges_attempted == 0:
            return 0.0
        return (self.challenges_completed / self.challenges_attempted) * 100

    def get_track_progress(self, track: ChallengeTrack) -> dict:
        """Get progress for a specific track"""
        if track == ChallengeTrack.WEB:
            completed = self.web_track_completed
        elif track == ChallengeTrack.DATA:
            completed = self.data_track_completed
        else:
            completed = self.cloud_track_completed

        # Get total challenges in track (would query Challenge table)
        total = 15  # Placeholder - would be calculated from Challenge.query

        return {
            "track": track.value,
            "completed": completed,
            "total": total,
            "percentage": (completed / total) * 100 if total > 0 else 0,
        }
