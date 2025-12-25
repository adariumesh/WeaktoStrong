"use client";

import { useSession, signOut } from "next-auth/react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProgressDashboard } from "@/components/progress/progress-dashboard";
import {
  UnlockNotification,
  useUnlockNotifications,
} from "@/components/progress/unlock-notification";

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { notifications, dismissNotification, dismissAll, checkForNewUnlocks } =
    useUnlockNotifications();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin");
    }
  }, [status, router]);

  useEffect(() => {
    // Check for new unlocks when user visits dashboard
    if (session) {
      checkForNewUnlocks();
    }
  }, [session, checkForNewUnlocks]);

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Welcome back, {session.user.name}!</p>
          </div>
          <div className="flex items-center space-x-4">
            <nav className="hidden md:flex space-x-6">
              <a
                href="/challenges"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Challenges
              </a>
              <a
                href="/leaderboard"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Leaderboard
              </a>
              <a
                href="/profile"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Profile
              </a>
            </nav>
            <div className="flex items-center space-x-3">
              <img
                className="h-8 w-8 rounded-full border-2 border-gray-200"
                src={
                  session.user.avatar_url ||
                  `https://ui-avatars.com/api/?name=${encodeURIComponent(session.user.name)}&background=6366f1&color=fff`
                }
                alt={session.user.name}
              />
              <button
                onClick={() => signOut({ callbackUrl: "/" })}
                className="text-gray-600 hover:text-red-600 transition-colors text-sm"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <ProgressDashboard />
      </main>

      {/* Unlock Notifications */}
      <UnlockNotification
        notifications={notifications}
        onDismiss={dismissNotification}
        onDismissAll={dismissAll}
      />
    </div>
  );
}
