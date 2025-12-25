/**
 * TypeScript types for AI system
 */

export type ModelTier = "local" | "haiku" | "sonnet";

export interface ValidationResult {
  isValid: boolean;
  feedback: string;
  suggestions: string[];
}

export interface ChallengeContext {
  challengeId?: string;
  title?: string;
  difficulty: string;
  requirements: string[];
  userCode?: string;
  failedTests?: string[];
  hintsUsed?: number;
}

export interface AIRequest {
  prompt: string;
  preferred_tier: ModelTier;
  challenge_id?: string; // Auto-fetch live context for this challenge
  challenge_context?: {
    challenge_id?: string;
    title?: string;
    difficulty?: string;
    requirements?: string[];
    user_code?: string;
    failed_tests?: string[];
  };
  temperature?: number;
  max_tokens?: number;
  enforce_validation?: boolean;
}

export interface AIResponse {
  content: string;
  model_used: string;
  tokens_used: number;
  tier: ModelTier;
  validation_passed: boolean;
  validation_feedback?: string;
}

export interface StreamChunk {
  type: "start" | "chunk" | "end" | "error";
  content?: string;
  model?: string;
  tokens_used?: number;
  error?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  modelUsed?: string;
  tokensUsed: number;
  createdAt: string;
  validationResult?: ValidationResult;
}

export interface Conversation {
  id: string;
  title: string;
  challengeId?: string;
  modelTier: ModelTier;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
  totalTokensUsed: number;
}

export interface TierProgress {
  currentTier: string;
  nextTier?: string;
  progress: number;
  required: number;
  percentage: number;
  requiresPro?: boolean;
}

export interface AIServiceStatus {
  localAvailable: boolean;
  claudeAvailable: boolean;
  currentTier: ModelTier;
  dailyTokensUsed: number;
  dailyTokenLimit: number;
  tierProgress: TierProgress;
}

export interface SendMessageOptions {
  challengeId?: string;
  challengeContext?: ChallengeContext;
  enforceValidation?: boolean;
  temperature?: number;
  maxTokens?: number;
}

export interface ModelInfo {
  name: string;
  type: "local" | "cloud";
  provider: string;
  context_window: number;
  capabilities: string[];
  tier: string;
  available: boolean;
  tier_required: string;
}

export interface TierInfo {
  name: string;
  display_name: string;
  model: string;
  requirements: string;
  features: string[];
}

export interface TokenUsage {
  user_id: string;
  date: string;
  model: string;
  tokens_used: number;
  cost_usd: number;
}

// Re-export for convenience
export type { ValidationResult as PromptValidation };

// Type guards
export function isValidModelTier(tier: string): tier is ModelTier {
  return ["local", "haiku", "sonnet"].includes(tier);
}

export function isStreamChunk(data: any): data is StreamChunk {
  return (
    data &&
    typeof data.type === "string" &&
    ["start", "chunk", "end", "error"].includes(data.type)
  );
}

export function isMessage(data: any): data is Message {
  return (
    data &&
    typeof data.id === "string" &&
    typeof data.role === "string" &&
    typeof data.content === "string" &&
    typeof data.created_at === "string"
  );
}
