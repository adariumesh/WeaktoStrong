"use client";

import {
  Bot,
  User,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Code,
  CheckCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import type { Message } from "@/types/ai";

interface MessageBubbleProps {
  message: Message;
  onSolutionSuggestion?: (suggestion: string) => void;
}

export function MessageBubble({
  message,
  onSolutionSuggestion,
}: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);

  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleFeedback = (type: "up" | "down") => {
    setFeedback(type);
    // TODO: Send feedback to analytics
  };

  const extractCodeBlocks = (content: string) => {
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const blocks = [];
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      blocks.push({
        language: match[1] || "text",
        code: match[2].trim(),
      });
    }

    return blocks;
  };

  const renderContent = (content: string) => {
    // Simple markdown-like rendering
    const lines = content.split("\n");
    const elements = [];
    let currentIndex = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Code blocks
      if (line.startsWith("```")) {
        const language = line.slice(3).trim();
        const codeLines = [];
        i++; // Skip opening line

        while (i < lines.length && !lines[i].startsWith("```")) {
          codeLines.push(lines[i]);
          i++;
        }

        elements.push(
          <div key={currentIndex++} className="my-3">
            <div className="bg-gray-900 rounded-t-lg px-3 py-2 text-xs text-gray-300 flex items-center justify-between">
              <span>{language || "code"}</span>
              <Button
                size="sm"
                variant="ghost"
                className="h-6 text-gray-300 hover:text-white"
                onClick={() => {
                  navigator.clipboard.writeText(codeLines.join("\n"));
                }}
              >
                <Copy className="w-3 h-3" />
              </Button>
            </div>
            <pre className="bg-gray-100 rounded-b-lg p-3 text-sm font-mono overflow-x-auto">
              <code>{codeLines.join("\n")}</code>
            </pre>
          </div>
        );
        continue;
      }

      // Headers
      if (line.startsWith("#")) {
        const level = line.match(/^#+/)?.[0].length || 1;
        const text = line.slice(level).trim();
        const Tag = `h${Math.min(level, 6)}` as keyof JSX.IntrinsicElements;

        elements.push(
          <Tag
            key={currentIndex++}
            className={`font-semibold my-2 ${
              level === 1 ? "text-lg" : level === 2 ? "text-base" : "text-sm"
            }`}
          >
            {text}
          </Tag>
        );
        continue;
      }

      // Lists
      if (line.startsWith("- ") || line.startsWith("* ")) {
        const items = [line.slice(2)];

        // Collect consecutive list items
        while (
          i + 1 < lines.length &&
          (lines[i + 1].startsWith("- ") || lines[i + 1].startsWith("* "))
        ) {
          i++;
          items.push(lines[i].slice(2));
        }

        elements.push(
          <ul
            key={currentIndex++}
            className="list-disc list-inside my-2 space-y-1"
          >
            {items.map((item, idx) => (
              <li key={idx} className="text-sm">
                {item}
              </li>
            ))}
          </ul>
        );
        continue;
      }

      // Regular text
      if (line.trim()) {
        elements.push(
          <p key={currentIndex++} className="my-1 text-sm leading-relaxed">
            {line}
          </p>
        );
      } else if (elements.length > 0) {
        // Add spacing for empty lines
        elements.push(<br key={currentIndex++} />);
      }
    }

    return elements;
  };

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {/* Avatar */}
      {!isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <Bot className="w-4 h-4 text-blue-600" />
          </div>
        </div>
      )}

      {/* Message Content */}
      <Card
        className={`max-w-[80%] ${
          isUser
            ? "bg-blue-600 text-white border-blue-600"
            : "bg-white border-gray-200"
        }`}
      >
        <CardContent className="p-3">
          {/* Message Header */}
          {isAssistant && (
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs">
                  {message.modelUsed?.includes("claude")
                    ? "Claude"
                    : "Local AI"}
                </Badge>
                {message.tokensUsed && (
                  <span className="text-xs text-gray-500">
                    {message.tokensUsed} tokens
                  </span>
                )}
              </div>
              <span className="text-xs text-gray-500">
                {formatDistanceToNow(new Date(message.createdAt), {
                  addSuffix: true,
                })}
              </span>
            </div>
          )}

          {/* Validation Warning */}
          {message.validationResult && !message.validationResult.isValid && (
            <div className="mb-2 p-2 bg-orange-50 border border-orange-200 rounded text-sm text-orange-700">
              {message.validationResult.feedback}
            </div>
          )}

          {/* Message Content */}
          <div className={`${isUser ? "text-white" : "text-gray-900"}`}>
            {isUser ? (
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {message.content}
              </p>
            ) : (
              <div className="space-y-2">{renderContent(message.content)}</div>
            )}
          </div>

          {/* Message Actions */}
          {isAssistant && (
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-100">
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-7 text-xs text-gray-500 hover:text-gray-700"
                  onClick={handleCopy}
                >
                  {copied ? (
                    <>
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3 mr-1" />
                      Copy
                    </>
                  )}
                </Button>

                {extractCodeBlocks(message.content).length > 0 &&
                  onSolutionSuggestion && (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-7 text-xs text-gray-500 hover:text-gray-700"
                      onClick={() => {
                        const codeBlocks = extractCodeBlocks(message.content);
                        if (codeBlocks.length > 0) {
                          onSolutionSuggestion(codeBlocks[0].code);
                        }
                      }}
                    >
                      <Code className="w-3 h-3 mr-1" />
                      Use Code
                    </Button>
                  )}
              </div>

              {/* Feedback */}
              <div className="flex items-center gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  className={`h-7 w-7 p-0 ${
                    feedback === "up"
                      ? "text-green-600"
                      : "text-gray-400 hover:text-green-600"
                  }`}
                  onClick={() => handleFeedback("up")}
                >
                  <ThumbsUp className="w-3 h-3" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className={`h-7 w-7 p-0 ${
                    feedback === "down"
                      ? "text-red-600"
                      : "text-gray-400 hover:text-red-600"
                  }`}
                  onClick={() => handleFeedback("down")}
                >
                  <ThumbsDown className="w-3 h-3" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Avatar */}
      {isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
        </div>
      )}
    </div>
  );
}
