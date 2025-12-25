/**
 * Progress Dashboard Component
 * Displays user's overall progress, streaks, and achievements
 */

"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { StreakDisplay } from "./streak-display";
import { AchievementsList } from "./achievements-list";
import { TrackProgress } from "./track-progress";
import { CertificatesList } from "./certificates-list";
import { useProgress } from "@/hooks/useProgress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Trophy, Target, Zap, BookOpen, Award, TrendingUp } from "lucide-react";

interface ProgressStats {
  overview: {
    total_points: number;
    challenges_completed: number;
    challenges_attempted: number;
    completion_rate: number;
    ai_tier: string;
  };
  streaks: {
    current_streak: number;
    longest_streak: number;
    streak_active: boolean;
    days_until_reset: number;
  };
  achievements: {
    earned: number;
    total: number;
    recent: any[];
  };
  tracks: {
    web: any;
    data: any;
    cloud: any;
  };
  activity: {
    last_activity: string;
    ai_requests_total: number;
  };
}

export function ProgressDashboard() {
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { refreshProgress } = useProgress();

  useEffect(() => {
    loadProgressStats();
  }, []);

  const loadProgressStats = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/progress/stats", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load progress stats");
      }

      const data = await response.json();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load progress");
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshProgress = async () => {
    await refreshProgress();
    await loadProgressStats();
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-200 rounded-lg" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-64 bg-gray-200 rounded-lg" />
          <div className="h-64 bg-gray-200 rounded-lg" />
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <Card className="p-6 text-center">
        <p className="text-red-600 mb-4">
          {error || "Failed to load progress"}
        </p>
        <button
          onClick={loadProgressStats}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Try Again
        </button>
      </Card>
    );
  }

  const aiTierColor =
    {
      local: "bg-gray-500",
      haiku: "bg-yellow-500",
      sonnet: "bg-purple-500",
    }[stats.overview.ai_tier] || "bg-gray-500";

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center space-x-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            <div>
              <p className="text-sm text-gray-600">Total Points</p>
              <p className="text-2xl font-bold">
                {stats.overview.total_points.toLocaleString()}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-2">
            <Target className="h-5 w-5 text-green-500" />
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-2xl font-bold">
                {stats.overview.challenges_completed}/
                {stats.overview.challenges_attempted}
              </p>
              <p className="text-xs text-gray-500">
                {stats.overview.completion_rate.toFixed(1)}% success rate
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-orange-500" />
            <div>
              <p className="text-sm text-gray-600">Current Streak</p>
              <p className="text-2xl font-bold">
                {stats.streaks.current_streak}
              </p>
              <p className="text-xs text-gray-500">
                Best: {stats.streaks.longest_streak} days
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-2">
            <BookOpen className="h-5 w-5 text-blue-500" />
            <div>
              <p className="text-sm text-gray-600">AI Tier</p>
              <Badge className={`${aiTierColor} text-white`}>
                {stats.overview.ai_tier.toUpperCase()}
              </Badge>
            </div>
          </div>
        </Card>
      </div>

      {/* Detailed Progress Tabs */}
      <Tabs defaultValue="tracks" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="tracks">Track Progress</TabsTrigger>
          <TabsTrigger value="achievements">Achievements</TabsTrigger>
          <TabsTrigger value="certificates">Certificates</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="tracks" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <TrackProgress trackName="web" trackData={stats.tracks.web} />
            <TrackProgress trackName="data" trackData={stats.tracks.data} />
            <TrackProgress trackName="cloud" trackData={stats.tracks.cloud} />
          </div>
        </TabsContent>

        <TabsContent value="achievements" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Award className="h-5 w-5 mr-2" />
                Achievement Progress
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Achievements Earned</span>
                    <span>
                      {stats.achievements.earned}/{stats.achievements.total}
                    </span>
                  </div>
                  <Progress
                    value={
                      (stats.achievements.earned / stats.achievements.total) *
                      100
                    }
                    className="h-2"
                  />
                </div>
                {stats.achievements.recent.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">
                      Recent Achievements:
                    </p>
                    <div className="space-y-2">
                      {stats.achievements.recent.map((achievement, index) => (
                        <div
                          key={index}
                          className="flex items-center space-x-2"
                        >
                          <Badge variant="secondary" className="text-xs">
                            {achievement.title}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>

            <StreakDisplay
              currentStreak={stats.streaks.current_streak}
              longestStreak={stats.streaks.longest_streak}
              streakActive={stats.streaks.streak_active}
              daysUntilReset={stats.streaks.days_until_reset}
            />
          </div>
          <AchievementsList />
        </TabsContent>

        <TabsContent value="certificates">
          <CertificatesList />
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Activity Summary
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Last Activity:</span>
                  <span className="text-sm font-medium">
                    {stats.activity.last_activity
                      ? new Date(
                          stats.activity.last_activity
                        ).toLocaleDateString()
                      : "Never"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">AI Requests:</span>
                  <span className="text-sm font-medium">
                    {stats.activity.ai_requests_total.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Success Rate:</span>
                  <span className="text-sm font-medium">
                    {stats.overview.completion_rate.toFixed(1)}%
                  </span>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={handleRefreshProgress}
                  className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                >
                  Refresh Progress
                </button>
                <button
                  onClick={() =>
                    window.open("/api/v1/certificates/check-awards", "_blank")
                  }
                  className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                >
                  Check New Certificates
                </button>
              </div>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
