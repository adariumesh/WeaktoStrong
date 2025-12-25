"""
AI Coaching System - Comprehensive learning guidance
Combines context, hints, and learning insights for personalized coaching
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

# Import services dynamically to avoid circular imports

logger = logging.getLogger(__name__)


class AICoachingSystem:
    """Comprehensive AI coaching that provides personalized learning guidance"""

    def __init__(self):
        self.coaching_templates = {
            "struggling": {
                "tone": "encouraging",
                "focus": ["fundamentals", "step_by_step", "patience"],
                "avoid": ["complex_concepts", "advanced_techniques"],
            },
            "progressing": {
                "tone": "supportive",
                "focus": ["optimization", "best_practices", "patterns"],
                "avoid": ["basic_concepts"],
            },
            "advanced": {
                "tone": "challenging",
                "focus": ["architecture", "performance", "edge_cases", "scalability"],
                "avoid": ["oversimplification"],
            },
            "stuck": {
                "tone": "problem_solving",
                "focus": ["debugging", "alternative_approaches", "breaking_down"],
                "avoid": ["overwhelming_details"],
            },
        }

    async def generate_comprehensive_coaching(
        self,
        challenge_id: str,
        user_id: str,
        user_prompt: str,
        db_session: AsyncSession,
    ) -> dict[str, Any]:
        """Generate comprehensive coaching response with context, hints, and guidance"""

        try:
            # Import services here to avoid circular imports
            from .challenge_context import challenge_context_service
            from .hint_generator import hint_generator

            # Get comprehensive context
            context = await challenge_context_service.get_challenge_context(
                challenge_id=challenge_id,
                user_id=user_id,
                db_session=db_session,
                include_code=True,
                include_test_results=True,
                include_diff_analysis=True,
                include_learning_path=True,
            )

            # Analyze user situation
            situation = self._analyze_user_situation(context, user_prompt)

            # Generate targeted hints
            hints = await hint_generator.generate_contextual_hints(
                challenge_id=challenge_id,
                user_id=user_id,
                db_session=db_session,
                context=context,
                max_hints=3,
            )

            # Generate coaching strategy
            coaching_strategy = self._determine_coaching_strategy(situation, context)

            # Build enhanced system prompt
            enhanced_prompt = self._build_coaching_prompt(
                user_prompt=user_prompt,
                context=context,
                situation=situation,
                hints=hints,
                strategy=coaching_strategy,
            )

            return {
                "enhanced_prompt": enhanced_prompt,
                "coaching_metadata": {
                    "user_situation": situation,
                    "coaching_strategy": coaching_strategy,
                    "context_quality": self._assess_context_quality(context),
                    "hints_generated": len(hints),
                    "focus_areas": coaching_strategy.get("focus", []),
                },
                "learning_recommendations": self._generate_learning_recommendations(
                    context, situation
                ),
                "context_summary": {
                    "challenge_title": context.get("title", "Unknown"),
                    "difficulty": context.get("difficulty", "unknown"),
                    "attempts": context.get("attempts", 0),
                    "has_working_code": self._has_working_code(context),
                },
            }

        except Exception as e:
            logger.error(f"Failed to generate comprehensive coaching: {e}")
            return self._generate_fallback_coaching(user_prompt)

    def _analyze_user_situation(
        self, context: dict[str, Any], user_prompt: str
    ) -> dict[str, Any]:
        """Analyze user's current learning situation"""

        situation = {
            "learning_stage": "unknown",
            "confidence_level": "medium",
            "needs_encouragement": False,
            "primary_challenge": "unknown",
            "code_quality": "unknown",
        }

        # Analyze test results
        test_results = context.get("last_test_results", {})
        if test_results:
            passed = test_results.get("passed", 0)
            total = test_results.get("total", 1)
            success_rate = passed / total if total > 0 else 0

            if success_rate == 0:
                situation["learning_stage"] = "struggling"
                situation["confidence_level"] = "low"
                situation["needs_encouragement"] = True
                situation["primary_challenge"] = "getting_started"
            elif success_rate < 0.5:
                situation["learning_stage"] = "progressing"
                situation["confidence_level"] = "medium"
                situation["primary_challenge"] = "logic_refinement"
            elif success_rate < 1.0:
                situation["learning_stage"] = "advanced"
                situation["confidence_level"] = "high"
                situation["primary_challenge"] = "edge_cases"
            else:
                situation["learning_stage"] = "mastery"
                situation["confidence_level"] = "high"
                situation["primary_challenge"] = "optimization"

        # Analyze progression patterns
        progression = context.get("code_progression", {})
        if progression:
            attempts = progression.get("total_submissions", 0)
            if attempts > 5:
                situation["needs_encouragement"] = True

            patterns = progression.get("patterns_identified", [])
            if "User tends to add substantial code between attempts" in patterns:
                situation["code_quality"] = "overcomplicating"
            elif "User making small refinements" in patterns:
                situation["code_quality"] = "iterative_improvement"

        # Analyze user prompt tone
        prompt_lower = user_prompt.lower()
        if any(
            word in prompt_lower
            for word in ["stuck", "confused", "don't understand", "help", "lost"]
        ):
            situation["confidence_level"] = "low"
            situation["needs_encouragement"] = True
        elif any(
            word in prompt_lower
            for word in ["optimize", "improve", "better way", "performance"]
        ):
            situation["learning_stage"] = "advanced"
            situation["primary_challenge"] = "optimization"

        return situation

    def _determine_coaching_strategy(
        self, situation: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Determine the best coaching strategy for the user"""

        learning_stage = situation.get("learning_stage", "unknown")
        confidence_level = situation.get("confidence_level", "medium")

        # Map situation to coaching template
        if learning_stage == "struggling" or confidence_level == "low":
            strategy_key = "struggling"
        elif learning_stage == "progressing":
            strategy_key = "progressing"
        elif learning_stage == "advanced" or learning_stage == "mastery":
            strategy_key = "advanced"
        else:
            strategy_key = "stuck"

        base_strategy = self.coaching_templates.get(
            strategy_key, self.coaching_templates["progressing"]
        )

        # Customize based on specific context
        strategy = base_strategy.copy()

        # Add specific focus areas based on context
        learning_insights = context.get("learning_insights", {})
        if learning_insights:
            skill_gaps = learning_insights.get("skill_gaps", [])
            if skill_gaps:
                strategy["focus"] = strategy["focus"] + ["skill_building"]

            difficulty_assessment = learning_insights.get("difficulty_assessment", "")
            if difficulty_assessment == "too_hard":
                strategy["focus"] = ["fundamentals", "step_by_step"] + strategy["focus"]
                strategy["tone"] = "encouraging"

        return strategy

    def _build_coaching_prompt(
        self,
        user_prompt: str,
        context: dict[str, Any],
        situation: dict[str, Any],
        hints: list[dict[str, Any]],
        strategy: dict[str, Any],
    ) -> str:
        """Build enhanced coaching prompt with full context"""

        coaching_prompt = f"""You are an expert coding coach helping a student with a programming challenge. 

COACHING CONTEXT:
- Student Situation: {situation.get("learning_stage", "unknown")} learner, {situation.get("confidence_level", "medium")} confidence
- Coaching Tone: {strategy.get("tone", "supportive")}
- Focus Areas: {", ".join(strategy.get("focus", []))}
- Avoid: {", ".join(strategy.get("avoid", []))}

STUDENT'S QUESTION: {user_prompt}

COACHING GUIDELINES:
1. Be {strategy.get("tone", "supportive")} and personalized to their learning stage
2. Focus on: {", ".join(strategy.get("focus", ["general guidance"]))}
3. Provide actionable, specific advice
4. {"Encourage and build confidence" if situation.get("needs_encouragement") else "Challenge them appropriately"}
5. Reference their current code and test results when helpful

"""

        # Add relevant hints if available
        if hints:
            high_priority_hints = [h for h in hints if h.get("priority") == "high"]
            if high_priority_hints:
                coaching_prompt += """
IMMEDIATE FOCUS AREAS (based on code analysis):
"""
                for hint in high_priority_hints[:2]:  # Limit to top 2
                    coaching_prompt += (
                        f"- {hint.get('title', '')}: {hint.get('message', '')}\n"
                    )

        return coaching_prompt

    def _assess_context_quality(self, context: dict[str, Any]) -> str:
        """Assess how much context we have for coaching"""

        quality_score = 0

        if context.get("user_code"):
            quality_score += 3
        if context.get("last_test_results"):
            quality_score += 3
        if context.get("code_progression"):
            quality_score += 2
        if context.get("learning_insights"):
            quality_score += 2

        if quality_score >= 8:
            return "excellent"
        elif quality_score >= 5:
            return "good"
        elif quality_score >= 3:
            return "fair"
        else:
            return "limited"

    def _has_working_code(self, context: dict[str, Any]) -> bool:
        """Check if user has any working code"""

        test_results = context.get("last_test_results", {})
        if test_results:
            passed = test_results.get("passed", 0)
            return passed > 0

        return bool(context.get("user_code"))

    def _generate_learning_recommendations(
        self, context: dict[str, Any], situation: dict[str, Any]
    ) -> list[str]:
        """Generate specific learning recommendations"""

        recommendations = []

        learning_stage = situation.get("learning_stage", "unknown")
        primary_challenge = situation.get("primary_challenge", "unknown")

        # Stage-specific recommendations
        if learning_stage == "struggling":
            recommendations.extend(
                [
                    "Break the problem into smaller steps",
                    "Focus on getting basic functionality working first",
                    "Use console.log to debug step by step",
                ]
            )
        elif learning_stage == "progressing":
            recommendations.extend(
                [
                    "Review failing test cases carefully",
                    "Consider edge cases and boundary conditions",
                    "Look for patterns in similar problems you've solved",
                ]
            )
        elif learning_stage == "advanced":
            recommendations.extend(
                [
                    "Consider code optimization and efficiency",
                    "Think about scalability and maintainability",
                    "Explore advanced language features",
                ]
            )

        # Challenge-specific recommendations
        if primary_challenge == "optimization":
            recommendations.append(
                "Profile your code to identify performance bottlenecks"
            )
        elif primary_challenge == "edge_cases":
            recommendations.append("Create test cases for boundary conditions")

        return recommendations[:3]  # Limit to top 3

    def _generate_fallback_coaching(self, user_prompt: str) -> dict[str, Any]:
        """Generate basic coaching when context is unavailable"""

        return {
            "enhanced_prompt": f"""You are a helpful coding coach. The student asked: "{user_prompt}"

Provide supportive, educational guidance that helps them learn and grow as a programmer.""",
            "coaching_metadata": {
                "user_situation": {"learning_stage": "unknown"},
                "coaching_strategy": {"tone": "supportive"},
                "context_quality": "none",
                "hints_generated": 0,
            },
            "learning_recommendations": [
                "Break problems down into smaller steps",
                "Test your code frequently",
                "Don't be afraid to experiment",
            ],
            "context_summary": {
                "challenge_title": "Unknown",
                "difficulty": "unknown",
                "attempts": 0,
                "has_working_code": False,
            },
        }


# Global coaching system instance
ai_coaching_system = AICoachingSystem()
