"""
Progress service for tracking user progress, streaks, and model tier unlocks
"""

from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.challenge import (
    Challenge,
    ChallengeDifficulty,
    ChallengeTrack,
    Submission,
    SubmissionStatus,
    UserProgress,
)
from app.models.user import User, UserTier

logger = get_logger(__name__)


class ProgressService:
    """Service for managing user progress and achievements"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_progress(self, user_id: UUID) -> UserProgress | None:
        """Get user's progress record"""
        result = await self.db_session.execute(
            select(UserProgress)
            .options(selectinload(UserProgress.user))
            .where(UserProgress.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user_progress(self, user_id: UUID) -> UserProgress:
        """Create initial progress record for new user"""
        progress = UserProgress(user_id=user_id)
        self.db_session.add(progress)
        await self.db_session.commit()
        await self.db_session.refresh(progress)
        return progress

    async def update_progress_for_submission(
        self, submission: Submission
    ) -> UserProgress:
        """Update user progress when they complete a submission"""
        # Get or create progress record
        progress = await self.get_user_progress(submission.user_id)
        if not progress:
            progress = await self.create_user_progress(submission.user_id)

        # Update progress based on submission
        if submission.status == SubmissionStatus.COMPLETED:
            await self._update_attempts_count(progress, submission.user_id)

            if submission.passed:
                await self._update_completion_stats(progress, submission)
                await self._update_track_progress(progress, submission)
                await self._update_ai_tier(progress)
                await self._update_streak(progress, submission.user_id)

        progress.last_activity = datetime.utcnow()
        await self.db_session.commit()

        logger.info(
            f"Updated progress for user {submission.user_id}",
            user_id=str(submission.user_id),
            total_points=progress.total_points,
            challenges_completed=progress.challenges_completed,
            current_streak=progress.current_streak,
        )

        # Check for new certificates after progress update
        if submission.passed:
            await self._check_certificate_awards(submission.user_id)

        return progress

    async def _check_certificate_awards(self, user_id: UUID):
        """Check and award new certificates (integrated with certificate service)"""
        try:
            from app.services.certificate_service import CertificateService

            cert_service = CertificateService(self.db_session)
            await cert_service.check_and_award_certificates(user_id)
        except Exception as e:
            logger.warning(f"Failed to check certificate awards: {e}")

    async def _update_attempts_count(self, progress: UserProgress, user_id: UUID):
        """Update the count of attempted challenges"""
        result = await self.db_session.execute(
            select(func.count(func.distinct(Submission.challenge_id))).where(
                and_(
                    Submission.user_id == user_id,
                    Submission.status == SubmissionStatus.COMPLETED,
                )
            )
        )
        progress.challenges_attempted = result.scalar() or 0

    async def _update_completion_stats(
        self, progress: UserProgress, submission: Submission
    ):
        """Update completion statistics and points"""
        # Count unique completed challenges
        result = await self.db_session.execute(
            select(func.count(func.distinct(Submission.challenge_id))).where(
                and_(
                    Submission.user_id == submission.user_id,
                    Submission.status == SubmissionStatus.COMPLETED,
                    Submission.passed == True,
                )
            )
        )
        progress.challenges_completed = result.scalar() or 0

        # Update total points
        result = await self.db_session.execute(
            select(func.sum(Submission.points_earned)).where(
                and_(
                    Submission.user_id == submission.user_id, Submission.passed == True
                )
            )
        )
        progress.total_points = result.scalar() or 0

    async def _update_track_progress(
        self, progress: UserProgress, submission: Submission
    ):
        """Update track-specific completion counts"""
        challenge = submission.challenge

        # Count completed challenges in each track
        for track in [ChallengeTrack.WEB, ChallengeTrack.DATA, ChallengeTrack.CLOUD]:
            result = await self.db_session.execute(
                select(func.count(func.distinct(Submission.challenge_id)))
                .select_from(Submission)
                .join(Challenge, Submission.challenge_id == Challenge.id)
                .where(
                    and_(
                        Submission.user_id == submission.user_id,
                        Submission.passed == True,
                        Challenge.track == track.value,
                    )
                )
            )
            count = result.scalar() or 0

            if track == ChallengeTrack.WEB:
                progress.web_track_completed = count
            elif track == ChallengeTrack.DATA:
                progress.data_track_completed = count
            elif track == ChallengeTrack.CLOUD:
                progress.cloud_track_completed = count

    async def _update_ai_tier(self, progress: UserProgress):
        """Update AI tier based on user's progress and subscription"""
        # Get user to check subscription tier
        result = await self.db_session.execute(
            select(User).where(User.id == progress.user_id)
        )
        user = result.scalar_one()

        # AI tier unlock logic based on challenges completed
        if progress.challenges_completed >= 25 and user.tier in [
            UserTier.PRO,
            UserTier.TEAM,
            UserTier.ENTERPRISE,
        ]:
            progress.ai_tier_unlocked = "sonnet"
        elif progress.challenges_completed >= 10:
            progress.ai_tier_unlocked = "haiku"
        else:
            progress.ai_tier_unlocked = "local"

    async def _update_streak(self, progress: UserProgress, user_id: UUID):
        """Update daily completion streak"""
        # Get recent submissions to calculate streak
        recent_cutoff = datetime.utcnow() - timedelta(days=30)

        result = await self.db_session.execute(
            select(Submission.completed_at)
            .where(
                and_(
                    Submission.user_id == user_id,
                    Submission.passed == True,
                    Submission.completed_at >= recent_cutoff,
                )
            )
            .order_by(desc(Submission.completed_at))
        )

        completion_dates = [row[0].date() for row in result.fetchall() if row[0]]

        if not completion_dates:
            progress.current_streak = 0
            return

        # Calculate current streak
        current_streak = 1
        today = date.today()

        # Check if today or yesterday had activity
        latest_date = completion_dates[0]
        if latest_date not in [today, today - timedelta(days=1)]:
            progress.current_streak = 0
            return

        # Count consecutive days
        unique_dates = sorted(set(completion_dates), reverse=True)
        for i in range(1, len(unique_dates)):
            if unique_dates[i - 1] - unique_dates[i] == timedelta(days=1):
                current_streak += 1
            else:
                break

        progress.current_streak = current_streak
        progress.longest_streak = max(progress.longest_streak, current_streak)

    async def get_track_progress(self, user_id: UUID, track: ChallengeTrack) -> dict:
        """Get detailed progress for a specific track"""
        progress = await self.get_user_progress(user_id)
        if not progress:
            progress = await self.create_user_progress(user_id)

        # Get total challenges in track
        result = await self.db_session.execute(
            select(func.count(Challenge.id)).where(
                and_(Challenge.track == track.value, Challenge.is_active == True)
            )
        )
        total_challenges = result.scalar() or 0

        # Get completed count
        track_completed = getattr(progress, f"{track.value}_track_completed", 0)

        # Get user's submissions for this track
        result = await self.db_session.execute(
            select(Submission, Challenge)
            .join(Challenge, Submission.challenge_id == Challenge.id)
            .where(
                and_(
                    Submission.user_id == user_id,
                    Challenge.track == track.value,
                    Submission.status == SubmissionStatus.COMPLETED,
                )
            )
            .order_by(Challenge.order_index)
        )

        submissions_data = result.fetchall()

        # Calculate challenge details
        challenges_status = []
        for i in range(1, total_challenges + 1):
            submission_for_challenge = next(
                (s for s, c in submissions_data if c.order_index == i), None
            )

            if submission_for_challenge:
                status = "completed" if submission_for_challenge.passed else "attempted"
                score = submission_for_challenge.score
                points = submission_for_challenge.points_earned
            else:
                status = (
                    "locked"
                    if i > 1 and challenges_status[-1]["status"] != "completed"
                    else "available"
                )
                score = 0
                points = 0

            challenges_status.append(
                {"order": i, "status": status, "score": score, "points": points}
            )

        return {
            "track": track.value,
            "completed": track_completed,
            "total": total_challenges,
            "percentage": (
                (track_completed / total_challenges * 100)
                if total_challenges > 0
                else 0
            ),
            "challenges": challenges_status,
        }

    async def get_user_streaks(self, user_id: UUID) -> dict:
        """Get user's streak information"""
        progress = await self.get_user_progress(user_id)
        if not progress:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "streak_active": False,
                "days_until_reset": 1,
            }

        # Check if streak is active (completed challenge today or yesterday)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db_session.execute(
            select(func.count(Submission.id)).where(
                and_(
                    Submission.user_id == user_id,
                    Submission.passed == True,
                    Submission.completed_at >= cutoff,
                )
            )
        )

        recent_completions = result.scalar() or 0
        streak_active = recent_completions > 0

        # Days until streak resets (always 1 day if no recent activity)
        days_until_reset = 1 if not streak_active else 0

        return {
            "current_streak": progress.current_streak,
            "longest_streak": progress.longest_streak,
            "streak_active": streak_active,
            "days_until_reset": days_until_reset,
        }

    async def get_model_tier_for_challenge(
        self, user_id: UUID, challenge: Challenge
    ) -> str:
        """Determine which AI model tier user can access for a challenge"""
        progress = await self.get_user_progress(user_id)
        if not progress:
            return "local"

        user_result = await self.db_session.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one()

        # Model tier logic based on challenge difficulty and user progress
        if challenge.difficulty == ChallengeDifficulty.BEGINNER.value:
            return "local"

        if challenge.difficulty == ChallengeDifficulty.INTERMEDIATE.value:
            if progress.challenges_completed >= 10:
                return "haiku"
            return "local"

        if challenge.difficulty == ChallengeDifficulty.ADVANCED.value:
            if (
                user.tier in [UserTier.PRO, UserTier.TEAM, UserTier.ENTERPRISE]
                and progress.challenges_completed >= 25
            ):
                return "sonnet"
            elif progress.challenges_completed >= 10:
                return "haiku"
            return "local"

        return "local"

    async def get_leaderboard(
        self, track: ChallengeTrack | None = None, limit: int = 100
    ) -> list[dict]:
        """Get leaderboard data"""
        # Base query for user progress with user info
        query = select(UserProgress, User).join(User, UserProgress.user_id == User.id)

        if track:
            # Filter by track-specific completion
            track_field = f"{track.value}_track_completed"
            query = query.order_by(
                desc(getattr(UserProgress, track_field)),
                desc(UserProgress.total_points),
            )
        else:
            # Overall leaderboard
            query = query.order_by(
                desc(UserProgress.total_points), desc(UserProgress.challenges_completed)
            )

        query = query.limit(limit)

        result = await self.db_session.execute(query)
        leaderboard_data = result.fetchall()

        leaderboard = []
        for i, (progress, user) in enumerate(leaderboard_data, 1):
            track_completed = (
                getattr(progress, f"{track.value}_track_completed")
                if track
                else progress.challenges_completed
            )

            leaderboard.append(
                {
                    "rank": i,
                    "user_id": str(user.id),
                    "name": user.name,
                    "avatar_url": user.avatar_url,
                    "points": progress.total_points,
                    "completed": track_completed,
                    "streak": progress.current_streak,
                    "tier": user.tier.value,
                }
            )

        return leaderboard

    async def get_achievements(self, user_id: UUID) -> list[dict]:
        """Get user's achievements and available achievements"""
        progress = await self.get_user_progress(user_id)
        if not progress:
            return []

        # Define achievements
        all_achievements = [
            {
                "id": "first_steps",
                "title": "First Steps",
                "description": "Complete your first challenge",
                "requirement": lambda p: p.challenges_completed >= 1,
                "icon": "🎯",
                "points": 50,
            },
            {
                "id": "web_novice",
                "title": "Web Novice",
                "description": "Complete 5 web challenges",
                "requirement": lambda p: p.web_track_completed >= 5,
                "icon": "🌐",
                "points": 100,
            },
            {
                "id": "streak_master",
                "title": "Streak Master",
                "description": "Maintain a 7-day streak",
                "requirement": lambda p: p.current_streak >= 7,
                "icon": "🔥",
                "points": 200,
            },
            {
                "id": "ai_unlocked",
                "title": "AI Unlocked",
                "description": "Unlock Claude Haiku access",
                "requirement": lambda p: p.ai_tier_unlocked in ["haiku", "sonnet"],
                "icon": "🤖",
                "points": 150,
            },
        ]

        # Check which achievements user has earned
        earned_achievements = progress.achievements or []
        achievements_list = []

        for achievement in all_achievements:
            is_earned = achievement["id"] in earned_achievements
            is_available = achievement["requirement"](progress)

            # Auto-award new achievements
            if is_available and not is_earned:
                earned_achievements.append(achievement["id"])
                progress.achievements = earned_achievements
                await self.db_session.commit()
                is_earned = True

            achievements_list.append(
                {
                    **achievement,
                    "earned": is_earned,
                    "available": is_available,
                    "earned_at": datetime.utcnow() if is_earned else None,
                }
            )

        return achievements_list
