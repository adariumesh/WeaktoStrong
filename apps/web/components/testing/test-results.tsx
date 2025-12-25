"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Play,
  RefreshCw,
  TrendingUp,
  Zap,
} from "lucide-react";

interface TestCase {
  name: string;
  description: string;
  passed: boolean;
  points: number;
  error?: string;
}

interface TestResult {
  test_id: string;
  challenge_id: string;
  success: boolean;
  score: number;
  max_score: number;
  tests: TestCase[];
  errors: Array<{
    message: string;
    type: string;
  }>;
  metrics: {
    loadTime?: number;
    elements?: number;
    scripts?: number;
    stylesheets?: number;
  };
  execution_time_ms: number;
  timestamp: string;
}

interface TestResultsProps {
  result?: TestResult;
  isLoading?: boolean;
  onRerun?: () => void;
}

export function TestResults({
  result,
  isLoading = false,
  onRerun,
}: TestResultsProps) {
  const [expandedTest, setExpandedTest] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 animate-spin" />
                Running Tests...
              </CardTitle>
              <Badge variant="outline">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2"></div>
                In Progress
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full animate-pulse"
                  style={{ width: "45%" }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">
                Validating HTML structure, CSS styling, and responsive design...
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="text-center py-8">
        <Play className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">Click "Run Tests" to see your results</p>
      </div>
    );
  }

  const scorePercentage =
    result.max_score > 0 ? (result.score / result.max_score) * 100 : 0;
  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return "text-green-600";
    if (percentage >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBadgeVariant = (percentage: number) => {
    if (percentage >= 80) return "default";
    if (percentage >= 60) return "secondary";
    return "destructive";
  };

  return (
    <div className="space-y-4">
      {/* Overall Results */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {result.success ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600" />
              )}
              Test Results
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={getScoreBadgeVariant(scorePercentage)}>
                {result.score}/{result.max_score} Passed
              </Badge>
              {onRerun && (
                <Button size="sm" variant="outline" onClick={onRerun}>
                  <RefreshCw className="w-4 h-4 mr-1" />
                  Rerun
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div
                className={`text-2xl font-bold ${getScoreColor(scorePercentage)}`}
              >
                {scorePercentage.toFixed(0)}%
              </div>
              <div className="text-sm text-gray-600">Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {result.execution_time_ms}ms
              </div>
              <div className="text-sm text-gray-600">Execution Time</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {result.tests.length}
              </div>
              <div className="text-sm text-gray-600">Tests Run</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${
                scorePercentage >= 80
                  ? "bg-green-600"
                  : scorePercentage >= 60
                    ? "bg-yellow-600"
                    : "bg-red-600"
              }`}
              style={{ width: `${scorePercentage}%` }}
            ></div>
          </div>

          {/* Metrics */}
          {result.metrics && Object.keys(result.metrics).length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4">
              {result.metrics.elements && (
                <div className="text-center p-2 bg-gray-50 rounded">
                  <div className="text-sm font-semibold">
                    {result.metrics.elements}
                  </div>
                  <div className="text-xs text-gray-600">Elements</div>
                </div>
              )}
              {result.metrics.stylesheets !== undefined && (
                <div className="text-center p-2 bg-gray-50 rounded">
                  <div className="text-sm font-semibold">
                    {result.metrics.stylesheets}
                  </div>
                  <div className="text-xs text-gray-600">Stylesheets</div>
                </div>
              )}
              {result.metrics.scripts !== undefined && (
                <div className="text-center p-2 bg-gray-50 rounded">
                  <div className="text-sm font-semibold">
                    {result.metrics.scripts}
                  </div>
                  <div className="text-xs text-gray-600">Scripts</div>
                </div>
              )}
              {result.metrics.loadTime && (
                <div className="text-center p-2 bg-gray-50 rounded">
                  <div className="text-sm font-semibold">
                    {result.metrics.loadTime.toFixed(0)}ms
                  </div>
                  <div className="text-xs text-gray-600">Load Time</div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Individual Test Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Test Details
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-64">
            <div className="space-y-2">
              {result.tests.map((test, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-3 cursor-pointer transition-all ${
                    test.passed
                      ? "border-green-200 bg-green-50 hover:bg-green-100"
                      : "border-red-200 bg-red-50 hover:bg-red-100"
                  } ${expandedTest === test.name ? "ring-2 ring-blue-500" : ""}`}
                  onClick={() =>
                    setExpandedTest(
                      expandedTest === test.name ? null : test.name
                    )
                  }
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {test.passed ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-600" />
                      )}
                      <span className="font-medium">{test.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {test.points} pt{test.points !== 1 ? "s" : ""}
                      </Badge>
                      <Badge
                        variant={test.passed ? "default" : "destructive"}
                        className="text-xs"
                      >
                        {test.passed ? "PASS" : "FAIL"}
                      </Badge>
                    </div>
                  </div>

                  {expandedTest === test.name && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-sm text-gray-700 mb-2">
                        {test.description}
                      </p>
                      {test.error && (
                        <div className="bg-red-100 border border-red-300 rounded p-2">
                          <p className="text-sm text-red-700">{test.error}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Errors */}
      {result.errors && result.errors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              Errors & Issues
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {result.errors.map((error, index) => (
                <div
                  key={index}
                  className="border border-red-200 bg-red-50 rounded p-3"
                >
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="text-sm font-medium text-red-800">
                        {error.type.toUpperCase()} Error
                      </div>
                      <div className="text-sm text-red-700 mt-1">
                        {error.message}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Message */}
      {result.success && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-2" />
              <h3 className="text-lg font-semibold text-green-800">
                Perfect Score! 🎉
              </h3>
              <p className="text-green-700">
                Your solution passes all tests. Great work on following web
                development best practices!
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
