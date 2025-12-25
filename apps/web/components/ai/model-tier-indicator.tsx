"use client";

import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Crown, Cpu, Zap, Lock, Star } from "lucide-react";
import type { ModelTier, TierProgress } from "@/types/ai";

interface ModelTierIndicatorProps {
  tier: ModelTier;
  progress: TierProgress;
  compact?: boolean;
  showProgress?: boolean;
}

const TIER_CONFIG = {
  local: {
    icon: Cpu,
    color: "bg-gray-500",
    textColor: "text-gray-700",
    label: "Local AI",
    description: "Llama 3.2 8B",
  },
  haiku: {
    icon: Zap,
    color: "bg-blue-500",
    textColor: "text-blue-700",
    label: "Claude Haiku",
    description: "Fast & Smart",
  },
  sonnet: {
    icon: Crown,
    color: "bg-purple-500",
    textColor: "text-purple-700",
    label: "Claude Sonnet",
    description: "Advanced AI",
  },
} as const;

export function ModelTierIndicator({
  tier,
  progress,
  compact = false,
  showProgress = true,
}: ModelTierIndicatorProps) {
  const config = TIER_CONFIG[tier];
  const IconComponent = config.icon;

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <Badge variant="secondary" className="flex items-center gap-1">
          <IconComponent className="w-3 h-3" />
          {config.label}
        </Badge>
        {showProgress && progress.nextTier && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <span>
              {progress.progress}/{progress.required}
            </span>
            <div className="w-12 h-1 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full ${config.color} transition-all duration-300`}
                style={{ width: `${Math.min(100, progress.percentage)}%` }}
              />
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <Card className="w-full">
      <CardContent className="p-4">
        {/* Current Tier */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 ${config.color} rounded-lg flex items-center justify-center text-white`}
            >
              <IconComponent className="w-5 h-5" />
            </div>
            <div>
              <h3 className={`font-semibold ${config.textColor}`}>
                {config.label}
              </h3>
              <p className="text-sm text-gray-600">{config.description}</p>
            </div>
          </div>
          <Badge
            variant="secondary"
            className={`${config.textColor} border-current`}
          >
            Current
          </Badge>
        </div>

        {/* Progress to Next Tier */}
        {showProgress && progress.nextTier && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">
                Progress to{" "}
                {progress.nextTier.charAt(0).toUpperCase() +
                  progress.nextTier.slice(1)}
              </span>
              <span className="font-medium">
                {progress.progress}/{progress.required} challenges
              </span>
            </div>

            <Progress
              value={Math.min(100, progress.percentage)}
              className="h-2"
            />

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{Math.round(progress.percentage)}% complete</span>
              {progress.requiresPro && (
                <div className="flex items-center gap-1 text-orange-600">
                  <Star className="w-3 h-3" />
                  Pro required
                </div>
              )}
            </div>
          </div>
        )}

        {/* Next Tier Preview */}
        {progress.nextTier && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Lock className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                Unlock {TIER_CONFIG[progress.nextTier as ModelTier]?.label}
              </span>
            </div>
            <p className="text-xs text-gray-600">
              Complete {progress.required - progress.progress} more challenges
              {progress.requiresPro ? " and upgrade to Pro" : ""}
            </p>
          </div>
        )}

        {/* Completed Tier */}
        {!progress.nextTier && (
          <div className="mt-4 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
            <div className="flex items-center gap-2 text-purple-700">
              <Crown className="w-4 h-4" />
              <span className="text-sm font-medium">
                Maximum tier unlocked!
              </span>
            </div>
            <p className="text-xs text-purple-600 mt-1">
              You have access to the most advanced AI models.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
