"""
AI Model Router - Routes requests to appropriate AI model based on user tier
Implements model tier progression: Local → Haiku → Sonnet
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.ai_schemas import AIRequest, ModelTier
from .claude_client import claude_service
from .coaching_system import ai_coaching_system
from .local_llm import local_llm_service
from .prompt_validator import validate_prompt

logger = logging.getLogger(__name__)


class ModelTierRouter:
    """Routes AI requests to appropriate model based on user progress and tier"""

    def __init__(self):
        self.tier_requirements = {
            ModelTier.LOCAL: {"min_challenges_completed": 0},
            ModelTier.HAIKU: {"min_challenges_completed": 10},
            ModelTier.SONNET: {"min_challenges_completed": 25, "requires_pro": True},
        }

    async def get_allowed_tier(
        self,
        user,
        challenge_difficulty: str = "beginner",
        db_session: AsyncSession = None,
    ) -> ModelTier:
        """Determine the highest model tier the user can access"""

        # Count user's completed challenges
        challenges_completed = await self._count_completed_challenges(
            str(user.id), db_session
        )

        # Check tier progression
        if (
            challenges_completed
            >= self.tier_requirements[ModelTier.SONNET]["min_challenges_completed"]
            and user.subscription_tier == "pro"
        ):
            return ModelTier.SONNET
        elif (
            challenges_completed
            >= self.tier_requirements[ModelTier.HAIKU]["min_challenges_completed"]
        ):
            return ModelTier.HAIKU
        else:
            return ModelTier.LOCAL

    async def route_request(
        self, request: AIRequest, user, db_session: AsyncSession | None = None
    ) -> AsyncGenerator[str, None]:
        """Route AI request to appropriate model and stream response"""

        # Validate prompt for anti-blind-prompting
        validation = validate_prompt(request.prompt)
        if not validation.is_valid and request.enforce_validation:
            yield f"❌ {validation.feedback}"
            return

        # Use coaching system for enhanced prompts when context available
        enhanced_request = request
        if (
            db_session
            and request.challenge_context
            and hasattr(request, "challenge_id")
            and request.challenge_id
        ):
            try:
                coaching_result = (
                    await ai_coaching_system.generate_comprehensive_coaching(
                        challenge_id=request.challenge_id,
                        user_id=str(user.id),
                        user_prompt=request.prompt,
                        db_session=db_session,
                    )
                )
                # Use enhanced coaching prompt
                enhanced_request.prompt = coaching_result["enhanced_prompt"]
                logger.info(
                    f"Using AI coaching for user {user.id}, coaching strategy: {coaching_result['coaching_metadata'].get('coaching_strategy', {}).get('tone', 'standard')}"
                )
            except Exception as e:
                logger.warning(f"AI coaching failed, using standard prompt: {e}")

        # Determine allowed tier
        allowed_tier = await self.get_allowed_tier(
            user,
            (
                enhanced_request.challenge_context.get("difficulty", "beginner")
                if enhanced_request.challenge_context
                else "beginner"
            ),
        )

        # Use requested tier or fall back to allowed tier
        effective_tier = min(
            enhanced_request.preferred_tier, allowed_tier, key=lambda x: x.value
        )

        # Add tier info to response
        tier_info = f"🤖 **{effective_tier.name.title()} AI** | "
        if effective_tier != request.preferred_tier:
            tier_info += f"*Upgraded to {effective_tier.name.title()} tier* | "

        yield tier_info

        # Route to appropriate service
        try:
            if effective_tier == ModelTier.LOCAL:
                async for chunk in local_llm_service.stream_response(
                    prompt=enhanced_request.prompt,
                    system_prompt=self._build_system_prompt(enhanced_request),
                    temperature=enhanced_request.temperature,
                    max_tokens=enhanced_request.max_tokens,
                ):
                    yield chunk

            elif effective_tier == ModelTier.HAIKU:
                async for chunk in claude_service.stream_response(
                    prompt=enhanced_request.prompt,
                    system_prompt=self._build_system_prompt(enhanced_request),
                    model="claude-3-haiku-20240307",
                    temperature=enhanced_request.temperature,
                    max_tokens=enhanced_request.max_tokens,
                ):
                    yield chunk

            elif effective_tier == ModelTier.SONNET:
                async for chunk in claude_service.stream_response(
                    prompt=enhanced_request.prompt,
                    system_prompt=self._build_system_prompt(enhanced_request),
                    model="claude-3-5-sonnet-20241022",
                    temperature=enhanced_request.temperature,
                    max_tokens=enhanced_request.max_tokens,
                ):
                    yield chunk

        except Exception as e:
            logger.error(f"AI routing failed for tier {effective_tier}: {e}")
            yield "\n\n❌ AI service temporarily unavailable. Please try again."

    def _build_system_prompt(self, request: AIRequest) -> str:
        """Build context-aware system prompt with live challenge and code context"""
        base_prompt = """You are an AI assistant for the Weak-to-Strong platform, helping users learn web development through guided practice.

Key guidelines:
- Provide helpful guidance without giving complete solutions
- Encourage users to think through problems step by step
- Reference the specific challenge requirements when relevant
- Focus on teaching concepts rather than just fixing code
- Be encouraging and supportive of the learning process"""

        if request.challenge_context:
            challenge_info = f"""

Current Challenge Context:
- Challenge: {request.challenge_context.get('title', 'Unknown')}
- Track: {request.challenge_context.get('track', 'General')}
- Difficulty: {request.challenge_context.get('difficulty', 'beginner')}
- Points: {request.challenge_context.get('points', 'N/A')}"""

            # Add requirements if available
            if request.challenge_context.get("requirements"):
                requirements = request.challenge_context["requirements"]
                if isinstance(requirements, list):
                    challenge_info += f"""
- Requirements: {', '.join(requirements)}"""
                else:
                    challenge_info += f"""
- Requirements: {requirements}"""

            # Add challenge description for better context
            if request.challenge_context.get("description"):
                desc = request.challenge_context["description"][:200]
                challenge_info += f"""
- Description: {desc}{'...' if len(request.challenge_context['description']) > 200 else ''}"""

            # Add current user code with syntax highlighting awareness
            if request.challenge_context.get("user_code"):
                user_code = request.challenge_context["user_code"]
                language = request.challenge_context.get("language", "javascript")
                challenge_info += f"""

User's Current Code ({language}):
```{language}
{user_code}
```"""

            # Add test results if available
            if request.challenge_context.get("last_test_results"):
                test_results = request.challenge_context["last_test_results"]
                if isinstance(test_results, dict):
                    passed = test_results.get("passed", 0)
                    total = test_results.get("total", 0)
                    challenge_info += f"""
- Last Test Results: {passed}/{total} tests passed"""

                    if test_results.get("failures"):
                        challenge_info += f"""
- Recent Failures: {test_results['failures'][:100]}{'...' if len(str(test_results['failures'])) > 100 else ''}"""

            # Add submission history context
            if request.challenge_context.get("attempts"):
                attempts = request.challenge_context["attempts"]
                challenge_info += f"""
- Previous Attempts: {attempts}"""

            # Add code progression insights
            if request.challenge_context.get("code_progression"):
                progression = request.challenge_context["code_progression"]
                challenge_info += f"""

Code Progression Analysis:
- Total Submissions: {progression.get('total_submissions', 0)}"""

                if progression.get("patterns_identified"):
                    patterns = ", ".join(
                        progression["patterns_identified"][:2]
                    )  # Limit to avoid prompt bloat
                    challenge_info += f"""
- Coding Patterns: {patterns}"""

                if progression.get("improvement_areas"):
                    improvements = ", ".join(progression["improvement_areas"][:2])
                    challenge_info += f"""
- Focus Areas: {improvements}"""

            # Add learning insights
            if request.challenge_context.get("learning_insights"):
                insights = request.challenge_context["learning_insights"]
                challenge_info += f"""

Learning Context:
- Difficulty Assessment: {insights.get('difficulty_assessment', 'appropriate')}"""

                if insights.get("skill_gaps"):
                    gaps = ", ".join(insights["skill_gaps"][:2])
                    challenge_info += f"""
- Skill Development: {gaps}"""

                if insights.get("learning_path_status"):
                    path = insights["learning_path_status"]
                    suggested_focus = path.get("suggested_focus", "")
                    if suggested_focus:
                        challenge_info += f"""
- Learning Focus: {suggested_focus}"""

            base_prompt += challenge_info

        return base_prompt

    async def _count_completed_challenges(
        self, user_id: str, db_session: AsyncSession = None
    ) -> int:
        """Count number of challenges the user has completed successfully"""
        # Import here to avoid circular imports
        from ...models.challenge import UserProgress

        if db_session is None:
            # If no database session provided, return 0 for now
            return 0

        try:
            # Try to get user progress record
            from sqlalchemy import select

            query = select(UserProgress.challenges_completed).where(
                UserProgress.user_id == user_id
            )
            result = await db_session.execute(query)
            progress_record = result.scalar()
            return progress_record or 0
        except Exception:
            # Fallback to counting submissions directly if progress table not available
            try:
                from ...models.challenge import Submission

                # Count unique challenges where user has a successful submission
                query = (
                    select(Submission.challenge_id)
                    .where(Submission.user_id == user_id, Submission.passed == True)
                    .distinct()
                )
                result = await db_session.execute(query)
                completed_challenges = result.fetchall()
                return len(completed_challenges)
            except Exception:
                # Ultimate fallback - return 0
                return 0

    async def get_tier_progress(
        self, user, current_tier: ModelTier, db_session: AsyncSession = None
    ) -> dict[str, Any]:
        """Get progress towards next tier unlock"""
        challenges_completed = await self._count_completed_challenges(
            str(user.id), db_session
        )

        if current_tier == ModelTier.LOCAL:
            next_tier = ModelTier.HAIKU
            required = self.tier_requirements[next_tier]["min_challenges_completed"]
            return {
                "current_tier": current_tier.name.lower(),
                "next_tier": next_tier.name.lower(),
                "progress": challenges_completed,
                "required": required,
                "percentage": min(100, (challenges_completed / required) * 100),
            }
        elif current_tier == ModelTier.HAIKU:
            next_tier = ModelTier.SONNET
            required = self.tier_requirements[next_tier]["min_challenges_completed"]
            is_pro = user.subscription_tier == "pro"
            return {
                "current_tier": current_tier.name.lower(),
                "next_tier": next_tier.name.lower(),
                "progress": challenges_completed,
                "required": required,
                "percentage": min(100, (challenges_completed / required) * 100),
                "requires_pro": not is_pro,
            }
        else:  # SONNET
            return {
                "current_tier": current_tier.name.lower(),
                "next_tier": None,
                "progress": challenges_completed,
                "required": 0,
                "percentage": 100,
            }


# Global router instance
model_router = ModelTierRouter()
