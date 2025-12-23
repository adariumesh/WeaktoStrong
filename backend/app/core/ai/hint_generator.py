"""
Smart Hint Generation Service
Provides contextual hints based on code analysis and learning patterns
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class SmartHintGenerator:
    """Generates contextual hints based on user progress and code analysis"""

    def __init__(self):
        self.hint_templates = {
            "syntax_error": [
                "Check your syntax around line {line}. Look for missing semicolons, brackets, or quotes.",
                "There might be a syntax issue in your code. Review the error message carefully.",
                "Double-check your code structure - are all brackets and parentheses properly closed?",
            ],
            "logic_error": [
                "Your code structure looks good, but the logic might need adjustment.",
                "Consider tracing through your code step by step with a test case.",
                "Review the problem requirements - are you handling all the expected cases?",
            ],
            "performance": [
                "Your solution works but might be inefficient. Consider optimizing the algorithm.",
                "Look for opportunities to reduce time complexity in your loops or data structures.",
                "Consider using built-in functions or libraries that might be more efficient.",
            ],
            "edge_cases": [
                "Your main logic works but consider edge cases like empty inputs or boundary values.",
                "Test your solution with extreme values - very large numbers, empty arrays, etc.",
                "Make sure your code handles null, undefined, or edge conditions gracefully.",
            ],
            "debugging": [
                "Add some console.log statements to see what values your variables contain.",
                "Step through your code mentally or with a debugger to find where it diverges from expected behavior.",
                "Check that your function returns the correct data type and format.",
            ],
            "approach": [
                "Consider breaking down the problem into smaller, manageable steps.",
                "Think about what data structures or algorithms would be most suitable for this problem.",
                "Review similar problems you've solved before - can you apply a similar approach?",
            ],
        }

    async def generate_contextual_hints(
        self,
        challenge_id: str,
        user_id: str,
        db_session: AsyncSession,
        context: dict[str, Any],
        max_hints: int = 3,
    ) -> list[dict[str, Any]]:
        """Generate smart hints based on user's current situation"""

        hints = []

        try:
            # Analyze current situation
            situation_analysis = self._analyze_situation(context)

            # Generate hints based on different factors
            if situation_analysis.get("has_syntax_errors"):
                hints.extend(self._generate_syntax_hints(context))

            if situation_analysis.get("stuck_on_logic"):
                hints.extend(self._generate_logic_hints(context))

            if situation_analysis.get("performance_issues"):
                hints.extend(self._generate_performance_hints(context))

            if situation_analysis.get("missing_edge_cases"):
                hints.extend(self._generate_edge_case_hints(context))

            # Generate progression-based hints
            if context.get("code_progression"):
                progression_hints = self._generate_progression_hints(
                    context["code_progression"]
                )
                hints.extend(progression_hints)

            # Generate learning path hints
            if context.get("learning_insights"):
                learning_hints = self._generate_learning_hints(
                    context["learning_insights"]
                )
                hints.extend(learning_hints)

            # Prioritize and limit hints
            prioritized_hints = self._prioritize_hints(hints, situation_analysis)

            return prioritized_hints[:max_hints]

        except Exception as e:
            logger.error(f"Failed to generate contextual hints: {e}")
            return self._generate_fallback_hints()

    def _analyze_situation(self, context: dict[str, Any]) -> dict[str, bool]:
        """Analyze the user's current situation to determine hint strategy"""

        analysis = {
            "has_syntax_errors": False,
            "stuck_on_logic": False,
            "performance_issues": False,
            "missing_edge_cases": False,
            "needs_encouragement": False,
        }

        # Check test results for patterns
        test_results = context.get("last_test_results", {})
        if test_results:
            errors = test_results.get("errors", "")
            failures = test_results.get("failures", "")
            passed = test_results.get("passed", 0)
            total = test_results.get("total", 1)

            # Detect syntax errors
            if errors and any(
                keyword in str(errors).lower()
                for keyword in [
                    "syntaxerror",
                    "unexpected token",
                    "missing",
                    "invalid syntax",
                ]
            ):
                analysis["has_syntax_errors"] = True

            # Detect logic issues
            if passed > 0 and passed < total:
                analysis["stuck_on_logic"] = True

            # Detect edge case issues
            if failures and any(
                keyword in str(failures).lower()
                for keyword in ["edge", "boundary", "empty", "null"]
            ):
                analysis["missing_edge_cases"] = True

        # Check progression patterns
        progression = context.get("code_progression", {})
        if progression:
            total_submissions = progression.get("total_submissions", 0)
            patterns = progression.get("patterns_identified", [])

            if total_submissions > 5:
                analysis["needs_encouragement"] = True

            if "User tends to add substantial code between attempts" in patterns:
                analysis["stuck_on_logic"] = True

        # Check learning insights
        insights = context.get("learning_insights", {})
        if insights:
            difficulty = insights.get("difficulty_assessment", "")
            if difficulty == "too_hard":
                analysis["needs_encouragement"] = True

        return analysis

    def _generate_syntax_hints(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate hints for syntax issues"""
        hints = []

        test_results = context.get("last_test_results", {})
        errors = str(test_results.get("errors", "")).lower()

        if "missing semicolon" in errors or "unexpected token" in errors:
            hints.append(
                {
                    "type": "syntax",
                    "priority": "high",
                    "title": "Syntax Check",
                    "message": "Check for missing semicolons or unexpected characters in your code.",
                    "category": "debugging",
                }
            )

        if "bracket" in errors or "parenthesis" in errors:
            hints.append(
                {
                    "type": "syntax",
                    "priority": "high",
                    "title": "Bracket Mismatch",
                    "message": "Make sure all brackets and parentheses are properly opened and closed.",
                    "category": "debugging",
                }
            )

        return hints

    def _generate_logic_hints(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate hints for logic issues"""
        hints = []

        test_results = context.get("last_test_results", {})
        passed = test_results.get("passed", 0)
        total = test_results.get("total", 1)

        if passed == 0:
            hints.append(
                {
                    "type": "logic",
                    "priority": "high",
                    "title": "Logic Foundation",
                    "message": "Focus on getting the basic functionality working first. Break the problem into smaller steps.",
                    "category": "approach",
                }
            )
        elif passed < total * 0.5:
            hints.append(
                {
                    "type": "logic",
                    "priority": "medium",
                    "title": "Partial Success",
                    "message": "You're on the right track! Review the failing test cases to see what conditions you might be missing.",
                    "category": "debugging",
                }
            )

        return hints

    def _generate_performance_hints(
        self, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate hints for performance optimization"""
        hints = []

        test_results = context.get("last_test_results", {})
        execution_time = test_results.get("execution_time")

        if execution_time and execution_time > 1000:  # More than 1 second
            hints.append(
                {
                    "type": "performance",
                    "priority": "low",
                    "title": "Performance Optimization",
                    "message": "Your solution works but might be slow. Consider optimizing your algorithm or using more efficient data structures.",
                    "category": "performance",
                }
            )

        return hints

    def _generate_edge_case_hints(
        self, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate hints for edge case handling"""
        hints = []

        test_results = context.get("last_test_results", {})
        failures = str(test_results.get("failures", "")).lower()

        if any(
            keyword in failures
            for keyword in ["empty", "null", "undefined", "boundary"]
        ):
            hints.append(
                {
                    "type": "edge_cases",
                    "priority": "medium",
                    "title": "Edge Cases",
                    "message": "Consider edge cases like empty inputs, null values, or boundary conditions.",
                    "category": "edge_cases",
                }
            )

        return hints

    def _generate_progression_hints(
        self, progression: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate hints based on code progression patterns"""
        hints = []

        patterns = progression.get("patterns_identified", [])
        total_submissions = progression.get("total_submissions", 0)

        if total_submissions > 5:
            hints.append(
                {
                    "type": "progression",
                    "priority": "low",
                    "title": "Take a Step Back",
                    "message": "You've made several attempts. Consider reviewing the problem requirements and planning your approach before coding.",
                    "category": "approach",
                }
            )

        if "User tends to add substantial code between attempts" in patterns:
            hints.append(
                {
                    "type": "progression",
                    "priority": "medium",
                    "title": "Simpler Approach",
                    "message": "Try a simpler approach first. Complex solutions can be harder to debug and may not be necessary.",
                    "category": "approach",
                }
            )

        return hints

    def _generate_learning_hints(
        self, insights: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate hints based on learning insights"""
        hints = []

        difficulty = insights.get("difficulty_assessment", "")
        skill_gaps = insights.get("skill_gaps", [])

        if difficulty == "too_hard":
            hints.append(
                {
                    "type": "learning",
                    "priority": "high",
                    "title": "Challenging Problem",
                    "message": "This challenge might be above your current level. Focus on understanding the core concepts first.",
                    "category": "approach",
                }
            )

        if skill_gaps:
            gap = skill_gaps[0]  # Focus on first gap
            hints.append(
                {
                    "type": "learning",
                    "priority": "medium",
                    "title": "Skill Development",
                    "message": f"Consider reviewing {gap.lower()} to strengthen your foundation for this type of problem.",
                    "category": "learning",
                }
            )

        return hints

    def _prioritize_hints(
        self, hints: list[dict[str, Any]], analysis: dict[str, bool]
    ) -> list[dict[str, Any]]:
        """Prioritize hints based on situation analysis"""

        # Sort by priority level
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_hints = sorted(hints, key=lambda h: priority_order.get(h["priority"], 3))

        # Remove duplicates based on message content
        unique_hints = []
        seen_messages = set()

        for hint in sorted_hints:
            message = hint["message"]
            if message not in seen_messages:
                unique_hints.append(hint)
                seen_messages.add(message)

        return unique_hints

    def _generate_fallback_hints(self) -> list[dict[str, Any]]:
        """Generate generic helpful hints when context analysis fails"""
        return [
            {
                "type": "general",
                "priority": "medium",
                "title": "Debug Systematically",
                "message": "Add console.log statements to understand what your code is doing at each step.",
                "category": "debugging",
            },
            {
                "type": "general",
                "priority": "medium",
                "title": "Break It Down",
                "message": "Try breaking the problem into smaller parts and solve each one step by step.",
                "category": "approach",
            },
            {
                "type": "general",
                "priority": "low",
                "title": "Test Edge Cases",
                "message": "Make sure your solution works with edge cases like empty inputs or boundary values.",
                "category": "edge_cases",
            },
        ]


# Global service instance
hint_generator = SmartHintGenerator()
