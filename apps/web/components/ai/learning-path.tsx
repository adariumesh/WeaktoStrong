"use client";

import { useState, useEffect } from "react";
import { aiClient } from "@/lib/api/ai-client";
import { useAuth } from "@/hooks/useAuth";

interface LearningInsights {
  difficulty_assessment: string;
  recommended_resources: string[];
  skill_gaps: string[];
  next_challenges: Array<{
    id: string;
    title: string;
    difficulty: string;
  }>;
  learning_path_status: {
    current_track: string;
    track_completion: string;
    suggested_focus: string;
  };
}

interface LearningPathProps {
  challengeId: string;
  className?: string;
}

export function LearningPath({
  challengeId,
  className = "",
}: LearningPathProps) {
  const { isAuthenticated } = useAuth();
  const [insights, setInsights] = useState<LearningInsights | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (challengeId && isAuthenticated) {
      loadLearningInsights();
    }
  }, [challengeId, isAuthenticated]);

  const loadLearningInsights = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await aiClient.getChallengeContext(challengeId);
      const learningInsights = response.challenge_context?.learning_insights;

      if (learningInsights) {
        setInsights(learningInsights);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load learning insights"
      );
      console.error("Learning insights loading failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const getDifficultyColor = (assessment: string) => {
    switch (assessment) {
      case "too_easy":
        return "text-green-600 bg-green-50 border-green-200";
      case "too_hard":
        return "text-red-600 bg-red-50 border-red-200";
      case "appropriate":
        return "text-blue-600 bg-blue-50 border-blue-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const getDifficultyIcon = (assessment: string) => {
    switch (assessment) {
      case "too_easy":
        return "😴";
      case "too_hard":
        return "🔥";
      case "appropriate":
        return "🎯";
      default:
        return "📊";
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow p-4 ${className}`}>
        <h3 className="font-semibold text-gray-900 mb-3">Learning Path</h3>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow p-4 ${className}`}>
        <h3 className="font-semibold text-gray-900 mb-3">Learning Path</h3>
        <div className="text-red-600 text-sm">{error}</div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className={`bg-white rounded-lg shadow p-4 ${className}`}>
        <h3 className="font-semibold text-gray-900 mb-3">Learning Path</h3>
        <div className="text-gray-500 text-sm">
          No learning insights available for this challenge.
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow p-4 ${className}`}>
      <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <span>🗺️</span>
        Learning Path
      </h3>

      {/* Difficulty Assessment */}
      <div
        className={`mb-4 p-3 border rounded-lg ${getDifficultyColor(insights.difficulty_assessment)}`}
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="text-lg">
            {getDifficultyIcon(insights.difficulty_assessment)}
          </span>
          <h4 className="font-medium">Difficulty Assessment</h4>
        </div>
        <p className="text-sm capitalize">
          {insights.difficulty_assessment.replace("_", " ")}
        </p>
      </div>

      {/* Current Track & Focus */}
      {insights.learning_path_status && (
        <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
          <h4 className="font-medium text-purple-800 mb-2 flex items-center gap-2">
            <span>🎯</span>
            Current Focus
          </h4>
          <div className="text-sm text-purple-700 space-y-1">
            <p>
              <strong>Track:</strong>{" "}
              {insights.learning_path_status.current_track}
            </p>
            <p>
              <strong>Level:</strong>{" "}
              {insights.learning_path_status.track_completion}
            </p>
            <p>
              <strong>Suggested Focus:</strong>{" "}
              {insights.learning_path_status.suggested_focus}
            </p>
          </div>
        </div>
      )}

      {/* Skill Gaps */}
      {insights.skill_gaps && insights.skill_gaps.length > 0 && (
        <div className="mb-4">
          <h4 className="font-medium text-gray-800 mb-2 flex items-center gap-2">
            <span>🎓</span>
            Areas for Improvement
          </h4>
          <div className="space-y-2">
            {insights.skill_gaps.map((gap, index) => (
              <div
                key={index}
                className="text-sm bg-orange-50 border border-orange-200 text-orange-700 px-3 py-2 rounded"
              >
                {gap}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommended Resources */}
      {insights.recommended_resources &&
        insights.recommended_resources.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium text-gray-800 mb-2 flex items-center gap-2">
              <span>📚</span>
              Recommendations
            </h4>
            <div className="space-y-2">
              {insights.recommended_resources.map((resource, index) => (
                <div
                  key={index}
                  className="text-sm bg-blue-50 border border-blue-200 text-blue-700 px-3 py-2 rounded"
                >
                  {resource}
                </div>
              ))}
            </div>
          </div>
        )}

      {/* Next Challenges */}
      {insights.next_challenges && insights.next_challenges.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-800 mb-2 flex items-center gap-2">
            <span>🚀</span>
            Similar Challenges
          </h4>
          <div className="space-y-2">
            {insights.next_challenges.map((challenge) => (
              <div
                key={challenge.id}
                className="text-sm bg-gray-50 border border-gray-200 px-3 py-2 rounded flex justify-between items-center"
              >
                <span className="font-medium">{challenge.title}</span>
                <span
                  className={`px-2 py-1 text-xs rounded ${
                    challenge.difficulty === "beginner"
                      ? "bg-green-100 text-green-600"
                      : challenge.difficulty === "intermediate"
                        ? "bg-yellow-100 text-yellow-600"
                        : challenge.difficulty === "advanced"
                          ? "bg-orange-100 text-orange-600"
                          : "bg-red-100 text-red-600"
                  }`}
                >
                  {challenge.difficulty}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <button
          onClick={loadLearningInsights}
          className="w-full text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          🔄 Refresh Learning Insights
        </button>
      </div>
    </div>
  );
}
