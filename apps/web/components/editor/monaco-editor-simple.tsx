"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { Button } from "@/components/ui/button";
import { Play, RotateCcw, Download } from "lucide-react";

// Dynamic import to prevent SSR issues
const Editor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-gray-50">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm text-gray-600">Loading editor...</p>
      </div>
    </div>
  ),
});

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  height?: string;
  theme?: "light" | "dark";
  readOnly?: boolean;
  onRun?: () => void;
  onReset?: () => void;
  fileName?: string;
}

export function MonacoEditor({
  value,
  onChange,
  language = "html",
  height = "100%",
  theme = "light",
  readOnly = false,
  onRun,
  onReset,
  fileName = "index.html",
}: MonacoEditorProps) {
  const [currentTheme, setCurrentTheme] = useState(theme);

  const downloadCode = () => {
    const blob = new Blob([value], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full bg-white border border-gray-200 rounded-lg overflow-hidden min-h-0 min-w-0">
      {/* Editor Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 bg-gray-50 border-b border-gray-200 flex-shrink-0 min-w-0">
        <div className="flex items-center gap-2 min-w-0 flex-shrink">
          <span className="text-sm font-medium text-gray-700 truncate">{fileName}</span>
          <span className="text-xs text-gray-500 flex-shrink-0">
            {language.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center gap-1 flex-shrink-0">
          <Button
            size="sm"
            variant="ghost"
            onClick={downloadCode}
            className="h-7 px-1"
            title="Download Code"
            aria-label="Download code as file"
          >
            <Download size={12} />
          </Button>

          {onReset && (
            <Button
              size="sm"
              variant="outline"
              onClick={onReset}
              className="h-7 px-1"
              title="Reset Code"
              aria-label="Reset code to initial state"
            >
              <RotateCcw size={12} />
            </Button>
          )}

          {onRun && (
            <Button
              size="sm"
              onClick={onRun}
              className="h-7 px-2 bg-green-600 hover:bg-green-700"
              title="Run Tests"
              aria-label="Execute tests for this code"
            >
              <Play size={12} className="mr-1" />
              <span className="hidden sm:inline">Run Tests</span>
              <span className="sm:hidden">Run</span>
            </Button>
          )}
        </div>
      </div>

      {/* Monaco Editor */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <Editor
          height="100%"
          width="100%"
          defaultLanguage={language}
          language={language}
          value={value}
          onChange={(value) => onChange(value || "")}
          theme={currentTheme === "dark" ? "vs-dark" : "vs"}
          options={{
            readOnly,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
            fontFamily:
              "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
            lineNumbers: "on",
            renderWhitespace: "selection",
            automaticLayout: true,
            wordWrap: "on",
            bracketPairColorization: { enabled: true },
            suggest: {
              showKeywords: true,
              showSnippets: true,
            },
            quickSuggestions: {
              other: true,
              comments: true,
              strings: true,
            },
            parameterHints: { enabled: true },
            autoIndent: "full",
            formatOnPaste: true,
            formatOnType: true,
          }}
        />
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between px-3 py-1 bg-gray-50 border-t border-gray-200 text-xs text-gray-600 flex-shrink-0">
        <div className="flex items-center gap-4">
          <span>Lines: {value.split("\n").length}</span>
          <span>Characters: {value.length}</span>
        </div>
        <div className="flex items-center gap-2">
          <span>UTF-8</span>
          <span>•</span>
          <span>{language.toUpperCase()}</span>
        </div>
      </div>
    </div>
  );
}
