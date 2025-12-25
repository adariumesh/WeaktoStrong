"""
Progress tracking service
Handles challenge completion, progress updates, and achievement unlocking
"""

from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.challenge import Challenge, ChallengeTrack, Submission, UserProgress
from ..models.user import User


class ProgressService:
    """Service for tracking and managing user progress"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_or_create_user_progress(self, user_id: str) -> UserProgress:
        """Get or create UserProgress record for a user"""
        # Try to get existing progress
        query = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await self.db.execute(query)
        progress = result.scalar_one_or_none()

        if not progress:
            # Create new progress record
            progress = UserProgress(user_id=user_id)
            self.db.add(progress)
            await self.db.commit()
            await self.db.refresh(progress)

        return progress

    async def update_progress_for_submission(self, submission: Submission):
        """Update user progress based on a submission"""
        progress = await self.get_or_create_user_progress(str(submission.user_id))

        # Update progress calculations
        await self._recalculate_progress(progress, submission.user_id)

        # Update AI tier based on new progress
        await self._update_ai_tier(progress)

        # Update activity timestamp
        progress.last_activity = datetime.utcnow()

        await self.db.commit()
        return progress

    async def _recalculate_progress(self, progress: UserProgress, user_id: str):
        """Recalculate all progress metrics for a user"""

        # Count total completed challenges (unique challenges with successful submissions)
        completed_query = select(
            func.count(func.distinct(Submission.challenge_id))
        ).where(and_(Submission.user_id == user_id, Submission.passed == True))
        completed_result = await self.db.execute(completed_query)
        progress.challenges_completed = completed_result.scalar() or 0

        # Count total attempted challenges (unique challenges with any submission)
        attempted_query = select(
            func.count(func.distinct(Submission.challenge_id))
        ).where(Submission.user_id == user_id)
        attempted_result = await self.db.execute(attempted_query)
        progress.challenges_attempted = attempted_result.scalar() or 0

        # Calculate total points earned
        points_query = select(func.sum(Submission.points_earned)).where(
            and_(Submission.user_id == user_id, Submission.passed == True)
        )
        points_result = await self.db.execute(points_query)
        progress.total_points = points_result.scalar() or 0

        # Calculate track-specific progress
        await self._update_track_progress(progress, user_id)

        # Update AI request count
        ai_requests_query = select(func.sum(Submission.ai_requests)).where(
            Submission.user_id == user_id
        )
        ai_requests_result = await self.db.execute(ai_requests_query)
        progress.ai_requests_total = ai_requests_result.scalar() or 0

    async def _update_track_progress(self, progress: UserProgress, user_id: str):
        """Update track-specific completion counts"""

        # Get track completion counts
        track_query = (
            select(
                Challenge.track,
                func.count(func.distinct(Submission.challenge_id)).label("completed"),
            )
            .select_from(Submission.__table__.join(Challenge.__table__))
            .where(and_(Submission.user_id == user_id, Submission.passed == True))
            .group_by(Challenge.track)
        )

        track_result = await self.db.execute(track_query)
        track_counts = {row.track: row.completed for row in track_result}

        progress.web_track_completed = track_counts.get(ChallengeTrack.WEB.value, 0)
        progress.data_track_completed = track_counts.get(ChallengeTrack.DATA.value, 0)
        progress.cloud_track_completed = track_counts.get(ChallengeTrack.CLOUD.value, 0)

    async def _update_ai_tier(self, progress: UserProgress):
        """Update AI tier based on completed challenges"""
        if progress.challenges_completed >= 25:
            progress.ai_tier_unlocked = "sonnet"
        elif progress.challenges_completed >= 10:
            progress.ai_tier_unlocked = "haiku"
        else:
            progress.ai_tier_unlocked = "local"

    async def get_progress_summary(self, user_id: str) -> dict:
        """Get comprehensive progress summary for a user"""
        progress = await self.get_or_create_user_progress(user_id)

        # Get total challenges available per track
        track_totals = {}
        for track in ChallengeTrack:
            count_query = select(func.count()).where(
                and_(Challenge.track == track.value, Challenge.is_active == True)
            )
            result = await self.db.execute(count_query)
            track_totals[track.value] = result.scalar() or 0

        return {
            "user_id": user_id,
            "overall": {
                "challenges_completed": progress.challenges_completed,
                "challenges_attempted": progress.challenges_attempted,
                "total_points": progress.total_points,
                "completion_rate": progress.completion_rate,
                "ai_tier": progress.ai_tier_unlocked,
            },
            "tracks": {
                "web": {
                    "completed": progress.web_track_completed,
                    "total": track_totals.get("web", 0),
                    "percentage": (
                        progress.web_track_completed / track_totals.get("web", 1)
                    )
                    * 100,
                },
                "data": {
                    "completed": progress.data_track_completed,
                    "total": track_totals.get("data", 0),
                    "percentage": (
                        progress.data_track_completed / track_totals.get("data", 1)
                    )
                    * 100,
                },
                "cloud": {
                    "completed": progress.cloud_track_completed,
                    "total": track_totals.get("cloud", 0),
                    "percentage": (
                        progress.cloud_track_completed / track_totals.get("cloud", 1)
                    )
                    * 100,
                },
            },
            "engagement": {
                "current_streak": progress.current_streak,
                "longest_streak": progress.longest_streak,
                "last_activity": (
                    progress.last_activity.isoformat()
                    if progress.last_activity
                    else None
                ),
                "ai_requests_total": progress.ai_requests_total,
            },
        }

    async def get_leaderboard(
        self, track: ChallengeTrack | None = None, limit: int = 10
    ) -> list[dict]:
        """Get leaderboard of top users by points or track completion"""

        if track:
            # Track-specific leaderboard
            if track == ChallengeTrack.WEB:
                order_field = UserProgress.web_track_completed
            elif track == ChallengeTrack.DATA:
                order_field = UserProgress.data_track_completed
            else:
                order_field = UserProgress.cloud_track_completed
        else:
            # Overall leaderboard by total points
            order_field = UserProgress.total_points

        query = (
            select(UserProgress, User.name, User.avatar_url)
            .join(User, UserProgress.user_id == User.id)
            .order_by(order_field.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)

        leaderboard = []
        for row in result:
            progress, name, avatar_url = row
            leaderboard.append(
                {
                    "rank": len(leaderboard) + 1,
                    "user_name": name,
                    "avatar_url": avatar_url,
                    "total_points": progress.total_points,
                    "challenges_completed": progress.challenges_completed,
                    "track_completed": (
                        getattr(progress, f"{track.value}_track_completed")
                        if track
                        else None
                    ),
                }
            )

        return leaderboard

    async def get_recent_completions(self, user_id: str, limit: int = 10) -> list[dict]:
        """Get user's recent challenge completions"""

        query = (
            select(Submission, Challenge.title, Challenge.track, Challenge.difficulty)
            .join(Challenge, Submission.challenge_id == Challenge.id)
            .where(and_(Submission.user_id == user_id, Submission.passed == True))
            .order_by(Submission.completed_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)

        completions = []
        for row in result:
            submission, title, track, difficulty = row
            completions.append(
                {
                    "challenge_title": title,
                    "track": track,
                    "difficulty": difficulty,
                    "points_earned": submission.points_earned,
                    "score": submission.score,
                    "completed_at": (
                        submission.completed_at.isoformat()
                        if submission.completed_at
                        else None
                    ),
                    "completion_time": submission.completion_time,
                }
            )

        return completions


async def get_progress_service(db: AsyncSession) -> ProgressService:
    """Factory function to create a ProgressService instance"""
    return ProgressService(db)
