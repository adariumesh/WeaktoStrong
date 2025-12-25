/**
 * Achievements List Component
 * Displays user achievements with progress indicators
 */

"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Award, Star, Lock } from "lucide-react";

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  points: number;
  earned: boolean;
  available: boolean;
  earned_at: string | null;
}

export function AchievementsList() {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAchievements();
  }, []);

  const loadAchievements = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/progress/achievements", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load achievements");
      }

      const data = await response.json();
      setAchievements(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load achievements"
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="space-y-4 animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-48" />
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-gray-200 rounded-full" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={loadAchievements}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Try Again
        </button>
      </Card>
    );
  }

  const earnedAchievements = achievements.filter((a) => a.earned);
  const availableAchievements = achievements.filter(
    (a) => a.available && !a.earned
  );
  const lockedAchievements = achievements.filter(
    (a) => !a.available && !a.earned
  );

  const totalPoints = earnedAchievements.reduce((sum, a) => sum + a.points, 0);
  const completionRate =
    achievements.length > 0
      ? (earnedAchievements.length / achievements.length) * 100
      : 0;

  return (
    <div className="space-y-6">
      {/* Overview */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Award className="h-5 w-5 mr-2" />
            Achievements
          </h3>
          <div className="text-right">
            <p className="text-2xl font-bold text-yellow-600">{totalPoints}</p>
            <p className="text-sm text-gray-600">points earned</p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>
              {earnedAchievements.length} of {achievements.length}
            </span>
          </div>
          <Progress value={completionRate} className="h-2" />
        </div>
      </Card>

      {/* Earned Achievements */}
      {earnedAchievements.length > 0 && (
        <Card className="p-6">
          <h4 className="text-md font-semibold mb-4 flex items-center text-green-700">
            <Star className="h-4 w-4 mr-2" />
            Earned ({earnedAchievements.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {earnedAchievements.map((achievement) => (
              <div
                key={achievement.id}
                className="flex items-center space-x-4 p-3 bg-green-50 rounded-lg border border-green-200"
              >
                <div className="text-3xl">{achievement.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h5 className="font-medium text-green-800">
                      {achievement.title}
                    </h5>
                    <Badge
                      variant="outline"
                      className="text-xs bg-green-100 text-green-700"
                    >
                      {achievement.points} pts
                    </Badge>
                  </div>
                  <p className="text-sm text-green-600 mb-2">
                    {achievement.description}
                  </p>
                  {achievement.earned_at && (
                    <p className="text-xs text-green-500">
                      Earned{" "}
                      {new Date(achievement.earned_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <div className="text-green-500">
                  <Award className="h-5 w-5" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Available Achievements */}
      {availableAchievements.length > 0 && (
        <Card className="p-6">
          <h4 className="text-md font-semibold mb-4 flex items-center text-blue-700">
            <Star className="h-4 w-4 mr-2" />
            Available ({availableAchievements.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableAchievements.map((achievement) => (
              <div
                key={achievement.id}
                className="flex items-center space-x-4 p-3 bg-blue-50 rounded-lg border border-blue-200"
              >
                <div className="text-3xl">{achievement.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h5 className="font-medium text-blue-800">
                      {achievement.title}
                    </h5>
                    <Badge
                      variant="outline"
                      className="text-xs bg-blue-100 text-blue-700"
                    >
                      {achievement.points} pts
                    </Badge>
                  </div>
                  <p className="text-sm text-blue-600">
                    {achievement.description}
                  </p>
                </div>
                <div className="text-blue-500">
                  <div className="h-5 w-5 border-2 border-blue-500 rounded-full" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Locked Achievements */}
      {lockedAchievements.length > 0 && (
        <Card className="p-6">
          <h4 className="text-md font-semibold mb-4 flex items-center text-gray-500">
            <Lock className="h-4 w-4 mr-2" />
            Locked ({lockedAchievements.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {lockedAchievements.map((achievement) => (
              <div
                key={achievement.id}
                className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg border border-gray-200 opacity-75"
              >
                <div className="text-3xl grayscale">{achievement.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h5 className="font-medium text-gray-600">
                      {achievement.title}
                    </h5>
                    <Badge
                      variant="outline"
                      className="text-xs bg-gray-100 text-gray-500"
                    >
                      {achievement.points} pts
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-500">
                    {achievement.description}
                  </p>
                </div>
                <div className="text-gray-400">
                  <Lock className="h-5 w-5" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {achievements.length === 0 && (
        <Card className="p-6 text-center">
          <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">No achievements available yet</p>
          <p className="text-sm text-gray-500">
            Complete challenges to unlock achievements and earn points!
          </p>
        </Card>
      )}
    </div>
  );
}
