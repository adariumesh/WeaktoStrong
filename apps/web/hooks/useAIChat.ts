"use client";

import { useState, useCallback, useRef } from "react";
import { aiClient } from "@/lib/api/ai-client";
import type {
  Message,
  ModelTier,
  TierProgress,
  AIServiceStatus,
  SendMessageOptions,
} from "@/types/ai";

interface UseAIChatReturn {
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  currentTier: ModelTier;
  tierProgress: TierProgress;
  serviceStatus: AIServiceStatus;
  sendMessage: (prompt: string, options?: SendMessageOptions) => Promise<void>;
  clearMessages: () => void;
  retryLastMessage: () => Promise<void>;
}

export function useAIChat(challengeId?: string): UseAIChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentTier, setCurrentTier] = useState<ModelTier>("local");
  const [tierProgress, setTierProgress] = useState<TierProgress>({
    currentTier: "local",
    nextTier: "haiku",
    progress: 0,
    required: 10,
    percentage: 0,
    requiresPro: false,
  });
  const [serviceStatus, setServiceStatus] = useState<AIServiceStatus>({
    localAvailable: true,
    claudeAvailable: false,
    currentTier: "local",
    dailyTokensUsed: 0,
    dailyTokenLimit: 10000,
    tierProgress: {
      currentTier: "local",
      nextTier: "haiku",
      progress: 0,
      required: 10,
      percentage: 0,
      requiresPro: false,
    },
  });

  const lastMessageRef = useRef<{
    prompt: string;
    options?: SendMessageOptions;
  } | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load service status on mount
  const loadServiceStatus = useCallback(async () => {
    try {
      const status = await aiClient.getServiceStatus();
      setServiceStatus(status);
      setCurrentTier(status.currentTier);
      setTierProgress(status.tierProgress);
    } catch (error) {
      console.error("Failed to load AI service status:", error);
    }
  }, []);

  // Send a message to the AI
  const sendMessage = useCallback(
    async (prompt: string, options: SendMessageOptions = {}) => {
      if (isLoading || !prompt.trim()) return;

      // Store for retry functionality
      lastMessageRef.current = { prompt, options };

      // Add user message immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: prompt,
        createdAt: new Date().toISOString(),
        tokensUsed: 0,
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setIsStreaming(true);

      try {
        // Create abort controller for cancellation
        abortControllerRef.current = new AbortController();

        // Prepare request
        const request = {
          prompt,
          preferred_tier: currentTier,
          challenge_context: options.challengeContext
            ? {
                challenge_id: options.challengeId,
                title: options.challengeContext.title,
                difficulty: options.challengeContext.difficulty,
                requirements: options.challengeContext.requirements,
                user_code: options.challengeContext.userCode,
                failed_tests: options.challengeContext.failedTests || [],
              }
            : undefined,
          enforce_validation: options.enforceValidation ?? true,
          temperature: options.temperature ?? 0.7,
          max_tokens: options.maxTokens ?? 4000,
        };

        let assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: "",
          createdAt: new Date().toISOString(),
          tokensUsed: 0,
          modelUsed: `${currentTier}_model`,
        };

        // Add placeholder message
        setMessages((prev) => [...prev, assistantMessage]);

        // Stream response
        await aiClient.streamChatResponse(
          request,
          (chunk) => {
            // Update assistant message content
            assistantMessage = {
              ...assistantMessage,
              content: assistantMessage.content + chunk.content,
            };

            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessage.id ? assistantMessage : msg
              )
            );
          },
          {
            onStart: (startData) => {
              assistantMessage.modelUsed = startData.model;
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessage.id ? assistantMessage : msg
                )
              );
            },
            onEnd: (endData) => {
              assistantMessage.tokensUsed = endData.tokens_used || 0;
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessage.id ? assistantMessage : msg
                )
              );
              setIsStreaming(false);
            },
            onError: (error) => {
              assistantMessage.content = `❌ Error: ${error}`;
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessage.id ? assistantMessage : msg
                )
              );
              setIsStreaming(false);
            },
          }
        );

        // Refresh service status after successful message
        await loadServiceStatus();
      } catch (error) {
        console.error("Failed to send message:", error);

        // Add error message
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: `❌ Failed to send message: ${error instanceof Error ? error.message : "Unknown error"}`,
          createdAt: new Date().toISOString(),
          tokensUsed: 0,
        };

        setMessages((prev) => [...prev, errorMessage]);
        setIsStreaming(false);
      } finally {
        setIsLoading(false);
        abortControllerRef.current = null;
      }
    },
    [isLoading, currentTier, loadServiceStatus]
  );

  // Retry the last message
  const retryLastMessage = useCallback(async () => {
    if (!lastMessageRef.current) return;

    // Remove the last assistant message if it was an error
    setMessages((prev) => {
      const lastMsg = prev[prev.length - 1];
      if (lastMsg?.role === "assistant" && lastMsg.content.startsWith("❌")) {
        return prev.slice(0, -1);
      }
      return prev;
    });

    await sendMessage(
      lastMessageRef.current.prompt,
      lastMessageRef.current.options
    );
  }, [sendMessage]);

  // Clear all messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    lastMessageRef.current = null;

    // Cancel any ongoing requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    setIsLoading(false);
    setIsStreaming(false);
  }, []);

  return {
    messages,
    isLoading,
    isStreaming,
    currentTier,
    tierProgress,
    serviceStatus,
    sendMessage,
    clearMessages,
    retryLastMessage,
  };
}
