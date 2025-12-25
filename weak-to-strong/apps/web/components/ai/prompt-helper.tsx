"use client";

import { X, Lightbulb, AlertTriangle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ValidationResult } from "@/types/ai";

interface PromptHelperProps {
  validation: ValidationResult;
  onDismiss: () => void;
  onExample: (example: string) => void;
}

const GOOD_EXAMPLES = [
  {
    category: "Problem-solving approach",
    examples: [
      "I'm trying to center a div horizontally and vertically using CSS. My current approach is using flexbox with justify-content: center, but the vertical centering isn't working. I think I might be missing align-items: center.",
      "I want to create a responsive navigation bar that collapses on mobile devices. My strategy is to use CSS media queries and JavaScript to toggle a hamburger menu, but I'm unsure about the best breakpoint to use.",
    ],
  },
  {
    category: "Code debugging",
    examples: [
      "My JavaScript function should return the sum of an array, but I'm getting NaN instead. I think the issue might be with my reduce method because I'm not providing an initial value of 0.",
      "I expect my CSS grid layout to have three equal columns, but they're not sizing correctly. My approach was to use 'grid-template-columns: 1fr 1fr 1fr', but maybe I need to consider the container width.",
    ],
  },
  {
    category: "Learning concepts",
    examples: [
      "I understand that promises help with asynchronous JavaScript, but I'm confused about when to use .then() versus async/await. I want to learn the best practices for error handling in both approaches.",
      "I'm learning about CSS specificity and why my styles aren't being applied. I believe it's because the existing styles have higher specificity, but I want to understand how to calculate specificity correctly.",
    ],
  },
];

const IMPROVEMENT_TIPS = [
  "Start with 'I think...' or 'I believe...' to show your reasoning",
  "Use 'My approach is...' to explain your strategy",
  "Say 'I want to...' or 'I'm trying to...' to clarify your goal",
  "Include 'because...' to show cause-and-effect thinking",
  "Describe what you expect vs. what's actually happening",
  "Share what you've already tried or considered",
];

export function PromptHelper({
  validation,
  onDismiss,
  onExample,
}: PromptHelperProps) {
  return (
    <div className="absolute bottom-full left-0 right-0 mb-2 z-50">
      <Card className="mx-4 border-orange-200 bg-orange-50">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-base text-orange-800">
              <AlertTriangle className="w-4 h-4" />
              Let's improve your prompt
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
              className="h-8 w-8 p-0 text-orange-600 hover:text-orange-800"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Validation Feedback */}
          <div className="p-3 bg-white rounded-lg border border-orange-200">
            <p className="text-sm text-orange-800 mb-2">
              <strong>Issue:</strong> {validation.feedback}
            </p>
            {validation.suggestions.length > 0 && (
              <ul className="text-sm text-orange-700 space-y-1">
                {validation.suggestions.map((suggestion, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1 h-1 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                    {suggestion}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Quick Tips */}
          <div>
            <h4 className="flex items-center gap-2 text-sm font-medium text-orange-800 mb-2">
              <Lightbulb className="w-4 h-4" />
              Quick improvement tips:
            </h4>
            <div className="grid grid-cols-1 gap-1">
              {IMPROVEMENT_TIPS.slice(0, 3).map((tip, idx) => (
                <Badge
                  key={idx}
                  variant="outline"
                  className="justify-start text-xs text-orange-700 border-orange-300 cursor-pointer hover:bg-orange-100"
                  onClick={() => {
                    // Extract the phrase in quotes for quick insertion
                    const match = tip.match(/'([^']+)'/);
                    if (match) {
                      onExample(match[1] + " ");
                    }
                  }}
                >
                  {tip}
                </Badge>
              ))}
            </div>
          </div>

          {/* Example Prompts */}
          <div>
            <h4 className="flex items-center gap-2 text-sm font-medium text-orange-800 mb-3">
              <CheckCircle className="w-4 h-4" />
              Good example prompts:
            </h4>
            <div className="space-y-3 max-h-48 overflow-y-auto">
              {GOOD_EXAMPLES.map((category, catIdx) => (
                <div key={catIdx}>
                  <Badge variant="secondary" className="text-xs mb-2">
                    {category.category}
                  </Badge>
                  <div className="space-y-2">
                    {category.examples.map((example, exIdx) => (
                      <div
                        key={exIdx}
                        className="p-2 bg-white border border-gray-200 rounded text-xs text-gray-700 cursor-pointer hover:border-orange-300 hover:bg-orange-50 transition-colors"
                        onClick={() => onExample(example)}
                      >
                        "{example}"
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onDismiss}
              className="text-orange-700 border-orange-300 hover:bg-orange-100"
            >
              I'll improve it myself
            </Button>
            <Button
              size="sm"
              onClick={() => {
                onExample("I think my approach is to ");
              }}
              className="bg-orange-600 hover:bg-orange-700 text-white"
            >
              Start with "I think..."
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
