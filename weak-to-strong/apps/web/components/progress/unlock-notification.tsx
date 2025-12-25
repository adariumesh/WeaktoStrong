/**
 * Unlock Notification Component
 * Shows notifications for new achievements, certificates, and AI tier unlocks
 */

"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { X, Star, Trophy, Zap, BookOpen } from "lucide-react";

interface UnlockNotification {
  id: string;
  type: "achievement" | "certificate" | "ai_tier" | "streak_milestone";
  title: string;
  description: string;
  icon: string;
  level?: string;
  timestamp: string;
}

interface UnlockNotificationProps {
  notifications: UnlockNotification[];
  onDismiss: (id: string) => void;
  onDismissAll: () => void;
}

export function UnlockNotification({
  notifications,
  onDismiss,
  onDismissAll,
}: UnlockNotificationProps) {
  const [visible, setVisible] = useState<string[]>([]);

  useEffect(() => {
    // Show notifications one by one with delay
    notifications.forEach((notification, index) => {
      setTimeout(() => {
        setVisible((prev) => [...prev, notification.id]);
      }, index * 500);
    });

    // Auto-dismiss after 10 seconds
    const timer = setTimeout(() => {
      onDismissAll();
    }, 10000);

    return () => clearTimeout(timer);
  }, [notifications, onDismissAll]);

  if (notifications.length === 0) {
    return null;
  }

  const getNotificationStyle = (type: string) => {
    switch (type) {
      case "achievement":
        return "bg-yellow-50 border-yellow-200 text-yellow-800";
      case "certificate":
        return "bg-green-50 border-green-200 text-green-800";
      case "ai_tier":
        return "bg-purple-50 border-purple-200 text-purple-800";
      case "streak_milestone":
        return "bg-orange-50 border-orange-200 text-orange-800";
      default:
        return "bg-blue-50 border-blue-200 text-blue-800";
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "achievement":
        return <Star className="h-5 w-5" />;
      case "certificate":
        return <Trophy className="h-5 w-5" />;
      case "ai_tier":
        return <BookOpen className="h-5 w-5" />;
      case "streak_milestone":
        return <Zap className="h-5 w-5" />;
      default:
        return <Star className="h-5 w-5" />;
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification, index) => (
        <Card
          key={notification.id}
          className={`p-4 shadow-lg border-l-4 transform transition-all duration-500 ${
            visible.includes(notification.id)
              ? "translate-x-0 opacity-100"
              : "translate-x-full opacity-0"
          } ${getNotificationStyle(notification.type)}`}
          style={{
            animationDelay: `${index * 0.5}s`,
          }}
        >
          <div className="flex items-start space-x-3">
            {/* Icon */}
            <div className="flex-shrink-0 mt-0.5">
              {notification.icon ? (
                <span className="text-2xl">{notification.icon}</span>
              ) : (
                getNotificationIcon(notification.type)
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <p className="text-sm font-medium">{notification.title}</p>
                {notification.level && (
                  <Badge variant="outline" className="text-xs">
                    {notification.level}
                  </Badge>
                )}
              </div>

              <p className="text-sm opacity-90">{notification.description}</p>

              <p className="text-xs opacity-75 mt-2">
                {new Date(notification.timestamp).toLocaleTimeString()}
              </p>
            </div>

            {/* Dismiss Button */}
            <button
              onClick={() => onDismiss(notification.id)}
              className="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Progress Bar */}
          <div className="mt-3 bg-black/10 h-1 rounded-full overflow-hidden">
            <div
              className="h-full bg-current transition-all duration-[10000ms] ease-linear"
              style={{
                width: visible.includes(notification.id) ? "0%" : "100%",
              }}
            />
          </div>
        </Card>
      ))}

      {/* Dismiss All Button */}
      {notifications.length > 1 && (
        <div className="text-center">
          <button
            onClick={onDismissAll}
            className="text-xs text-gray-600 hover:text-gray-800 bg-white/80 px-2 py-1 rounded shadow-sm"
          >
            Dismiss All ({notifications.length})
          </button>
        </div>
      )}
    </div>
  );
}

// Hook to manage unlock notifications
export function useUnlockNotifications() {
  const [notifications, setNotifications] = useState<UnlockNotification[]>([]);

  const addNotification = (
    notification: Omit<UnlockNotification, "id" | "timestamp">
  ) => {
    const newNotification: UnlockNotification = {
      ...notification,
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
    };

    setNotifications((prev) => [...prev, newNotification]);
  };

  const dismissNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const dismissAll = () => {
    setNotifications([]);
  };

  const checkForNewUnlocks = async () => {
    try {
      // Check for new certificates
      const certResponse = await fetch("/api/v1/certificates/check-awards", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (certResponse.ok) {
        const certData = await certResponse.json();

        certData.certificates?.forEach((cert: any) => {
          addNotification({
            type: "certificate",
            title: "🏆 New Certificate!",
            description: `You've earned: ${cert.title}`,
            icon: "🏆",
            level: cert.achievement,
          });
        });
      }

      // Check for progress updates that might unlock new features
      const progressResponse = await fetch("/api/v1/progress/stats", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (progressResponse.ok) {
        const progressData = await progressResponse.json();

        // Check for AI tier upgrades
        const currentTier = localStorage.getItem("ai_tier");
        if (currentTier !== progressData.overview.ai_tier) {
          localStorage.setItem("ai_tier", progressData.overview.ai_tier);

          if (progressData.overview.ai_tier === "haiku") {
            addNotification({
              type: "ai_tier",
              title: "🤖 AI Upgrade!",
              description: "You've unlocked Claude Haiku access!",
              icon: "🤖",
              level: "Haiku",
            });
          } else if (progressData.overview.ai_tier === "sonnet") {
            addNotification({
              type: "ai_tier",
              title: "🧠 AI Upgrade!",
              description: "You've unlocked Claude Sonnet access!",
              icon: "🧠",
              level: "Sonnet",
            });
          }
        }

        // Check for streak milestones
        const currentStreak = progressData.streaks.current_streak;
        if ([7, 14, 30, 50, 100].includes(currentStreak)) {
          const lastStreakNotification = parseInt(
            localStorage.getItem("last_streak_notification") || "0"
          );
          if (currentStreak > lastStreakNotification) {
            localStorage.setItem(
              "last_streak_notification",
              currentStreak.toString()
            );

            addNotification({
              type: "streak_milestone",
              title: "🔥 Streak Milestone!",
              description: `Amazing! You've reached a ${currentStreak}-day streak!`,
              icon: "🔥",
              level: `${currentStreak} days`,
            });
          }
        }
      }
    } catch (error) {
      console.error("Error checking for unlocks:", error);
    }
  };

  return {
    notifications,
    addNotification,
    dismissNotification,
    dismissAll,
    checkForNewUnlocks,
  };
}
