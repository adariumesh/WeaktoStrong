# AI Development Context - Phase 5

> **Domain Focus:** AI Integration & Anti-Blind-Prompting System  
> **Session Type:** AI Development  
> **Max Context:** 80K tokens

## 🎯 Session Objectives

**Primary Goals:**

- Implement AI chat interface with streaming responses
- Build anti-blind-prompting enforcement system
- Create model tier progression (Local → Haiku → Sonnet)
- Integrate AI assistant into Resources panel

## 📋 Current AI Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI SYSTEM ARCHITECTURE               │
├─────────────────────────────────────────────────────────┤
│ Frontend: AI Chat Interface                             │
│  ├── Chat UI with streaming responses                   │
│  ├── Anti-blind-prompting validation                    │
│  ├── Model tier indicators                              │
│  └── Conversation history                               │
├─────────────────────────────────────────────────────────┤
│ Backend: AI Routing Service                             │
│  ├── Model tier detection (user progress)               │
│  ├── Anti-blind-prompting validation                    │
│  ├── Streaming SSE responses                            │
│  └── Token usage tracking                               │
├─────────────────────────────────────────────────────────┤
│ AI Providers:                                           │
│  ├── Local: Ollama + Llama 3.2 8B                       │
│  ├── Cloud: Claude Haiku (earned access)                │
│  └── Premium: Claude Sonnet (pro users)                 │
└─────────────────────────────────────────────────────────┘
```

## 🔗 Integration Points from Phase 4

### Test Results → AI Feedback

```typescript
// When tests fail, AI provides contextual help
interface TestFailureContext {
  failedTests: TestCase[];
  userCode: string;
  challengeRequirements: string[];
  hints: string[];
}

// AI analyzes failures and provides targeted guidance
const aiAnalysis = await analyzeTestFailures(context);
```

### Progress Tracking → Model Tier

```python
def get_allowed_model_tier(user: User, challenge: Challenge) -> ModelTier:
    """Determine which AI model user can access based on progress"""
    if challenge.difficulty == "beginner":
        return ModelTier.LOCAL
    elif challenge.difficulty == "intermediate":
        return ModelTier.HAIKU if user.local_challenges_passed >= 10 else ModelTier.LOCAL
    else:  # advanced
        return ModelTier.SONNET if user.haiku_challenges_passed >= 10 else ModelTier.HAIKU
```

## 🚀 Phase 5 Implementation Plan

### 5.1: Local AI Setup (Ollama + Llama)

**Files to Create/Modify:**

- `/backend/app/core/ai/local_llm.py` - Ollama integration
- `/docker-compose.yml` - Add Ollama service
- `/backend/requirements.txt` - Add Ollama client

### 5.2: AI Chat Interface

**Files to Create/Modify:**

- `/apps/web/components/ai/chat-interface.tsx` - Main chat UI
- `/apps/web/components/ai/message-bubble.tsx` - Chat bubbles
- `/apps/web/hooks/useAIChat.ts` - Chat state management
- `/apps/web/lib/api/ai-client.ts` - AI API client

### 5.3: Anti-Blind-Prompting System

**Files to Create/Modify:**

- `/backend/app/core/ai/prompt_validator.py` - Prompt validation
- `/apps/web/components/ai/prompt-helper.tsx` - UI guidance
- `/backend/app/schemas/ai_schemas.py` - AI request/response models

### 5.4: Model Tier Progression

**Files to Create/Modify:**

- `/backend/app/core/ai/model_router.py` - Model selection logic
- `/backend/app/api/v1/ai.py` - AI API endpoints
- `/apps/web/components/ai/model-tier-indicator.tsx` - Show current tier

## 🧠 Anti-Blind-Prompting Specifications

### Validation Rules

```python
REQUIRED_PATTERNS = [
    "because", "my approach", "I think", "I want to",
    "my strategy", "I believe", "my goal"
]

REJECTED_PATTERNS = [
    "just do it", "make it work", "fix it", "generate code",
    "write code for", "implement this", "build this"
]

def validate_prompt(message: str) -> ValidationResult:
    """Enforce thoughtful prompting patterns"""
    has_reasoning = any(pattern in message.lower() for pattern in REQUIRED_PATTERNS)
    has_lazy_patterns = any(pattern in message.lower() for pattern in REJECTED_PATTERNS)

    return ValidationResult(
        is_valid=has_reasoning and not has_lazy_patterns,
        feedback="Explain your thinking and approach before asking for implementation"
    )
```

### UI Enforcement

```typescript
// Prompt input validation with real-time feedback
const validatePromptInput = (input: string): PromptValidation => {
  const hasReasoning = REQUIRED_PATTERNS.some((pattern) =>
    input.toLowerCase().includes(pattern)
  );
  const hasLazyPatterns = REJECTED_PATTERNS.some((pattern) =>
    input.toLowerCase().includes(pattern)
  );

  return {
    isValid: hasReasoning && !hasLazyPatterns,
    feedback: hasReasoning
      ? "Good! You're explaining your approach."
      : "Please explain your thinking before asking for help.",
  };
};
```

## 🔄 Streaming Response Architecture

### Backend SSE Implementation

```python
from fastapi.responses import StreamingResponse
import json
import asyncio

async def stream_ai_response(prompt: str, model: str):
    """Stream AI responses using Server-Sent Events"""
    async def generate():
        yield f"data: {json.dumps({'type': 'start', 'model': model})}\n\n"

        async for chunk in ai_service.stream_response(prompt, model):
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Frontend SSE Consumption

```typescript
const useStreamingAIResponse = (onChunk: (chunk: string) => void) => {
  const streamResponse = async (prompt: string) => {
    const eventSource = new EventSource(`/api/v1/ai/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "chunk") {
        onChunk(data.content);
      }
    };
  };

  return { streamResponse };
};
```

## 📊 Token Usage Tracking

### Backend Tracking

```python
class TokenUsageTracker:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def track_usage(self, user_id: str, model: str, tokens: int):
        key = f"tokens:{user_id}:{datetime.now().date()}"
        await self.redis.hincrby(key, model, tokens)
        await self.redis.expire(key, 86400)  # 24 hours

    async def get_daily_usage(self, user_id: str) -> dict:
        key = f"tokens:{user_id}:{datetime.now().date()}"
        return await self.redis.hgetall(key)
```

### Rate Limiting by Tier

```python
TIER_LIMITS = {
    "free": {"daily_tokens": 10000, "models": ["local"]},
    "pro": {"daily_tokens": 100000, "models": ["local", "haiku", "sonnet"]},
    "team": {"daily_tokens": 500000, "models": ["local", "haiku", "sonnet"]},
    "enterprise": {"daily_tokens": -1, "models": ["local", "haiku", "sonnet"]}
}
```

## 🎨 UI Component Architecture

### Chat Interface Layout

```typescript
interface ChatInterfaceProps {
  challengeId?: string;
  context?: ChallengeContext;
  onSolutionSuggestion?: (suggestion: string) => void;
}

// Chat interface integrates with workspace
<div className="flex flex-col h-full">
  <ChatHeader modelTier={currentTier} tokensUsed={usage} />
  <MessageHistory messages={messages} isStreaming={isStreaming} />
  <PromptInput onSubmit={handleSubmit} validation={promptValidation} />
  <ModelTierProgress currentTier={tier} progress={progress} />
</div>
```

### Model Tier Indicator

```typescript
const ModelTierIndicator = ({ tier, progress }: {
  tier: 'local' | 'haiku' | 'sonnet';
  progress: { current: number; required: number; };
}) => (
  <div className="flex items-center gap-2">
    <Badge variant={getBadgeVariant(tier)}>
      {tier.charAt(0).toUpperCase() + tier.slice(1)}
    </Badge>
    <Progress value={(progress.current / progress.required) * 100} />
    <span className="text-xs text-gray-600">
      {progress.current}/{progress.required} to next tier
    </span>
  </div>
);
```

## 🗄 Database Schema Extensions

### Conversation Storage

```sql
-- AI conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    challenge_id UUID REFERENCES challenges(id) ON DELETE SET NULL,
    title VARCHAR(200),
    model_tier VARCHAR(20) NOT NULL, -- 'local', 'haiku', 'sonnet'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversation messages
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    model_used VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Token usage tracking
CREATE TABLE token_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    model VARCHAR(20) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date, model)
);
```

## 🔌 Environment Configuration

### Required Environment Variables

```bash
# Local AI (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:8b

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxx
CLAUDE_HAIKU_MODEL=claude-3-haiku-20240307
CLAUDE_SONNET_MODEL=claude-3-5-sonnet-20241022

# AI Service Configuration
AI_DEFAULT_TIMEOUT=30
AI_MAX_TOKENS_PER_REQUEST=4000
AI_STREAM_CHUNK_SIZE=50

# Anti-Blind-Prompting
ENABLE_PROMPT_VALIDATION=true
MIN_PROMPT_LENGTH=20
REQUIRED_REASONING_PATTERNS=because,approach,think,strategy
```

## 📈 Success Metrics

### Technical Metrics

- [ ] Response time: <2s for local, <5s for cloud
- [ ] Stream latency: <500ms first chunk
- [ ] Anti-blind-prompting: 90%+ compliance
- [ ] Model tier progression: 80% complete challenges to unlock

### User Experience Metrics

- [ ] Chat interface: Intuitive and responsive
- [ ] Prompt validation: Helpful, not annoying
- [ ] Model progression: Clear and motivating
- [ ] Context awareness: AI understands challenge context

## 🎬 Development Session Commands

### Start AI Development Session

```bash
echo "=== AI DEVELOPMENT SESSION ==="
echo "Focus: AI chat integration, anti-blind-prompting"
echo "Context files loaded:"
echo "- claude_memory.md (architecture)"
echo "- DEVELOPMENT_PLAN.md (roadmap)"
echo "- AI_DEVELOPMENT_CONTEXT.md (this file)"
echo ""
echo "Ready to implement Phase 5: AI Integration 🤖"
```

### Quick File Reference

```bash
# Core AI files (to be created)
ls apps/web/components/ai/
ls backend/app/core/ai/
ls backend/app/api/v1/ai.py
```

---

**Next Implementation:** Start with 5.1 (Local AI Setup) → 5.2 (Chat Interface) → 5.3 (Anti-Blind-Prompting) → 5.4 (Model Tiers)
