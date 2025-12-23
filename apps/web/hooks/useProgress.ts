"use client";

import { useState, useEffect, useCallback } from "react";

// Progress types based on our new API
interface UserProgress {
  user_id: string;
  total_points: number;
  challenges_completed: number;
  challenges_attempted: number;
  completion_rate: number;
  current_streak: number;
  longest_streak: number;
  ai_tier_unlocked: string;
  web_track_completed: number;
  data_track_completed: number;
  cloud_track_completed: number;
  last_activity: string | null;
  achievements_count: number;
  badges_count: number;
}

interface StreakInfo {
  current_streak: number;
  longest_streak: number;
  streak_active: boolean;
  days_until_reset: number;
}

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  name: string;
  avatar_url?: string;
  points: number;
  completed: number;
  streak: number;
  tier: string;
}

interface UseProgressReturn {
  progress: UserProgress | null;
  streaks: StreakInfo | null;
  leaderboard: LeaderboardEntry[];
  isLoading: boolean;
  error: string | null;
  refreshProgress: () => Promise<void>;
  loadStreaks: () => Promise<void>;
  loadLeaderboard: (track?: string, limit?: number) => Promise<void>;
}

export function useProgress(): UseProgressReturn {
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [streaks, setStreaks] = useState<StreakInfo | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get auth token
  const getToken = () => localStorage.getItem("token");

  // Load user progress
  const loadProgress = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch("/api/v1/progress/", {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load progress");
      }

      const data = await response.json();
      setProgress(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load progress");
      console.error("Failed to load progress:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load streak information
  const loadStreaks = useCallback(async () => {
    try {
      const response = await fetch("/api/v1/progress/streaks", {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load streaks");
      }

      const data = await response.json();
      setStreaks(data);
    } catch (err) {
      console.error("Failed to load streaks:", err);
    }
  }, []);

  // Load leaderboard
  const loadLeaderboard = useCallback(
    async (track?: string, limit: number = 50) => {
      try {
        const params = new URLSearchParams();
        if (track) params.append("track", track);
        params.append("limit", limit.toString());

        const response = await fetch(`/api/v1/progress/leaderboard?${params}`, {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to load leaderboard");
        }

        const data = await response.json();
        setLeaderboard(data);
      } catch (err) {
        console.error("Failed to load leaderboard:", err);
      }
    },
    []
  );

  // Refresh progress (force recalculation)
  const refreshProgress = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch("/api/v1/progress/refresh", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to refresh progress");
      }

      // Reload progress after refresh
      await loadProgress();
      await loadStreaks();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to refresh progress"
      );
      console.error("Failed to refresh progress:", err);
    } finally {
      setIsLoading(false);
    }
  }, [loadProgress, loadStreaks]);

  // Load initial data
  useEffect(() => {
    loadProgress();
    loadStreaks();
  }, [loadProgress, loadStreaks]);

  return {
    progress,
    streaks,
    leaderboard,
    isLoading,
    error,
    refreshProgress,
    loadStreaks,
    loadLeaderboard,
  };
}
