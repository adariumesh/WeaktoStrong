/**
 * Test Status Component
 * Shows real-time status of test runner service and test execution
 */

"use client";

import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
  Server,
  Container,
  Zap,
} from "lucide-react";
import { testRunnerAPI } from "@/lib/api/test-runner";

interface TestStatusProps {
  onRefresh?: () => void;
  showDetails?: boolean;
}

interface ServiceStatus {
  status: string;
  service: string;
  stats?: {
    active_containers: number;
    total_containers: number;
    docker_info?: any;
  };
  error?: string;
  timestamp: string;
}

export function TestStatus({
  onRefresh,
  showDetails = false,
}: TestStatusProps) {
  const [status, setStatus] = useState<ServiceStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkStatus = async () => {
    setIsLoading(true);
    try {
      const statusData = await testRunnerAPI.getTestRunnerStatus();
      setStatus(statusData);
      setLastCheck(new Date());
    } catch (error) {
      console.error("Failed to check test runner status:", error);
      setStatus({
        status: "error",
        service: "test-runner",
        error: error instanceof Error ? error.message : "Failed to connect",
        timestamp: new Date().toISOString(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();

    // Auto-refresh every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "healthy":
      case "running":
      case "ready":
        return "text-green-600";
      case "warning":
      case "degraded":
        return "text-yellow-600";
      case "error":
      case "failed":
      case "down":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "healthy":
      case "running":
      case "ready":
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case "warning":
      case "degraded":
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case "error":
      case "failed":
      case "down":
        return <XCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "healthy":
      case "running":
      case "ready":
        return "default";
      case "warning":
      case "degraded":
        return "secondary";
      case "error":
      case "failed":
      case "down":
        return "destructive";
      default:
        return "outline";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return "Unknown";
    }
  };

  if (!showDetails) {
    // Compact status indicator
    return (
      <div className="flex items-center gap-2">
        {isLoading ? (
          <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
        ) : (
          status && getStatusIcon(status.status)
        )}
        <Badge
          variant={status ? getStatusBadgeVariant(status.status) : "outline"}
        >
          {isLoading ? "Checking..." : status?.status || "Unknown"}
        </Badge>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => {
            checkStatus();
            onRefresh?.();
          }}
          disabled={isLoading}
          className="h-6 px-2"
        >
          <RefreshCw className={`w-3 h-3 ${isLoading ? "animate-spin" : ""}`} />
        </Button>
      </div>
    );
  }

  // Detailed status card
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Server className="w-4 h-4" />
            Test Runner Status
          </CardTitle>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              checkStatus();
              onRefresh?.();
            }}
            disabled={isLoading}
          >
            <RefreshCw
              className={`w-4 h-4 mr-1 ${isLoading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {status ? (
          <div className="space-y-4">
            {/* Main Status */}
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                {getStatusIcon(status.status)}
                <div>
                  <div className="font-medium">Service Status</div>
                  <div className={`text-sm ${getStatusColor(status.status)}`}>
                    {status.status.charAt(0).toUpperCase() +
                      status.status.slice(1)}
                  </div>
                </div>
              </div>

              {status.error && (
                <div className="text-xs text-red-600 max-w-xs text-right">
                  {status.error}
                </div>
              )}
            </div>

            {/* Container Stats */}
            {status.stats && (
              <div className="grid grid-cols-2 gap-3">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <Container className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">
                      Active
                    </span>
                  </div>
                  <div className="text-lg font-bold text-blue-600">
                    {status.stats.active_containers || 0}
                  </div>
                </div>

                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <Zap className="w-4 h-4 text-purple-600" />
                    <span className="text-sm font-medium text-purple-800">
                      Total
                    </span>
                  </div>
                  <div className="text-lg font-bold text-purple-600">
                    {status.stats.total_containers || 0}
                  </div>
                </div>
              </div>
            )}

            {/* Last Check */}
            <div className="text-xs text-gray-500 text-center">
              Last updated:{" "}
              {lastCheck ? lastCheck.toLocaleTimeString() : "Never"}
            </div>
          </div>
        ) : (
          <div className="text-center py-6">
            <div className="text-gray-400 mb-2">
              {isLoading ? (
                <RefreshCw className="w-8 h-8 animate-spin mx-auto" />
              ) : (
                <XCircle className="w-8 h-8 mx-auto" />
              )}
            </div>
            <p className="text-sm text-gray-600">
              {isLoading
                ? "Checking service status..."
                : "Unable to connect to test runner"}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
