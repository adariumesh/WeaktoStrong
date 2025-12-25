"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, AlertCircle, CheckCircle, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { MessageBubble } from "./message-bubble";
import { ModelTierIndicator } from "./model-tier-indicator";
import { PromptHelper } from "./prompt-helper";
import { useAIChat } from "@/hooks/useAIChat";
import { validatePrompt } from "@/lib/ai/prompt-validation";
import type { Message, ModelTier, ValidationResult } from "@/types/ai";

interface ChatInterfaceProps {
  challengeId?: string;
  challengeContext?: {
    title: string;
    difficulty: string;
    requirements: string[];
    userCode?: string;
    failedTests?: string[];
  };
  onSolutionSuggestion?: (suggestion: string) => void;
}

export function ChatInterface({
  challengeId,
  challengeContext,
  onSolutionSuggestion,
}: ChatInterfaceProps) {
  const [prompt, setPrompt] = useState("");
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [showPromptHelper, setShowPromptHelper] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const {
    messages,
    isLoading,
    isStreaming,
    currentTier,
    tierProgress,
    sendMessage,
    serviceStatus,
  } = useAIChat(challengeId);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  // Validate prompt as user types
  useEffect(() => {
    if (prompt.trim().length > 5) {
      const result = validatePrompt(prompt);
      setValidation(result);
    } else {
      setValidation(null);
    }
  }, [prompt]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!prompt.trim() || isLoading) return;

    // Validate prompt before sending
    const validationResult = validatePrompt(prompt);
    if (!validationResult.isValid) {
      setValidation(validationResult);
      setShowPromptHelper(true);
      return;
    }

    // Send message with challenge context
    await sendMessage(prompt, {
      challengeId,
      challengeContext,
      enforceValidation: true,
    });

    // Clear input
    setPrompt("");
    setValidation(null);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const isPromptValid = validation?.isValid !== false;
  const canSend = prompt.trim() && isPromptValid && !isLoading;

  return (
    <div className="flex flex-col h-full bg-white border-l border-gray-200">
      {/* Header */}
      <CardHeader className="border-b bg-gray-50 py-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Bot className="w-5 h-5 text-blue-600" />
            AI Assistant
          </CardTitle>
          <ModelTierIndicator
            tier={currentTier}
            progress={tierProgress}
            compact
          />
        </div>
        {challengeContext && (
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="outline">{challengeContext.difficulty}</Badge>
            <span className="text-sm text-gray-600 truncate">
              {challengeContext.title}
            </span>
          </div>
        )}
      </CardHeader>

      {/* Service Status Alert */}
      {!serviceStatus.localAvailable && !serviceStatus.claudeAvailable && (
        <Alert className="m-4 mb-0">
          <AlertCircle className="w-4 h-4" />
          <AlertDescription>
            AI services are currently unavailable. Please try again later.
          </AlertDescription>
        </Alert>
      )}

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ready to help!
              </h3>
              <p className="text-gray-600 mb-4">
                Explain your approach and I'll guide you through the challenge.
              </p>
              {currentTier === "local" && (
                <div className="text-sm text-blue-600">
                  🤖 Using local AI for privacy and unlimited usage
                </div>
              )}
            </div>
          ) : (
            messages.map((message, index) => (
              <MessageBubble
                key={index}
                message={message}
                onSolutionSuggestion={onSolutionSuggestion}
              />
            ))
          )}

          {/* Streaming indicator */}
          {isStreaming && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200"></div>
              </div>
              AI is thinking...
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Prompt Helper */}
      {showPromptHelper && validation && !validation.isValid && (
        <PromptHelper
          validation={validation}
          onDismiss={() => setShowPromptHelper(false)}
          onExample={(example) => {
            setPrompt(example);
            setShowPromptHelper(false);
            textareaRef.current?.focus();
          }}
        />
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t bg-gray-50">
        {/* Validation Feedback */}
        {validation && (
          <div className="mb-3">
            {validation.isValid ? (
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle className="w-4 h-4" />
                {validation.feedback}
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-orange-600">
                <AlertCircle className="w-4 h-4" />
                {validation.feedback}
              </div>
            )}
          </div>
        )}

        <div className="flex gap-3">
          <Textarea
            ref={textareaRef}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              currentTier === "local"
                ? "Explain your approach and ask for guidance..."
                : `Ask ${currentTier.toUpperCase()} AI for help with your approach...`
            }
            className={`min-h-[60px] resize-none ${
              validation && !validation.isValid
                ? "border-orange-300 focus:border-orange-500"
                : validation?.isValid
                  ? "border-green-300 focus:border-green-500"
                  : ""
            }`}
            disabled={isLoading}
          />

          <div className="flex flex-col gap-2">
            <Button
              type="submit"
              size="sm"
              disabled={!canSend}
              className="min-w-[60px]"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>

            {prompt.length > 10 && !validation && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setShowPromptHelper(true)}
                className="text-xs"
              >
                <Zap className="w-3 h-3 mr-1" />
                Tips
              </Button>
            )}
          </div>
        </div>

        {/* Character count */}
        <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
          <span>{prompt.length}/2000 characters</span>
          <span className="flex items-center gap-1">
            <span
              className={`w-2 h-2 rounded-full ${
                serviceStatus.localAvailable ? "bg-green-500" : "bg-red-500"
              }`}
            />
            {currentTier.toUpperCase()} AI
          </span>
        </div>
      </form>
    </div>
  );
}
