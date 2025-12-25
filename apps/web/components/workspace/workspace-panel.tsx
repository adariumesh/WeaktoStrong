"use client";

import { useState } from "react";
import { Play, RotateCcw, Eye, Terminal, Code, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getChallengeById, getTrackByChallenge } from "@/lib/data/challenges";
import { MonacoEditor } from "@/components/editor/monaco-editor-simple";
import { LivePreview } from "@/components/editor/live-preview";
import { Terminal as TerminalComponent } from "@/components/editor/terminal";
import { TestResults } from "@/components/testing/test-results";
import {
  testRunnerAPI,
  type TestResult,
  type ExecutionResult,
} from "@/lib/api/test-runner";

interface WorkspacePanelProps {
  challengeId?: string;
}

export function WorkspacePanel({
  challengeId = "web-001",
}: WorkspacePanelProps) {
  const challenge = getChallengeById(challengeId);
  const track = getTrackByChallenge(challengeId);
  const [code, setCode] = useState(
    challenge?.starterCode || "<!-- Challenge not found -->"
  );
  const [isTestRunning, setIsTestRunning] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [executionResult, setExecutionResult] =
    useState<ExecutionResult | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  // Determine language based on track
  const getLanguageForTrack = () => {
    if (track?.id === "data") return "python";
    if (track?.id === "web") return "html";
    return "javascript"; // Default fallback
  };

  const handleRunTests = async () => {
    setIsTestRunning(true);
    setTestError(null);
    setTestResult(null);
    setExecutionResult(null);

    try {
      const language = getLanguageForTrack();

      // Use unified execution service for all tracks
      const result = await testRunnerAPI.executeChallenge({
        challenge_id: challengeId,
        code: code,
        language: language,
      });

      setExecutionResult(result);

      // Convert ExecutionResult to TestResult for compatibility
      if (result.track_type === "web") {
        // For web challenges, try to also get legacy test results
        try {
          const legacyResult = await testRunnerAPI.runTests({
            challenge_id: challengeId,
            code: code,
            language: language,
          });
          setTestResult(legacyResult);
        } catch {
          // Fallback to execution result
          setTestResult({
            test_id: `exec-${Date.now()}`,
            challenge_id: challengeId,
            success: result.success,
            score: result.score,
            max_score: result.max_score,
            tests: [],
            errors: result.errors.map((err) => ({
              message: err,
              type: "execution",
            })),
            metrics: {},
            execution_time_ms: result.execution_time_ms,
            timestamp: new Date().toISOString(),
          });
        }
      }
    } catch (error) {
      console.error("Challenge execution error:", error);
      setTestError(
        error instanceof Error ? error.message : "Failed to execute challenge"
      );
    } finally {
      setIsTestRunning(false);
    }
  };

  const handleResetCode = () => {
    if (challenge?.starterCode) {
      setCode(challenge.starterCode);
    }
  };

  const getFileName = () => {
    if (track?.id === "data") {
      return "analysis.py";
    }
    if (track?.id === "web") {
      return "index.html";
    }
    return "main.js"; // Default fallback
  };

  return (
    <div className="h-full flex flex-col min-h-0 min-w-0 overflow-hidden">
      {/* Tabs */}
      <Tabs defaultValue="editor" className="flex-1 flex flex-col min-h-0 min-w-0">
        <TabsList className="grid w-full grid-cols-4 rounded-none bg-muted/30 flex-shrink-0 min-w-0">
          <TabsTrigger value="editor" className="flex items-center gap-1 text-xs px-2">
            <Code className="w-4 h-4" />
            Code Editor
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center gap-1 text-xs px-2">
            <Eye className="w-4 h-4" />
            Live Preview
          </TabsTrigger>
          <TabsTrigger value="results" className="flex items-center gap-1 text-xs px-2">
            <Play className="w-4 h-4" />
            Test Results
          </TabsTrigger>
          <TabsTrigger value="terminal" className="flex items-center gap-1 text-xs px-2">
            <Terminal className="w-4 h-4" />
            Terminal
          </TabsTrigger>
        </TabsList>

        <TabsContent value="editor" className="flex-1 mt-0 min-h-0 min-w-0 overflow-hidden">
          <div className="h-full min-h-0 min-w-0">
            <MonacoEditor
              value={code}
              onChange={setCode}
              language={getLanguageForTrack()}
              fileName={getFileName()}
              onRun={handleRunTests}
              onReset={handleResetCode}
            />
          </div>
        </TabsContent>

        <TabsContent value="preview" className="flex-1 mt-0 min-h-0 min-w-0 overflow-hidden">
          {track?.id === "web" ? (
            <LivePreview code={code} title="Challenge Preview" />
          ) : (
            <div className="h-full p-4 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <Code className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>
                  Live preview not available for {track?.name || "this"}{" "}
                  challenges
                </p>
                <p className="text-sm">
                  Run your code to see results in the Test Results tab
                </p>
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="results" className="flex-1 mt-0 min-h-0 min-w-0 overflow-hidden">
          <div className="h-full p-4 overflow-auto">
            {testError ? (
              <div className="text-center py-8">
                <div className="text-red-600 mb-4">
                  <Terminal className="w-12 h-12 mx-auto mb-2" />
                  <p className="font-medium">Test Execution Failed</p>
                  <p className="text-sm">{testError}</p>
                </div>
                <Button onClick={handleRunTests} disabled={isTestRunning}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Retry Tests
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Show unified execution results for all tracks */}
                {executionResult && (
                  <div className="p-4 border rounded-lg">
                    <h3 className="font-semibold mb-2">
                      Execution Results ({executionResult.track_type})
                    </h3>
                    <div
                      className={`p-3 rounded ${executionResult.success ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}
                    >
                      <p
                        className={`font-medium ${executionResult.success ? "text-green-700" : "text-red-700"}`}
                      >
                        {executionResult.success ? "✅ Success" : "❌ Failed"} -
                        Score: {executionResult.score}/
                        {executionResult.max_score}
                      </p>
                      <p className="text-sm text-gray-600">
                        Execution time: {executionResult.execution_time_ms}ms
                      </p>

                      {executionResult.output && (
                        <div className="mt-2">
                          <p className="font-medium text-sm">Output:</p>
                          <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-auto max-h-32">
                            {executionResult.output}
                          </pre>
                        </div>
                      )}

                      {executionResult.errors.length > 0 && (
                        <div className="mt-2">
                          <p className="font-medium text-sm text-red-700">
                            Errors:
                          </p>
                          <ul className="text-sm text-red-600 mt-1">
                            {executionResult.errors.map((error, idx) => (
                              <li key={idx} className="list-disc list-inside">
                                {error}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {executionResult.validation_results.length > 0 && (
                        <div className="mt-2">
                          <p className="font-medium text-sm">
                            Validation Results:
                          </p>
                          <div className="text-xs mt-1 space-y-1">
                            {executionResult.validation_results.map(
                              (validation, idx) => (
                                <div
                                  key={idx}
                                  className={`p-2 rounded ${validation.passed ? "bg-green-100" : "bg-red-100"}`}
                                >
                                  {validation.name || `Validation ${idx + 1}`}:{" "}
                                  {validation.passed ? "PASS" : "FAIL"}
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}

                      {executionResult.insights_found !== undefined && (
                        <p
                          className={`text-sm mt-2 ${executionResult.insights_found ? "text-green-600" : "text-gray-600"}`}
                        >
                          Insights discovered:{" "}
                          {executionResult.insights_found ? "Yes" : "No"}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Legacy test results for web track */}
                <TestResults
                  result={testResult || undefined}
                  isLoading={isTestRunning}
                  onRerun={handleRunTests}
                />
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="terminal" className="flex-1 mt-0 min-h-0 min-w-0 overflow-hidden">
          <TerminalComponent
            onRunTests={handleRunTests}
            isRunning={isTestRunning}
            challengeId={challengeId}
            code={code}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
