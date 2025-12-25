/**
 * Frontend prompt validation for anti-blind-prompting
 * Mirrors the backend validation logic
 */

import type { ValidationResult } from "@/types/ai";

interface PromptValidator {
  requiredPatterns: RegExp[];
  rejectedPatterns: RegExp[];
  minLength: number;
  minWords: number;
}

class ClientPromptValidator implements PromptValidator {
  requiredPatterns = [
    // Reasoning indicators
    /\b(because|since|as)\b/i,
    /\b(my approach|approach is|I think|I believe)\b/i,
    /\b(strategy|plan|goal|intent)\b/i,
    /\b(want to|trying to|attempting to)\b/i,
    /\b(understand|learn|grasp)\b/i,

    // Context indicators
    /\b(currently|right now|so far)\b/i,
    /\b(issue|problem|challenge)\b/i,
    /\b(expected|expecting|should)\b/i,

    // Question patterns (good questions show thinking)
    /\bwhy (is|does|did|would|should)\b/i,
    /\bhow (can|should|do|does)\b/i,
    /\bwhat (if|would|should)\b/i,
  ];

  rejectedPatterns = [
    // Direct commands without reasoning
    /\b(just |simply )?(do it|make it work|fix it|solve it)\b/i,
    /\b(write|generate|create|build|implement) (the |this |my )?code\b/i,
    /\b(give me|show me) (the |a )?solution\b/i,
    /\bcomplete this\b/i,

    // Generic requests
    /\bhelp me\s*$/i,
    /\bfigure (this|it) out\b/i,
    /\bmake this better\b/i,

    // Copy-paste requests
    /\bhere is my code\s*$/i,
    /\bwhat.?s wrong\s*(\?|$)/i,
    /\bdoes(n.?t| not) work\s*(\?|$)/i,
  ];

  minLength = 20;
  minWords = 5;

  validate(prompt: string): ValidationResult {
    const trimmed = prompt.trim();

    // Basic length checks
    if (trimmed.length < this.minLength) {
      return {
        isValid: false,
        feedback:
          "Please provide more detail about what you're trying to accomplish and your current thinking.",
        suggestions: [
          "Explain your goal or what you're trying to achieve",
          "Describe what you've already tried",
          "Share your current understanding of the problem",
        ],
      };
    }

    if (trimmed.split(/\s+/).length < this.minWords) {
      return {
        isValid: false,
        feedback: "Please use more words to explain your thought process.",
        suggestions: [
          "Describe your approach or strategy",
          "Explain what you're thinking",
          "Share your reasoning for this request",
        ],
      };
    }

    // Check for lazy patterns first (immediate rejection)
    for (const pattern of this.rejectedPatterns) {
      if (pattern.test(trimmed)) {
        return {
          isValid: false,
          feedback:
            "Please explain your thinking and approach rather than just asking for a solution.",
          suggestions: [
            "Start with 'I think...' or 'My approach is...'",
            "Explain why you need help with this specific part",
            "Describe what you understand so far",
            "Share what you've already tried",
          ],
        };
      }
    }

    // Check for thoughtful patterns
    const hasReasoning = this.requiredPatterns.some((pattern) =>
      pattern.test(trimmed)
    );

    if (!hasReasoning) {
      return {
        isValid: false,
        feedback:
          "Help me understand your thought process. What's your approach or reasoning?",
        suggestions: [
          "Start with 'I think...' or 'My approach is...'",
          "Explain your goal: 'I want to...' or 'I'm trying to...'",
          "Share your reasoning: 'Because...' or 'Since...'",
          "Describe your strategy or plan",
        ],
      };
    }

    // Prompt passes all checks
    return {
      isValid: true,
      feedback: "Good! You're explaining your thinking and approach.",
      suggestions: [],
    };
  }

  getHelpfulExamples(): Array<{ bad: string; good: string }> {
    return [
      {
        bad: "Fix my code",
        good: "I'm trying to center a div using flexbox, but my approach with 'justify-content: center' isn't working as expected. I think I might be missing something with the cross-axis alignment.",
      },
      {
        bad: "Make this responsive",
        good: "I want to make my layout responsive because it currently breaks on mobile. My strategy is to use CSS Grid, but I'm unsure about the best breakpoints for tablets.",
      },
      {
        bad: "What's wrong with this?",
        good: "I expect this function to return the filtered array, but I'm getting undefined. I think the issue might be with my array method chaining, because similar code worked in my previous project.",
      },
    ];
  }
}

// Global validator instance
const promptValidator = new ClientPromptValidator();

/**
 * Validate a prompt on the client side
 */
export function validatePrompt(prompt: string): ValidationResult {
  return promptValidator.validate(prompt);
}

/**
 * Get examples of good vs bad prompts
 */
export function getPromptExamples() {
  return promptValidator.getHelpfulExamples();
}
