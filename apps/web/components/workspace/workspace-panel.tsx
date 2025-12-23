"use client";

import { useState } from "react";
import { Play, RotateCcw, Eye, Terminal, Code, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getChallengeById } from "@/lib/data/challenges";
import { MonacoEditor } from "@/components/editor/monaco-editor-simple";
import { LivePreview } from "@/components/editor/live-preview";
import { Terminal as TerminalComponent } from "@/components/editor/terminal";
import { TestResults } from "@/components/testing/test-results";
import { testRunnerAPI, type TestResult } from "@/lib/api/test-runner";

interface WorkspacePanelProps {
  challengeId?: string;
}

export function WorkspacePanel({
  challengeId = "web-001",
}: WorkspacePanelProps) {
  const challenge = getChallengeById(challengeId);
  const [code, setCode] = useState(
    challenge?.starterCode || "<!-- Challenge not found -->"
  );
  const [isTestRunning, setIsTestRunning] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  const handleRunTests = async () => {
    setIsTestRunning(true);
    setTestError(null);
    setTestResult(null);

    try {
      // Call backend API to run tests
      const result = await testRunnerAPI.runTests({
        challenge_id: challengeId,
        code: code,
        language: "html",
      });

      setTestResult(result);
    } catch (error) {
      console.error("Test execution error:", error);
      setTestError(
        error instanceof Error ? error.message : "Failed to run tests"
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
    if (challengeId?.includes("web")) {
      return "index.html";
    }
    return "main.py";
  };

  return (
    <div className="h-full flex flex-col">
      {/* Tabs */}
      <Tabs defaultValue="editor" className="flex-1 flex flex-col">
        <TabsList className="grid w-full grid-cols-4 rounded-none bg-muted/30">
          <TabsTrigger value="editor" className="flex items-center gap-2">
            <Code className="w-4 h-4" />
            Code Editor
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center gap-2">
            <Eye className="w-4 h-4" />
            Live Preview
          </TabsTrigger>
          <TabsTrigger value="results" className="flex items-center gap-2">
            <Play className="w-4 h-4" />
            Test Results
          </TabsTrigger>
          <TabsTrigger value="terminal" className="flex items-center gap-2">
            <Terminal className="w-4 h-4" />
            Terminal
          </TabsTrigger>
        </TabsList>

        <TabsContent value="editor" className="flex-1 mt-0">
          <MonacoEditor
            value={code}
            onChange={setCode}
            language="html"
            fileName={getFileName()}
            onRun={handleRunTests}
            onReset={handleResetCode}
          />
        </TabsContent>

        <TabsContent value="preview" className="flex-1 mt-0">
          <LivePreview code={code} title="Challenge Preview" />
        </TabsContent>

        <TabsContent value="results" className="flex-1 mt-0">
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
              <TestResults
                result={testResult || undefined}
                isLoading={isTestRunning}
                onRerun={handleRunTests}
              />
            )}
          </div>
        </TabsContent>

        <TabsContent value="terminal" className="flex-1 mt-0">
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
