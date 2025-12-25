"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Play,
  Square,
  Trash2,
  Download,
  CheckCircle,
  XCircle,
  AlertCircle,
  Terminal as TerminalIcon,
} from "lucide-react";
import { getChallengeById } from "@/lib/data/challenges";
import { testRunnerAPI } from "@/lib/api/test-runner";

interface TerminalLog {
  id: string;
  timestamp: Date;
  type: "info" | "success" | "warning" | "error" | "command";
  message: string;
  details?: string;
}

interface TerminalProps {
  onRunTests?: () => Promise<void>;
  isRunning?: boolean;
  autoScroll?: boolean;
  challengeId?: string;
  code?: string;
}

export function Terminal({
  onRunTests,
  isRunning = false,
  autoScroll = true,
  challengeId = "web-001",
  code = "",
}: TerminalProps) {
  const [logs, setLogs] = useState<TerminalLog[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, autoScroll]);

  const addLog = (
    type: TerminalLog["type"],
    message: string,
    details?: string
  ) => {
    const newLog: TerminalLog = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      type,
      message,
      details,
    };
    setLogs((prev) => [...prev, newLog]);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const downloadLogs = () => {
    const logText = logs
      .map(
        (log) =>
          `[${log.timestamp.toISOString()}] ${log.type.toUpperCase()}: ${log.message}${log.details ? "\n" + log.details : ""}`
      )
      .join("\n");

    const blob = new Blob([logText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `test-logs-${new Date().toISOString().split("T")[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const runRealTests = async () => {
    if (isRunning) return;

    setIsConnected(true);
    addLog("command", "$ Running tests...");
    addLog("info", "Initializing test environment");

    const challenge = getChallengeById(challengeId);
    if (!challenge) {
      addLog("error", "Challenge not found");
      setIsConnected(false);
      return;
    }

    try {
      addLog("info", `Running tests for: ${challenge.title}`);
      addLog("info", "Spinning up Docker container...");

      // Submit and run tests using our API
      const result = await testRunnerAPI.runTests({
        challenge_id: challengeId,
        code,
        language: "html",
      });

      // Display test results
      addLog("info", "Test execution completed");
      addLog("info", `Execution time: ${result.execution_time_ms}ms`);

      // Show individual test results
      for (const test of result.tests) {
        if (test.passed) {
          addLog(
            "success",
            `✓ ${test.name}`,
            `${test.points} points earned - ${test.description}`
          );
        } else {
          addLog(
            "error",
            `✗ ${test.name}`,
            test.error || `Failed: ${test.description}`
          );
        }
      }

      // Show errors if any
      if (result.errors.length > 0) {
        addLog("warning", "Execution Errors:");
        for (const error of result.errors) {
          addLog("error", `${error.type.toUpperCase()}: ${error.message}`);
        }
      }

      // Show metrics if available
      if (result.metrics && Object.keys(result.metrics).length > 0) {
        addLog("info", "Performance Metrics:");
        if (result.metrics.loadTime)
          addLog("info", `Page load time: ${result.metrics.loadTime}ms`);
        if (result.metrics.elements)
          addLog("info", `HTML elements: ${result.metrics.elements}`);
        if (result.metrics.stylesheets)
          addLog("info", `Stylesheets: ${result.metrics.stylesheets}`);
        if (result.metrics.scripts)
          addLog("info", `Scripts: ${result.metrics.scripts}`);
      }

      // Display summary
      addLog("info", "Test Summary:");
      const passed = result.tests.filter((r) => r.passed).length;
      const total = result.tests.length;

      if (result.success && passed === total) {
        addLog("success", `🎉 All tests passed! (${passed}/${total})`);
        addLog(
          "success",
          `Final Score: ${result.score}/${result.max_score} points`
        );
      } else {
        addLog("warning", `Passed: ${passed}/${total} tests`);
        addLog("info", `Score: ${result.score}/${result.max_score} points`);
      }

      if (onRunTests) {
        await onRunTests();
      }
    } catch (error) {
      addLog(
        "error",
        "Test execution failed",
        error instanceof Error ? error.message : "Unknown error"
      );
      addLog("error", "Please check your code and try again");
    } finally {
      setIsConnected(false);
    }
  };

  const handleRunTests = () => {
    runRealTests();
  };

  const getLogIcon = (type: TerminalLog["type"]) => {
    switch (type) {
      case "success":
        return <CheckCircle size={14} className="text-green-500" />;
      case "error":
        return <XCircle size={14} className="text-red-500" />;
      case "warning":
        return <AlertCircle size={14} className="text-yellow-500" />;
      case "command":
        return <TerminalIcon size={14} className="text-blue-400" />;
      case "info":
      default:
        return <div className="w-3.5 h-3.5 rounded-full bg-gray-400" />;
    }
  };

  const getLogColor = (type: TerminalLog["type"]) => {
    switch (type) {
      case "success":
        return "text-green-400";
      case "error":
        return "text-red-400";
      case "warning":
        return "text-yellow-400";
      case "command":
        return "text-blue-400";
      case "info":
      default:
        return "text-gray-300";
    }
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-gray-100 rounded-lg overflow-hidden">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <TerminalIcon size={16} className="text-gray-400" />
          <span className="text-sm font-medium text-gray-300">
            Test Terminal
          </span>

          <div className="flex items-center gap-1 ml-2">
            <div
              className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`}
            />
            <span className="text-xs text-gray-500">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            onClick={handleRunTests}
            disabled={isRunning}
            className="h-6 px-2 bg-green-600 hover:bg-green-700 text-white"
          >
            {isRunning ? (
              <>
                <Square size={12} className="mr-1" />
                Running...
              </>
            ) : (
              <>
                <Play size={12} className="mr-1" />
                Run Tests
              </>
            )}
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={downloadLogs}
            className="h-6 px-2 text-gray-400 hover:text-gray-200"
            disabled={logs.length === 0}
          >
            <Download size={12} />
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={clearLogs}
            className="h-6 px-2 text-gray-400 hover:text-gray-200"
            disabled={logs.length === 0}
          >
            <Trash2 size={12} />
          </Button>
        </div>
      </div>

      {/* Terminal Content */}
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-1 font-mono text-sm">
          {logs.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              <TerminalIcon size={32} className="mx-auto mb-2 opacity-50" />
              <p>No test output yet</p>
              <p className="text-xs mt-1">
                Click "Run Tests" to start testing your solution
              </p>
            </div>
          ) : (
            logs.map((log) => (
              <div key={log.id} className="flex items-start gap-2 py-0.5">
                <span className="text-xs text-gray-500 mt-0.5 w-16 flex-shrink-0">
                  {formatTimestamp(log.timestamp)}
                </span>

                <div className="flex items-start gap-2 flex-1">
                  <div className="mt-0.5 flex-shrink-0">
                    {getLogIcon(log.type)}
                  </div>

                  <div className="flex-1">
                    <div className={getLogColor(log.type)}>{log.message}</div>
                    {log.details && (
                      <div className="text-gray-400 text-xs mt-1 ml-4 opacity-80">
                        {log.details}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}

          {isRunning && (
            <div className="flex items-center gap-2 py-1">
              <span className="text-xs text-gray-500 w-16">
                {formatTimestamp(new Date())}
              </span>
              <div className="w-3 h-3 border border-blue-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-blue-400">Running tests...</span>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Terminal Footer */}
      <div className="flex items-center justify-between px-3 py-1 bg-gray-800 border-t border-gray-700 text-xs">
        <div className="flex items-center gap-4 text-gray-500">
          <span>{logs.length} log entries</span>
          {logs.length > 0 && (
            <span>
              Latest:{" "}
              {formatTimestamp(logs[logs.length - 1]?.timestamp || new Date())}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className="text-xs bg-gray-700 border-gray-600 text-gray-300"
          >
            Test Environment: Docker
          </Badge>
        </div>
      </div>
    </div>
  );
}
