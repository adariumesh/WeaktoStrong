"""
Challenge Context Service for AI Integration
Provides live context about user's current challenge, code, and progress
"""

import logging
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ChallengeContextService:
    """Service to fetch and provide live challenge context for AI"""

    async def get_challenge_context(
        self,
        challenge_id: str,
        user_id: str,
        db_session: AsyncSession,
        include_code: bool = True,
        include_test_results: bool = True,
        include_diff_analysis: bool = True,
        include_learning_path: bool = True,
    ) -> dict[str, Any]:
        """
        Fetch comprehensive challenge context for AI

        Args:
            challenge_id: ID of the current challenge
            user_id: ID of the user
            db_session: Database session
            include_code: Whether to include user's current code
            include_test_results: Whether to include test results

        Returns:
            Dictionary with challenge context information
        """
        try:
            from ...models.challenge import Challenge, Submission, TestResult

            context = {"challenge_id": challenge_id, "user_id": user_id}

            # Fetch challenge details
            challenge_query = select(Challenge).where(Challenge.id == challenge_id)
            challenge_result = await db_session.execute(challenge_query)
            challenge = challenge_result.scalar()

            if challenge:
                context.update(
                    {
                        "title": challenge.title,
                        "description": challenge.description,
                        "track": challenge.track,
                        "difficulty": challenge.difficulty,
                        "points": challenge.points,
                        "language": challenge.language or "javascript",
                        "requirements": challenge.requirements or [],
                    }
                )

            if include_code:
                # Get user's latest submission code
                latest_submission_query = (
                    select(Submission)
                    .where(
                        Submission.challenge_id == challenge_id,
                        Submission.user_id == user_id,
                    )
                    .order_by(desc(Submission.submitted_at))
                    .limit(1)
                )
                submission_result = await db_session.execute(latest_submission_query)
                latest_submission = submission_result.scalar()

                if latest_submission:
                    context.update(
                        {
                            "user_code": latest_submission.code,
                            "submission_id": str(latest_submission.id),
                            "last_submitted": latest_submission.submitted_at.isoformat(),
                            "attempts": await self._count_user_attempts(
                                challenge_id, user_id, db_session
                            ),
                        }
                    )

            if include_test_results and latest_submission:
                # Get latest test results
                test_results_query = (
                    select(TestResult)
                    .where(TestResult.submission_id == latest_submission.id)
                    .order_by(desc(TestResult.created_at))
                    .limit(1)
                )
                test_result = await db_session.execute(test_results_query)
                latest_test = test_result.scalar()

                if latest_test:
                    context["last_test_results"] = {
                        "passed": latest_test.tests_passed or 0,
                        "total": latest_test.total_tests or 0,
                        "score": latest_test.score,
                        "execution_time": latest_test.execution_time,
                        "memory_used": latest_test.memory_used,
                        "output": (
                            latest_test.output[:500] if latest_test.output else None
                        ),  # Truncate long output
                        "errors": (
                            latest_test.error_output[:500]
                            if latest_test.error_output
                            else None
                        ),
                        "failures": (
                            latest_test.failures[:500] if latest_test.failures else None
                        ),
                        "success": latest_test.passed,
                        "created_at": latest_test.created_at.isoformat(),
                    }

            # Add code diff analysis if requested
            if include_diff_analysis and latest_submission:
                diff_analysis = await self._analyze_code_progression(
                    challenge_id, user_id, db_session
                )
                if diff_analysis:
                    context["code_progression"] = diff_analysis

            # Add learning path insights if requested
            if include_learning_path:
                learning_insights = await self._generate_learning_insights(
                    challenge_id, user_id, challenge, db_session
                )
                if learning_insights:
                    context["learning_insights"] = learning_insights

            return context

        except Exception as e:
            logger.error(
                f"Failed to fetch challenge context for challenge {challenge_id}, user {user_id}: {e}"
            )
            return {
                "challenge_id": challenge_id,
                "user_id": user_id,
                "error": "Failed to load challenge context",
            }

    async def _count_user_attempts(
        self, challenge_id: str, user_id: str, db_session: AsyncSession
    ) -> int:
        """Count total submission attempts for this challenge"""
        try:
            from sqlalchemy import func

            from ...models.challenge import Submission

            count_query = select(func.count(Submission.id)).where(
                Submission.challenge_id == challenge_id, Submission.user_id == user_id
            )
            result = await db_session.execute(count_query)
            return result.scalar() or 0
        except Exception:
            return 0

    async def get_user_progress_summary(
        self, user_id: str, db_session: AsyncSession
    ) -> dict[str, Any]:
        """Get user's overall progress summary for AI context"""
        try:
            from sqlalchemy import func

            from ...models.challenge import Submission, UserProgress

            # Get user progress record
            progress_query = select(UserProgress).where(UserProgress.user_id == user_id)
            progress_result = await db_session.execute(progress_query)
            progress = progress_result.scalar()

            context = {}

            if progress:
                context.update(
                    {
                        "challenges_completed": progress.challenges_completed,
                        "total_points": progress.total_points,
                        "current_streak": progress.current_streak,
                        "ai_tier_unlocked": progress.ai_tier_unlocked,
                    }
                )

            # Get recent activity
            recent_submissions_query = (
                select(Submission.challenge_id, func.max(Submission.submitted_at))
                .where(Submission.user_id == user_id)
                .group_by(Submission.challenge_id)
                .order_by(func.max(Submission.submitted_at).desc())
                .limit(5)
            )
            recent_result = await db_session.execute(recent_submissions_query)
            recent_challenges = recent_result.fetchall()

            context["recent_challenges"] = [
                {"challenge_id": str(row[0]), "last_attempt": row[1].isoformat()}
                for row in recent_challenges
            ]

            return context

        except Exception as e:
            logger.error(
                f"Failed to fetch user progress summary for user {user_id}: {e}"
            )
            return {}

    async def _analyze_code_progression(
        self, challenge_id: str, user_id: str, db_session: AsyncSession
    ) -> dict[str, Any] | None:
        """Analyze user's code progression and patterns"""
        try:
            from sqlalchemy import asc

            from ...models.challenge import Submission

            # Get all submissions for this challenge, ordered by time
            submissions_query = (
                select(Submission)
                .where(
                    Submission.challenge_id == challenge_id,
                    Submission.user_id == user_id,
                )
                .order_by(asc(Submission.submitted_at))
            )
            submissions_result = await db_session.execute(submissions_query)
            submissions = submissions_result.scalars().all()

            if len(submissions) < 2:
                return None

            analysis = {
                "total_submissions": len(submissions),
                "progression_summary": [],
                "patterns_identified": [],
                "improvement_areas": [],
            }

            # Analyze progression patterns
            prev_code_length = 0
            successful_submissions = 0

            for i, submission in enumerate(submissions):
                code_length = len(submission.code) if submission.code else 0
                length_change = code_length - prev_code_length

                if submission.passed:
                    successful_submissions += 1

                submission_analysis = {
                    "attempt": i + 1,
                    "passed": submission.passed,
                    "code_length": code_length,
                    "length_change": length_change,
                    "submitted_at": submission.submitted_at.isoformat(),
                }

                # Identify patterns
                if i > 0:
                    if length_change > 100:
                        submission_analysis["pattern"] = "significant_expansion"
                        analysis["patterns_identified"].append(
                            "User tends to add substantial code between attempts"
                        )
                    elif length_change < -50:
                        submission_analysis["pattern"] = "code_reduction"
                        analysis["patterns_identified"].append(
                            "User simplified approach in recent attempts"
                        )
                    elif abs(length_change) < 20:
                        submission_analysis["pattern"] = "fine_tuning"
                        analysis["patterns_identified"].append(
                            "User making small refinements"
                        )

                analysis["progression_summary"].append(submission_analysis)
                prev_code_length = code_length

            # Generate improvement suggestions
            if successful_submissions == 0:
                analysis["improvement_areas"].append(
                    "Focus on getting basic functionality working first"
                )
            elif successful_submissions < len(submissions) * 0.3:
                analysis["improvement_areas"].append(
                    "Consider breaking down the problem into smaller steps"
                )

            if len(submissions) > 5:
                analysis["improvement_areas"].append(
                    "Take time to plan before coding to reduce trial-and-error"
                )

            # Remove duplicates from patterns
            analysis["patterns_identified"] = list(set(analysis["patterns_identified"]))

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze code progression: {e}")
            return None

    async def _generate_learning_insights(
        self, challenge_id: str, user_id: str, challenge, db_session: AsyncSession
    ) -> dict[str, Any] | None:
        """Generate contextual learning insights and suggestions"""
        try:
            from sqlalchemy import and_, func

            from ...models.challenge import Challenge, Submission, UserProgress

            insights = {
                "difficulty_assessment": "appropriate",
                "recommended_resources": [],
                "skill_gaps": [],
                "next_challenges": [],
                "learning_path_status": {},
            }

            if not challenge:
                return insights

            # Analyze difficulty appropriateness based on user progress
            user_progress_query = select(UserProgress).where(
                UserProgress.user_id == user_id
            )
            progress_result = await db_session.execute(user_progress_query)
            user_progress = progress_result.scalar()

            if user_progress:
                total_completed = user_progress.challenges_completed
                current_difficulty = challenge.difficulty

                # Assess if challenge difficulty matches user level
                if current_difficulty == "beginner" and total_completed > 15:
                    insights["difficulty_assessment"] = "too_easy"
                    insights["recommended_resources"].append(
                        "Consider intermediate challenges for better growth"
                    )
                elif current_difficulty == "advanced" and total_completed < 10:
                    insights["difficulty_assessment"] = "too_hard"
                    insights["recommended_resources"].append(
                        "Complete more intermediate challenges first"
                    )
                elif current_difficulty == "expert" and total_completed < 25:
                    insights["difficulty_assessment"] = "too_hard"
                    insights["recommended_resources"].append(
                        "Build stronger foundation with advanced challenges"
                    )

            # Identify skill gaps based on challenge track and user history
            track = challenge.track
            if track:
                # Get user's performance in this track
                track_submissions_query = (
                    select(
                        func.count(Submission.id),
                        func.avg(
                            Submission.passed.cast(
                                (
                                    db_session.bind.dialect.name == "postgresql"
                                    and "INTEGER"
                                )
                                or "REAL"
                            )
                        ),
                    )
                    .select_from(Submission)
                    .join(Challenge)
                    .where(
                        and_(Submission.user_id == user_id, Challenge.track == track)
                    )
                )
                track_result = await db_session.execute(track_submissions_query)
                track_stats = track_result.first()

                if (
                    track_stats and track_stats[0] > 3
                ):  # At least 3 attempts in this track
                    success_rate = track_stats[1] or 0
                    if success_rate < 0.4:  # Less than 40% success rate
                        insights["skill_gaps"].append(
                            f"Struggling with {track} fundamentals"
                        )
                        insights["recommended_resources"].append(
                            f"Review {track} basics and documentation"
                        )

            # Find similar challenges for practice
            similar_challenges_query = (
                select(Challenge.id, Challenge.title, Challenge.difficulty)
                .where(
                    and_(
                        Challenge.track == challenge.track,
                        Challenge.difficulty == challenge.difficulty,
                        Challenge.id != challenge_id,
                    )
                )
                .limit(3)
            )
            similar_result = await db_session.execute(similar_challenges_query)
            similar_challenges = similar_result.fetchall()

            insights["next_challenges"] = [
                {"id": str(ch[0]), "title": ch[1], "difficulty": ch[2]}
                for ch in similar_challenges
            ]

            # Learning path status
            insights["learning_path_status"] = {
                "current_track": track or "mixed",
                "track_completion": f"Working on {challenge.difficulty} level",
                "suggested_focus": self._get_suggested_focus(challenge, user_progress),
            }

            return insights

        except Exception as e:
            logger.error(f"Failed to generate learning insights: {e}")
            return None

    def _get_suggested_focus(self, challenge, user_progress) -> str:
        """Get learning focus suggestion based on challenge and progress"""
        if not challenge:
            return "Complete more challenges to assess learning path"

        track = challenge.track or "general"
        difficulty = challenge.difficulty

        if not user_progress:
            return f"Master {track} {difficulty} concepts"

        completed = user_progress.challenges_completed

        if completed < 5:
            return "Focus on building coding fundamentals"
        elif completed < 15:
            return f"Strengthen {track} problem-solving skills"
        elif completed < 30:
            return f"Advanced {track} patterns and optimization"
        else:
            return "Explore complex system design challenges"


# Global service instance
challenge_context_service = ChallengeContextService()
