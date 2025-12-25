/**
 * AI API Client for backend communication
 */

import { authClient } from "./auth-client";
import type {
  AIRequest,
  AIResponse,
  AIServiceStatus,
  ValidationResult,
  StreamChunk,
} from "@/types/ai";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class AIClient {
  private baseUrl = API_BASE;

  private async fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    return authClient.fetchWithAuth(endpoint, options);
  }

  /**
   * Get AI service status and user's tier info
   */
  async getServiceStatus(): Promise<AIServiceStatus> {
    const response = await this.fetchWithAuth("/ai/status");
    return response.json();
  }

  /**
   * Validate a prompt against anti-blind-prompting rules
   */
  async validatePrompt(prompt: string): Promise<ValidationResult> {
    const response = await this.fetchWithAuth("/ai/validate-prompt", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    });
    return response.json();
  }

  /**
   * Generate a complete AI response (non-streaming)
   */
  async generateResponse(request: AIRequest): Promise<AIResponse> {
    const response = await this.fetchWithAuth("/ai/chat", {
      method: "POST",
      body: JSON.stringify(request),
    });
    return response.json();
  }

  /**
   * Stream AI chat response using Server-Sent Events
   */
  async streamChatResponse(
    request: AIRequest,
    onChunk: (chunk: StreamChunk) => void,
    options: {
      onStart?: (data: StreamChunk) => void;
      onEnd?: (data: StreamChunk) => void;
      onError?: (error: string) => void;
    } = {}
  ): Promise<void> {
    const token = await authClient.getValidToken();

    if (!token) {
      options.onError?.("Authentication required");
      return;
    }

    try {
      const response = await fetch(`${this.baseUrl}/ai/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          Accept: "text/event-stream",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(
          `Stream Error: ${response.status} ${response.statusText}`
        );
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Failed to get response stream reader");
      }

      const decoder = new TextDecoder();
      let buffer = "";

      try {
        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete lines
          const lines = buffer.split("\n");
          buffer = lines.pop() || ""; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                const chunk = data as StreamChunk;

                switch (chunk.type) {
                  case "start":
                    options.onStart?.(chunk);
                    break;
                  case "chunk":
                    if (chunk.content) {
                      onChunk(chunk);
                    }
                    break;
                  case "end":
                    options.onEnd?.(chunk);
                    break;
                  case "error":
                    options.onError?.(chunk.error || "Unknown streaming error");
                    break;
                }
              } catch (parseError) {
                console.warn("Failed to parse SSE data:", line, parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      options.onError?.(
        error instanceof Error ? error.message : "Unknown streaming error"
      );
      throw error;
    }
  }

  /**
   * Get list of available AI models for current user
   */
  async getAvailableModels() {
    const response = await this.fetchWithAuth("/ai/models");
    return response.json();
  }

  /**
   * Get information about AI model tiers and requirements
   */
  async getTierInfo() {
    const response = await this.fetchWithAuth("/ai/tiers");
    return response.json();
  }

  /**
   * Get detailed token usage statistics for current user
   */
  async getTokenUsage() {
    const response = await this.fetchWithAuth("/ai/usage");
    return response.json();
  }

  /**
   * Get AI context for a specific challenge
   */
  async getChallengeContext(challengeId: string) {
    const response = await this.fetchWithAuth(`/ai/context/${challengeId}`);
    return response.json();
  }

  /**
   * Generate smart hints for a specific challenge
   */
  async generateSmartHints(challengeId: string, maxHints: number = 3) {
    const response = await this.fetchWithAuth(`/ai/hints/${challengeId}`, {
      method: "POST",
      body: JSON.stringify({ max_hints: maxHints }),
    });
    return response.json();
  }
}

// Global client instance
export const aiClient = new AIClient();
