"use client";

import { useState, useEffect } from "react";
import { aiClient } from "@/lib/api/ai-client";
import { useAuth } from "@/hooks/useAuth";

interface TokenUsageData {
  daily: {
    usage: {
      local: number;
      haiku: number;
      sonnet: number;
      total: number;
      date: string;
    };
    limit: number;
    remaining: number;
    percentage_used: number;
  };
  tier: string;
  breakdown_by_model: {
    local: number;
    haiku: number;
    sonnet: number;
  };
}

export function TokenUsageDisplay() {
  const { isAuthenticated } = useAuth();
  const [usage, setUsage] = useState<TokenUsageData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setIsLoading(false);
      return;
    }

    const fetchUsage = async () => {
      try {
        setIsLoading(true);
        const usageData = await aiClient.getTokenUsage();
        setUsage(usageData);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load token usage"
        );
        console.error("Token usage fetch failed:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsage();
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-4 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-3"></div>
        <div className="h-2 bg-gray-200 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600 text-sm">
          Error loading token usage: {error}
        </p>
      </div>
    );
  }

  if (!usage) return null;

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return "bg-red-500";
    if (percentage >= 70) return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-semibold text-gray-900 mb-3">Daily Token Usage</h3>

      {/* Usage Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Used: {usage.daily.usage.total.toLocaleString()} tokens</span>
          {usage.daily.limit === -1 ? (
            <span className="text-green-600">Unlimited</span>
          ) : (
            <span>Limit: {usage.daily.limit.toLocaleString()}</span>
          )}
        </div>

        {usage.daily.limit !== -1 && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${getUsageColor(usage.daily.percentage_used)}`}
              style={{
                width: `${Math.min(usage.daily.percentage_used, 100)}%`,
              }}
            ></div>
          </div>
        )}

        {usage.daily.limit !== -1 && (
          <div className="text-xs text-gray-500 mt-1">
            {usage.daily.remaining} tokens remaining (
            {usage.daily.percentage_used}% used)
          </div>
        )}
      </div>

      {/* Tier Badge */}
      <div className="mb-3">
        <span
          className={`inline-block px-2 py-1 rounded text-xs font-medium ${
            usage.tier === "free"
              ? "bg-gray-100 text-gray-700"
              : usage.tier === "pro"
                ? "bg-blue-100 text-blue-700"
                : usage.tier === "team"
                  ? "bg-purple-100 text-purple-700"
                  : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {usage.tier.charAt(0).toUpperCase() + usage.tier.slice(1)} Plan
        </span>
      </div>

      {/* Model Breakdown */}
      {(usage.breakdown_by_model.local > 0 ||
        usage.breakdown_by_model.haiku > 0 ||
        usage.breakdown_by_model.sonnet > 0) && (
        <div className="text-xs text-gray-600">
          <div className="font-medium mb-1">Usage by Model:</div>
          {usage.breakdown_by_model.local > 0 && (
            <div className="flex justify-between">
              <span>Local AI:</span>
              <span>{usage.breakdown_by_model.local.toLocaleString()}</span>
            </div>
          )}
          {usage.breakdown_by_model.haiku > 0 && (
            <div className="flex justify-between">
              <span>Claude Haiku:</span>
              <span>{usage.breakdown_by_model.haiku.toLocaleString()}</span>
            </div>
          )}
          {usage.breakdown_by_model.sonnet > 0 && (
            <div className="flex justify-between">
              <span>Claude Sonnet:</span>
              <span>{usage.breakdown_by_model.sonnet.toLocaleString()}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
