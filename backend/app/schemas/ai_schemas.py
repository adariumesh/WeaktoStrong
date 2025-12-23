"""
Pydantic schemas for AI system requests and responses
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class ModelTier(Enum):
    """AI model tiers based on user progress"""

    LOCAL = "local"
    HAIKU = "haiku"
    SONNET = "sonnet"


class ValidationResult(BaseModel):
    """Result of prompt validation for anti-blind-prompting"""

    is_valid: bool
    feedback: str
    suggestions: list[str] = []


class ChallengeContext(BaseModel):
    """Context about the current challenge for AI assistance"""

    challenge_id: str | None = None
    title: str | None = None
    difficulty: str = "beginner"
    requirements: list[str] = []
    user_code: str | None = None
    failed_tests: list[str] = []
    hints_used: int = 0


class AIRequest(BaseModel):
    """Request to AI service with context and preferences"""

    prompt: str = Field(..., min_length=1, max_length=10000)
    preferred_tier: ModelTier = ModelTier.LOCAL
    challenge_id: str | None = None  # Auto-fetch live context for this challenge
    challenge_context: dict[str, Any] | None = None
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(4000, ge=100, le=8000)
    enforce_validation: bool = True

    @validator("prompt")
    def validate_prompt_content(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class AIResponse(BaseModel):
    """Response from AI service"""

    content: str
    model_used: str
    tokens_used: int
    tier: ModelTier
    validation_passed: bool = True
    validation_feedback: str | None = None


class StreamChunk(BaseModel):
    """Individual chunk in a streamed AI response"""

    type: str  # 'start', 'chunk', 'end', 'error'
    content: str | None = None
    model: str | None = None
    tokens_used: int | None = None
    error: str | None = None


class ConversationMessage(BaseModel):
    """Single message in a conversation"""

    id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    model_used: str | None = None
    tokens_used: int = 0
    created_at: str
    validation_result: ValidationResult | None = None


class Conversation(BaseModel):
    """Full conversation with metadata"""

    id: str
    title: str
    challenge_id: str | None = None
    model_tier: ModelTier
    messages: list[ConversationMessage] = []
    created_at: str
    updated_at: str
    total_tokens_used: int = 0


class TierProgress(BaseModel):
    """User's progress towards next AI model tier"""

    current_tier: str
    next_tier: str | None = None
    progress: int
    required: int
    percentage: float
    requires_pro: bool = False


class AIServiceStatus(BaseModel):
    """Status of AI services"""

    local_available: bool
    claude_available: bool
    current_tier: ModelTier
    daily_tokens_used: int
    daily_token_limit: int
    tier_progress: TierProgress


class TokenUsage(BaseModel):
    """Token usage tracking"""

    user_id: str
    date: str
    model: str
    tokens_used: int
    cost_usd: float = 0.0


class ModelInfo(BaseModel):
    """Information about an AI model"""

    name: str
    type: str  # 'local' or 'cloud'
    provider: str
    context_window: int
    capabilities: list[str]
    tier: str
