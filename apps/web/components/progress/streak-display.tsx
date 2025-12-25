/**
 * Streak Display Component
 * Shows user's current and longest streak with visual indicators
 */

"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Flame, Calendar, Clock } from "lucide-react";

interface StreakDisplayProps {
  currentStreak: number;
  longestStreak: number;
  streakActive: boolean;
  daysUntilReset: number;
}

export function StreakDisplay({
  currentStreak,
  longestStreak,
  streakActive,
  daysUntilReset,
}: StreakDisplayProps) {
  const streakLevel = getStreakLevel(currentStreak);
  const nextMilestone = getNextMilestone(currentStreak);
  const progressToNext = nextMilestone
    ? (currentStreak / nextMilestone) * 100
    : 100;

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold flex items-center">
            <Flame
              className={`h-5 w-5 mr-2 ${streakActive ? "text-orange-500" : "text-gray-400"}`}
            />
            Learning Streak
          </h3>
          <Badge variant={streakActive ? "default" : "secondary"}>
            {streakActive ? "Active" : "Inactive"}
          </Badge>
        </div>

        {/* Current Streak */}
        <div className="text-center">
          <div className="text-4xl font-bold text-orange-500 mb-2">
            {currentStreak}
          </div>
          <p className="text-sm text-gray-600">
            {currentStreak === 1 ? "day" : "days"} current streak
          </p>

          {/* Streak Level Badge */}
          {streakLevel && (
            <Badge className="mt-2" variant="outline">
              {streakLevel.name}
            </Badge>
          )}
        </div>

        {/* Progress to Next Milestone */}
        {nextMilestone && currentStreak < nextMilestone && (
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Progress to {nextMilestone}-day milestone</span>
              <span>
                {currentStreak}/{nextMilestone}
              </span>
            </div>
            <Progress value={progressToNext} className="h-2" />
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-700">
              {longestStreak}
            </div>
            <p className="text-xs text-gray-500">Best Streak</p>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-gray-700">
              {daysUntilReset}
            </div>
            <p className="text-xs text-gray-500">
              {daysUntilReset <= 0 ? "Resets Today" : "Days to Reset"}
            </p>
          </div>
        </div>

        {/* Streak Status */}
        <div className="space-y-2 pt-4 border-t">
          <div className="flex items-center text-sm">
            <Calendar className="h-4 w-4 mr-2 text-gray-500" />
            <span className="text-gray-600">
              {streakActive
                ? "Keep it up! Complete a challenge today to maintain your streak."
                : "Start a new streak by completing a challenge today!"}
            </span>
          </div>

          {!streakActive && daysUntilReset <= 0 && (
            <div className="flex items-center text-sm text-amber-600">
              <Clock className="h-4 w-4 mr-2" />
              <span>
                Your streak will reset at midnight if you don't complete a
                challenge today.
              </span>
            </div>
          )}
        </div>

        {/* Motivational Message */}
        {currentStreak > 0 && (
          <div className="bg-orange-50 p-3 rounded-lg">
            <p className="text-sm text-orange-800">
              {getMotivationalMessage(currentStreak, longestStreak)}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}

function getStreakLevel(streak: number) {
  if (streak >= 100) return { name: "Legendary", color: "text-purple-600" };
  if (streak >= 50) return { name: "Expert", color: "text-blue-600" };
  if (streak >= 30) return { name: "Advanced", color: "text-green-600" };
  if (streak >= 14) return { name: "Committed", color: "text-yellow-600" };
  if (streak >= 7) return { name: "Consistent", color: "text-orange-600" };
  if (streak >= 3) return { name: "Building", color: "text-gray-600" };
  return null;
}

function getNextMilestone(streak: number): number | null {
  const milestones = [3, 7, 14, 30, 50, 100];
  return milestones.find((milestone) => milestone > streak) || null;
}

function getMotivationalMessage(current: number, longest: number): string {
  if (current === longest && current >= 7) {
    return "🔥 You're on your best streak ever! Keep the momentum going!";
  }

  if (current >= 30) {
    return "🏆 Amazing consistency! You're building some serious coding habits.";
  }

  if (current >= 14) {
    return "💪 Two weeks strong! You're developing real discipline.";
  }

  if (current >= 7) {
    return "⭐ One week streak! You're building great learning habits.";
  }

  if (current >= 3) {
    return "🚀 Nice start! Keep going to build momentum.";
  }

  return "💡 Every expert was once a beginner. Keep learning!";
}
