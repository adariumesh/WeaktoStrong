"use client";

import { useState } from "react";
import { aiClient } from "@/lib/api/ai-client";
import { useAuth } from "@/hooks/useAuth";

interface Hint {
  type: string;
  priority: "high" | "medium" | "low";
  title: string;
  message: string;
  category: string;
}

interface SmartHintsProps {
  challengeId: string;
  className?: string;
}

export function SmartHints({ challengeId, className = "" }: SmartHintsProps) {
  const { isAuthenticated } = useAuth();
  const [hints, setHints] = useState<Hint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contextSummary, setContextSummary] = useState<any>(null);

  const generateHints = async () => {
    if (!isAuthenticated || !challengeId) return;

    try {
      setIsLoading(true);
      setError(null);

      const response = await aiClient.generateSmartHints(challengeId, 3);
      setHints(response.hints || []);
      setContextSummary(response.context_summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate hints");
      console.error("Smart hints generation failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "border-red-200 bg-red-50 text-red-700";
      case "medium":
        return "border-yellow-200 bg-yellow-50 text-yellow-700";
      case "low":
        return "border-blue-200 bg-blue-50 text-blue-700";
      default:
        return "border-gray-200 bg-gray-50 text-gray-700";
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "debugging":
        return "🔍";
      case "approach":
        return "🎯";
      case "performance":
        return "⚡";
      case "edge_cases":
        return "🎪";
      case "learning":
        return "📚";
      default:
        return "💡";
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className={`bg-white rounded-lg shadow p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <span>💡</span>
          Smart Hints
        </h3>
        <button
          onClick={generateHints}
          disabled={isLoading}
          className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "Generating..." : "Get Hints"}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
          {error}
        </div>
      )}

      {contextSummary && (
        <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded text-sm text-gray-600">
          <div className="flex flex-wrap gap-4">
            <span>Attempts: {contextSummary.attempts}</span>
            <span>Difficulty: {contextSummary.difficulty}</span>
            {contextSummary.has_code && (
              <span className="text-green-600">✓ Code submitted</span>
            )}
            {contextSummary.has_test_results && (
              <span className="text-blue-600">✓ Test results available</span>
            )}
          </div>
        </div>
      )}

      {hints.length > 0 ? (
        <div className="space-y-3">
          {hints.map((hint, index) => (
            <div
              key={index}
              className={`p-3 border rounded-lg ${getPriorityColor(hint.priority)}`}
            >
              <div className="flex items-start gap-2">
                <span className="text-lg" role="img" aria-label={hint.category}>
                  {getCategoryIcon(hint.category)}
                </span>
                <div className="flex-1">
                  <h4 className="font-medium text-sm mb-1">{hint.title}</h4>
                  <p className="text-sm">{hint.message}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span
                      className={`px-2 py-1 text-xs rounded ${
                        hint.priority === "high"
                          ? "bg-red-100 text-red-600"
                          : hint.priority === "medium"
                            ? "bg-yellow-100 text-yellow-600"
                            : "bg-blue-100 text-blue-600"
                      }`}
                    >
                      {hint.priority}
                    </span>
                    <span className="text-xs text-gray-500">
                      {hint.category}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        !isLoading && (
          <div className="text-center py-6 text-gray-500">
            <p className="text-sm">
              Click "Get Hints" to receive personalized suggestions based on
              your progress.
            </p>
          </div>
        )
      )}

      {isLoading && (
        <div className="text-center py-6">
          <div className="animate-pulse space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
