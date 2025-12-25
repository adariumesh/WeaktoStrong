/**
 * Progress API Client for backend communication
 */

import { authClient } from "./auth-client";

interface ProgressSummary {
  user_id: string;
  overall: {
    challenges_completed: number;
    challenges_attempted: number;
    total_points: number;
    completion_rate: number;
    ai_tier: string;
  };
  tracks: {
    web: TrackProgress;
    data: TrackProgress;
    cloud: TrackProgress;
  };
  engagement: {
    current_streak: number;
    longest_streak: number;
    last_activity: string | null;
    ai_requests_total: number;
  };
}

interface TrackProgress {
  completed: number;
  total: number;
  percentage: number;
}

interface RecentCompletion {
  challenge_title: string;
  track: string;
  difficulty: string;
  points_earned: number;
  score: number;
  completed_at: string | null;
  completion_time: number | null;
}

interface LeaderboardEntry {
  rank: number;
  user_name: string;
  avatar_url: string | null;
  total_points: number;
  challenges_completed: number;
  track_completed?: number;
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ProgressClient {
  private baseUrl = API_BASE;

  private async fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    return authClient.fetchWithAuth(endpoint, options);
  }

  /**
   * Get comprehensive progress summary for current user
   */
  async getProgressSummary(): Promise<ProgressSummary> {
    const response = await this.fetchWithAuth("/progress/summary");
    return response.json();
  }

  /**
   * Get user's recent challenge completions
   */
  async getRecentCompletions(limit: number = 10): Promise<RecentCompletion[]> {
    const response = await this.fetchWithAuth(
      `/progress/recent-completions?limit=${limit}`
    );
    const data = await response.json();
    return data.recent_completions;
  }

  /**
   * Get leaderboard of top users
   */
  async getLeaderboard(
    track?: string,
    limit: number = 10
  ): Promise<LeaderboardEntry[]> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (track) params.append("track", track);

    const response = await this.fetchWithAuth(
      `/progress/leaderboard?${params}`
    );
    const data = await response.json();
    return data.users;
  }

  /**
   * Get detailed progress statistics
   */
  async getProgressStats(): Promise<{
    completion_stats: {
      total_completed: number;
      total_attempted: number;
      success_rate: number;
      total_points: number;
    };
    track_breakdown: Array<{
      track: string;
      completed: number;
      total: number;
      percentage: number;
    }>;
    ai_usage: {
      current_tier: string;
      total_requests: number;
      tier_progress: {
        current: number;
        haiku_requirement: number;
        sonnet_requirement: number;
      };
    };
    engagement: {
      current_streak: number;
      longest_streak: number;
      last_activity: string | null;
    };
  }> {
    const response = await this.fetchWithAuth("/progress/stats");
    return response.json();
  }

  /**
   * Manually refresh/recalculate user progress
   */
  async refreshProgress(): Promise<{
    message: string;
    summary: ProgressSummary;
  }> {
    const response = await this.fetchWithAuth("/progress/refresh", {
      method: "POST",
    });
    return response.json();
  }
}

// Global client instance
export const progressClient = new ProgressClient();

// Export types for use in components
export type {
  ProgressSummary,
  TrackProgress,
  RecentCompletion,
  LeaderboardEntry,
};
