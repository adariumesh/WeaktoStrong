"""
Pydantic schemas for progress and gamification API responses
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class UserProgressResponse(BaseModel):
    """User's overall progress response"""

    user_id: UUID
    total_points: int = Field(description="Total points earned")
    challenges_completed: int = Field(
        description="Number of challenges completed successfully"
    )
    challenges_attempted: int = Field(description="Number of challenges attempted")
    completion_rate: float = Field(description="Completion percentage (0-100)")
    current_streak: int = Field(description="Current daily streak")
    longest_streak: int = Field(description="Longest streak achieved")
    ai_tier_unlocked: str = Field(
        description="Highest AI model tier unlocked (local/haiku/sonnet)"
    )
    web_track_completed: int = Field(description="Web track challenges completed")
    data_track_completed: int = Field(description="Data track challenges completed")
    cloud_track_completed: int = Field(description="Cloud track challenges completed")
    last_activity: datetime | None = Field(description="Last activity timestamp")
    achievements_count: int = Field(description="Number of achievements earned")
    badges_count: int = Field(description="Number of badges earned")

    class Config:
        from_attributes = True


class ChallengeStatus(BaseModel):
    """Individual challenge status in a track"""

    order: int = Field(description="Challenge position in track (1-based)")
    status: str = Field(
        description="Challenge status (locked/available/attempted/completed)"
    )
    score: int = Field(description="Score achieved (0-100)")
    points: int = Field(description="Points earned")


class TrackProgressResponse(BaseModel):
    """Progress response for a specific track"""

    track: str = Field(description="Track name (web/data/cloud)")
    completed: int = Field(description="Number of challenges completed")
    total: int = Field(description="Total challenges in track")
    percentage: float = Field(description="Completion percentage")
    challenges: list[ChallengeStatus] = Field(
        description="Individual challenge statuses"
    )

    class Config:
        from_attributes = True


class StreakResponse(BaseModel):
    """User's streak information"""

    current_streak: int = Field(description="Current consecutive days")
    longest_streak: int = Field(description="Best streak achieved")
    streak_active: bool = Field(description="Whether streak is active today")
    days_until_reset: int = Field(description="Days until streak resets")

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Leaderboard entry"""

    rank: int = Field(description="User's rank position")
    user_id: str = Field(description="User ID")
    name: str = Field(description="User display name")
    avatar_url: str | None = Field(description="User avatar URL")
    points: int = Field(description="Total points earned")
    completed: int = Field(description="Challenges completed")
    streak: int = Field(description="Current streak")
    tier: str = Field(description="Subscription tier")

    class Config:
        from_attributes = True


class AchievementResponse(BaseModel):
    """Achievement information"""

    id: str = Field(description="Achievement ID")
    title: str = Field(description="Achievement title")
    description: str = Field(description="Achievement description")
    icon: str = Field(description="Achievement icon/emoji")
    points: int = Field(description="Points awarded for achievement")
    earned: bool = Field(description="Whether user has earned this achievement")
    available: bool = Field(description="Whether achievement is available to earn")
    earned_at: datetime | None = Field(description="When achievement was earned")

    class Config:
        from_attributes = True


# Additional schemas for comprehensive stats
class CompletionStats(BaseModel):
    """Completion statistics"""

    total_completed: int
    total_attempted: int
    success_rate: float
    total_points: int


class TrackBreakdown(BaseModel):
    """Track breakdown statistics"""

    track: str
    completed: int
    total: int
    percentage: float


class AIUsageStats(BaseModel):
    """AI usage statistics"""

    current_tier: str
    total_requests: int
    tier_progress: dict[str, int]


class EngagementStats(BaseModel):
    """User engagement statistics"""

    current_streak: int
    longest_streak: int
    last_activity: datetime | None


class UserStatsResponse(BaseModel):
    """Comprehensive user statistics"""

    overview: dict[str, Any]
    streaks: StreakResponse
    achievements: dict[str, Any]
    tracks: dict[str, TrackProgressResponse]
    activity: dict[str, Any]

    class Config:
        from_attributes = True
