/**
 * Track Progress Component
 * Displays progress for individual tracks (Web, Data, Cloud)
 */

"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { CheckCircle, Circle, Lock, Play } from "lucide-react";

interface Challenge {
  order: number;
  status: "locked" | "available" | "attempted" | "completed";
  score: number;
  points: number;
}

interface TrackData {
  track: string;
  completed: number;
  total: number;
  percentage: number;
  challenges: Challenge[];
}

interface TrackProgressProps {
  trackName: string;
  trackData: TrackData;
}

const trackIcons = {
  web: "🌐",
  data: "📊",
  cloud: "☁️",
};

const trackColors = {
  web: "bg-blue-500",
  data: "bg-green-500",
  cloud: "bg-purple-500",
};

export function TrackProgress({ trackName, trackData }: TrackProgressProps) {
  if (!trackData) {
    return (
      <Card className="p-6">
        <div className="text-center text-gray-500">
          <p>Track data not available</p>
        </div>
      </Card>
    );
  }

  const { track, completed, total, percentage, challenges } = trackData;
  const trackIcon = trackIcons[trackName as keyof typeof trackIcons] || "📚";
  const trackColor =
    trackColors[trackName as keyof typeof trackColors] || "bg-gray-500";

  // Get next available challenge
  const nextChallenge = challenges?.find((c) => c.status === "available");
  const completedChallenges =
    challenges?.filter((c) => c.status === "completed") || [];
  const totalPoints = completedChallenges.reduce((sum, c) => sum + c.points, 0);

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{trackIcon}</span>
            <div>
              <h3 className="text-lg font-semibold capitalize">
                {trackName} Track
              </h3>
              <p className="text-sm text-gray-600">
                {completed} of {total} challenges
              </p>
            </div>
          </div>

          <Badge className={`${trackColor} text-white`}>
            {(percentage || 0).toFixed(0)}%
          </Badge>
        </div>

        {/* Progress Bar */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span>Progress</span>
            <span>
              {completed}/{total}
            </span>
          </div>
          <Progress value={percentage || 0} className="h-3" />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 py-2">
          <div className="text-center">
            <div className="text-xl font-bold text-gray-700">
              {totalPoints.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500">Points Earned</p>
          </div>

          <div className="text-center">
            <div className="text-xl font-bold text-gray-700">
              {completedChallenges.length > 0
                ? Math.round(
                    completedChallenges.reduce((sum, c) => sum + c.score, 0) /
                      completedChallenges.length
                  )
                : 0}
              %
            </div>
            <p className="text-xs text-gray-500">Avg Score</p>
          </div>
        </div>

        {/* Challenge Grid */}
        {challenges && challenges.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-3">Challenges</h4>
            <div className="grid grid-cols-5 gap-2">
              {challenges.slice(0, 15).map((challenge) => (
                <div
                  key={challenge.order}
                  className="relative group"
                  title={`Challenge ${challenge.order}: ${challenge.status}`}
                >
                  {challenge.status === "completed" && (
                    <CheckCircle className="h-6 w-6 text-green-500" />
                  )}
                  {challenge.status === "attempted" && (
                    <Circle className="h-6 w-6 text-yellow-500" />
                  )}
                  {challenge.status === "available" && (
                    <Play className="h-6 w-6 text-blue-500" />
                  )}
                  {challenge.status === "locked" && (
                    <Lock className="h-6 w-6 text-gray-300" />
                  )}

                  {/* Tooltip */}
                  <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                    Challenge {challenge.order}
                    {challenge.status === "completed" && (
                      <div>
                        Score: {challenge.score}% | Points: {challenge.points}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Challenge */}
        {nextChallenge && (
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-blue-800 mb-1">
              Up Next: Challenge {nextChallenge.order}
            </p>
            <p className="text-xs text-blue-600">
              Ready to continue your {trackName} track journey!
            </p>
          </div>
        )}

        {/* Completion Message */}
        {completed === total && total > 0 && (
          <div className="bg-green-50 p-3 rounded-lg text-center">
            <p className="text-sm font-medium text-green-800 mb-1">
              🎉 Track Completed!
            </p>
            <p className="text-xs text-green-600">
              Congratulations on completing the {trackName} track!
            </p>
          </div>
        )}

        {/* Call to Action */}
        {completed < total && (
          <button
            className={`w-full px-4 py-2 ${trackColor} text-white rounded hover:opacity-90 transition-opacity text-sm`}
            onClick={() => {
              if (nextChallenge) {
                // Navigate to next challenge
                window.location.href = `/challenges?track=${trackName}&challenge=${nextChallenge.order}`;
              } else {
                // Navigate to track overview
                window.location.href = `/challenges?track=${trackName}`;
              }
            }}
          >
            {nextChallenge
              ? `Continue Challenge ${nextChallenge.order}`
              : `Browse ${trackName} Challenges`}
          </button>
        )}
      </div>
    </Card>
  );
}
