"""
Progress API endpoints for tracking user achievements and streaks
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.challenge import ChallengeTrack
from app.models.user import User
from app.schemas.progress import (
    AchievementResponse,
    LeaderboardResponse,
    StreakResponse,
    TrackProgressResponse,
    UserProgressResponse,
)
from app.services.progress_service import ProgressService

router = APIRouter(tags=["progress"])


@router.get("/", response_model=UserProgressResponse)
async def get_user_progress(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user's overall progress"""
    service = ProgressService(db)
    progress = await service.get_user_progress(current_user.id)

    if not progress:
        progress = await service.create_user_progress(current_user.id)

    return UserProgressResponse(
        user_id=current_user.id,
        total_points=progress.total_points,
        challenges_completed=progress.challenges_completed,
        challenges_attempted=progress.challenges_attempted,
        completion_rate=progress.completion_rate,
        current_streak=progress.current_streak,
        longest_streak=progress.longest_streak,
        ai_tier_unlocked=progress.ai_tier_unlocked,
        web_track_completed=progress.web_track_completed,
        data_track_completed=progress.data_track_completed,
        cloud_track_completed=progress.cloud_track_completed,
        last_activity=progress.last_activity,
        achievements_count=len(progress.achievements or []),
        badges_count=len(progress.badges or []),
    )


@router.get("/tracks/{track}", response_model=TrackProgressResponse)
async def get_track_progress(
    track: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed progress for a specific track"""
    # Validate track
    try:
        challenge_track = ChallengeTrack(track)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid track: {track}. Must be one of: web, data, cloud",
        )

    service = ProgressService(db)
    track_data = await service.get_track_progress(current_user.id, challenge_track)

    return TrackProgressResponse(**track_data)


@router.get("/streaks", response_model=StreakResponse)
async def get_user_streaks(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get user's streak information"""
    service = ProgressService(db)
    streak_data = await service.get_user_streaks(current_user.id)

    return StreakResponse(**streak_data)


@router.get("/leaderboard", response_model=list[LeaderboardResponse])
async def get_leaderboard(
    track: str | None = Query(
        None, description="Track to filter by (web, data, cloud)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Number of top users to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get leaderboard data"""
    challenge_track = None
    if track:
        try:
            challenge_track = ChallengeTrack(track)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid track: {track}. Must be one of: web, data, cloud",
            )

    service = ProgressService(db)
    leaderboard_data = await service.get_leaderboard(challenge_track, limit)

    return [LeaderboardResponse(**entry) for entry in leaderboard_data]


@router.get("/achievements", response_model=list[AchievementResponse])
async def get_user_achievements(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get user's achievements and progress toward unlocking new ones"""
    service = ProgressService(db)
    achievements_data = await service.get_achievements(current_user.id)

    return [AchievementResponse(**achievement) for achievement in achievements_data]


@router.get("/stats", response_model=dict[str, Any])
async def get_user_stats(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get comprehensive user statistics"""
    service = ProgressService(db)

    # Get progress
    progress = await service.get_user_progress(current_user.id)
    if not progress:
        progress = await service.create_user_progress(current_user.id)

    # Get streak info
    streaks = await service.get_user_streaks(current_user.id)

    # Get achievements
    achievements = await service.get_achievements(current_user.id)
    earned_achievements = [a for a in achievements if a["earned"]]

    # Get track progress
    tracks_progress = {}
    for track in ["web", "data", "cloud"]:
        track_data = await service.get_track_progress(
            current_user.id, ChallengeTrack(track)
        )
        tracks_progress[track] = track_data

    return {
        "overview": {
            "total_points": progress.total_points,
            "challenges_completed": progress.challenges_completed,
            "challenges_attempted": progress.challenges_attempted,
            "completion_rate": progress.completion_rate,
            "ai_tier": progress.ai_tier_unlocked,
        },
        "streaks": streaks,
        "achievements": {
            "earned": len(earned_achievements),
            "total": len(achievements),
            "recent": earned_achievements[-3:] if earned_achievements else [],
        },
        "tracks": tracks_progress,
        "activity": {
            "last_activity": progress.last_activity,
            "ai_requests_total": progress.ai_requests_total,
        },
    }


@router.post("/refresh")
async def refresh_progress(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Manually refresh/recalculate user progress"""
    service = ProgressService(db)

    # Force recalculation by getting all user submissions
    from sqlalchemy import and_, select

    from app.models.challenge import Submission, SubmissionStatus

    result = await db.execute(
        select(Submission)
        .where(
            and_(
                Submission.user_id == current_user.id,
                Submission.status == SubmissionStatus.COMPLETED,
            )
        )
        .order_by(Submission.completed_at)
    )

    submissions = result.scalars().all()

    # Get or create progress
    progress = await service.get_user_progress(current_user.id)
    if not progress:
        progress = await service.create_user_progress(current_user.id)

    # Update progress for each submission
    for submission in submissions:
        await service.update_progress_for_submission(submission)

    await db.commit()

    # Return updated progress
    updated_progress = await service.get_user_progress(current_user.id)

    return {
        "message": "Progress refreshed successfully",
        "progress": {
            "total_points": updated_progress.total_points,
            "challenges_completed": updated_progress.challenges_completed,
            "current_streak": updated_progress.current_streak,
            "ai_tier": updated_progress.ai_tier_unlocked,
        },
    }
