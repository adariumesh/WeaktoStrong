"""
Anti-Blind-Prompting System
Validates prompts to encourage thoughtful interaction with AI
"""

import re

from ...schemas.ai_schemas import ValidationResult


class PromptValidator:
    """Validates user prompts to enforce anti-blind-prompting patterns"""

    def __init__(self):
        # Patterns that indicate thoughtful prompting
        self.required_patterns = [
            # Reasoning indicators
            r"\b(because|since|as)\b",
            r"\b(my approach|approach is|I think|I believe)\b",
            r"\b(strategy|plan|goal|intent)\b",
            r"\b(want to|trying to|attempting to)\b",
            r"\b(understand|learn|grasp)\b",
            # Context indicators
            r"\b(currently|right now|so far)\b",
            r"\b(issue|problem|challenge)\b",
            r"\b(expected|expecting|should)\b",
            # Question patterns (good questions show thinking)
            r"\bwhy (is|does|did|would|should)\b",
            r"\bhow (can|should|do|does)\b",
            r"\bwhat (if|would|should)\b",
        ]

        # Patterns that indicate lazy/blind prompting
        self.rejected_patterns = [
            # Direct commands without reasoning
            r"\b(just |simply )?(do it|make it work|fix it|solve it)\b",
            r"\b(write|generate|create|build|implement) (the |this |my )?code\b",
            r"\b(give me|show me) (the |a )?solution\b",
            r"\bcomplete this\b",
            # Generic requests
            r"\bhelp me\s*$",
            r"\bfigure (this|it) out\b",
            r"\bmake this better\b",
            # Copy-paste requests
            r"\bhere is my code\s*$",
            r"\bwhat.?s wrong\s*(\?|$)",
            r"\bdoes(n.?t| not) work\s*(\?|$)",
        ]

        self.min_length = 20  # Minimum characters for a valid prompt
        self.min_words = 5  # Minimum words for a valid prompt

    def validate(self, prompt: str) -> ValidationResult:
        """Validate a user prompt against anti-blind-prompting rules"""

        # Basic length checks
        if len(prompt.strip()) < self.min_length:
            return ValidationResult(
                is_valid=False,
                feedback="Please provide more detail about what you're trying to accomplish and your current thinking.",
                suggestions=[
                    "Explain your goal or what you're trying to achieve",
                    "Describe what you've already tried",
                    "Share your current understanding of the problem",
                ],
            )

        if len(prompt.split()) < self.min_words:
            return ValidationResult(
                is_valid=False,
                feedback="Please use more words to explain your thought process.",
                suggestions=[
                    "Describe your approach or strategy",
                    "Explain what you're thinking",
                    "Share your reasoning for this request",
                ],
            )

        prompt_lower = prompt.lower()

        # Check for lazy patterns first (immediate rejection)
        for pattern in self.rejected_patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    feedback="Please explain your thinking and approach rather than just asking for a solution.",
                    suggestions=[
                        "Start with 'I think...' or 'My approach is...'",
                        "Explain why you need help with this specific part",
                        "Describe what you understand so far",
                        "Share what you've already tried",
                    ],
                )

        # Check for thoughtful patterns
        has_reasoning = False
        for pattern in self.required_patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                has_reasoning = True
                break

        if not has_reasoning:
            return ValidationResult(
                is_valid=False,
                feedback="Help me understand your thought process. What's your approach or reasoning?",
                suggestions=[
                    "Start with 'I think...' or 'My approach is...'",
                    "Explain your goal: 'I want to...' or 'I'm trying to...'",
                    "Share your reasoning: 'Because...' or 'Since...'",
                    "Describe your strategy or plan",
                ],
            )

        # Prompt passes all checks
        return ValidationResult(
            is_valid=True,
            feedback="Good! You're explaining your thinking and approach.",
            suggestions=[],
        )

    def get_helpful_examples(self) -> list[tuple[str, str]]:
        """Get examples of good vs bad prompts"""
        return [
            (
                "❌ Bad: Fix my code",
                "✅ Good: I'm trying to center a div using flexbox, but my approach with 'justify-content: center' isn't working as expected. I think I might be missing something with the cross-axis alignment.",
            ),
            (
                "❌ Bad: Make this responsive",
                "✅ Good: I want to make my layout responsive because it currently breaks on mobile. My strategy is to use CSS Grid, but I'm unsure about the best breakpoints for tablets.",
            ),
            (
                "❌ Bad: What's wrong with this?",
                "✅ Good: I expect this function to return the filtered array, but I'm getting undefined. I think the issue might be with my array method chaining, because similar code worked in my previous project.",
            ),
        ]


# Global validator instance
prompt_validator = PromptValidator()


def validate_prompt(prompt: str) -> ValidationResult:
    """Convenience function to validate a prompt"""
    return prompt_validator.validate(prompt)
