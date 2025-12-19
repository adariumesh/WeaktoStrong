# WEAK-TO-STRONG: Claude Code Memory File

> Compressed context for AI-assisted development. Load at session start.

---

## 📁 PROJECT FILES INDEX

This memory file is part of a 5-file context package. Load additional files as needed:

| File                     | Load When                      | Contains                                                    |
| ------------------------ | ------------------------------ | ----------------------------------------------------------- |
| **CLAUDE_MEMORY.md**     | Every session (this file)      | Architecture, schema, APIs, tech stack                      |
| **DEVELOPMENT_PLAN.md**  | Every session                  | Chunked phases, success criteria, execution order           |
| **ENV_TEMPLATE.md**      | Setting up environment         | All env vars with descriptions                              |
| **AI_PROMPTS.md**        | Building AI features (Phase 5) | System prompts, anti-blind-prompting, hints, error messages |
| **CHALLENGE_CONTENT.md** | Seeding challenges (Phase 3.4) | Requirements, test specs, hints for 15 Web challenges       |

### Quick Load Commands

```bash
# Always load these two:
cat CLAUDE_MEMORY.md DEVELOPMENT_PLAN.md

# For environment setup:
cat ENV_TEMPLATE.md

# For AI integration work:
cat AI_PROMPTS.md

# For challenge seeding:
cat CHALLENGE_CONTENT.md
```

### File Relationships

```
CLAUDE_MEMORY.md (core context)
    ├── DEVELOPMENT_PLAN.md (what to build, in what order)
    │       └── References phases that need:
    │               ├── ENV_TEMPLATE.md (Phase 0)
    │               ├── AI_PROMPTS.md (Phase 5)
    │               └── CHALLENGE_CONTENT.md (Phase 3.4)
    └── Defines schemas/APIs that other files implement
```

---

## PROJECT IDENTITY

**Name:** Weak-to-Strong | **Domain:** weaktostrong.dev
**Mission:** Train AI supervisors, not AI consumers. Close the "AI literacy gap."
**Core Concept:** Less capable supervisor (human) learns to steer more capable AI through precision, verification, and intent alignment (from AI alignment research).

## 🚀 **IMPLEMENTATION STATUS**

**✅ PHASE 0: PROJECT BOOTSTRAP (COMPLETE)**

- Turborepo monorepo with Next.js 14 + FastAPI
- Docker Compose for PostgreSQL, Redis, Ollama, LocalStack
- GitHub Actions CI/CD + Husky pre-commit hooks
- Code quality: ESLint, Prettier, Ruff, Black

**✅ PHASE 1: AUTHENTICATION SYSTEM (COMPLETE)**

- NextAuth integration with GitHub OAuth + email/password
- FastAPI JWT-based API with bcrypt password hashing
- Rate limiting: 100 requests/hour for free tier
- Protected routes with automatic token refresh
- User registration, login, logout, session management
- Database: User and Session models with Alembic migrations

## ARCHITECTURE SNAPSHOT

```
┌─────────────────────────────────────────────────────┐
│ FRONTEND: Next.js 14 + React 18 + Tailwind + Shadcn │
│ ├─ Monaco Editor (code)                             │
│ ├─ Three-panel: Challenge | Workspace | Resources   │
│ └─ Zustand (client) + React Query (server state)    │
├─────────────────────────────────────────────────────┤
│ BACKEND: FastAPI (Python)                           │
│ ├─ Services: Auth, AI, Test, Progress               │
│ └─ Async, Pydantic validation                       │
├─────────────────────────────────────────────────────┤
│ DATA: PostgreSQL (Supabase) + Redis (Upstash)       │
├─────────────────────────────────────────────────────┤
│ AI LAYER:                                           │
│ ├─ Local: Ollama + Llama 3.2 8B (default)           │
│ ├─ Cloud: Claude Haiku → Sonnet (earned access)     │
│ └─ Anti-blind-prompting enforcement                 │
├─────────────────────────────────────────────────────┤
│ SANDBOX: Docker + LocalStack (AWS emulation)        │
│ ├─ 512MB RAM, 0.5 CPU, 5min timeout, no network     │
│ └─ Test runners: Playwright, pytest, Lighthouse     │
├─────────────────────────────────────────────────────┤
│ HOSTING: Vercel (frontend) + Railway (backend)      │
└─────────────────────────────────────────────────────┘
```

## KEY DIFFERENTIATORS

1. **Anti-Blind-Prompting:** Pre-gen (explain approach) + Post-gen (explain output) + "Vibe Gap" tracking
2. **Model Progression:** Earn stronger models by succeeding with weaker ones (Local→Haiku→Sonnet)
3. **Red-Team Checkpoints:** Security challenges embedded in curriculum (XSS, SQLi, PII exposure)
4. **Portfolio-Ready:** Three tracks (Web/Data/Cloud) produce real deployable projects

## DATABASE SCHEMA (Core Tables)

```sql
-- users: id, email, password_hash, name, tier(free/pro/team/enterprise), tokens_used_today
-- tracks: id, name, description, order
-- challenges: id, track_id, title, description, difficulty(beginner/intermediate/advanced),
--             order, model_tier(local/haiku/sonnet), requirements(JSONB), constraints(JSONB),
--             test_config(JSONB), hints(JSONB[3]), is_red_team, points
-- submissions: id, user_id, challenge_id, code, test_results, score, created_at
-- progress: id, user_id, challenge_id, status, attempts, hints_used, best_score, completed_at
-- conversations: id, user_id, challenge_id, messages(JSONB), tokens_used, model_tier
```

## AI ROUTING LOGIC

```python
def get_model_tier(user, challenge):
    if challenge.difficulty == "beginner": return LOCAL
    if challenge.difficulty == "intermediate":
        return HAIKU if user.local_challenges_completed >= 10 else LOCAL
    if challenge.difficulty == "advanced":
        if user.tier == "pro" and user.haiku_challenges_completed >= 10:
            return SONNET
        return HAIKU

def validate_prompt(msg):
    requires = ["because", "my approach", "i think", "i want to"]
    rejects = ["just do it", "make it work", "fix it", "generate code"]
    return any(r in msg.lower() for r in requires) and not any(r in msg.lower() for r in rejects)
```

## DIRECTORY STRUCTURE

```
weak-to-strong/
├── apps/web/                    # Next.js frontend
│   ├── app/(auth)/              # Login, signup routes
│   ├── app/(dashboard)/         # Protected routes
│   ├── app/challenges/          # Challenge pages
│   ├── components/{ui,challenge,editor,ai,common}/
│   ├── hooks/                   # useAIChat, useTestRunner, etc.
│   ├── stores/                  # Zustand stores
│   └── lib/                     # Utils
├── backend/
│   ├── app/
│   │   ├── api/v1/{auth,challenges,submissions,ai,progress}.py
│   │   ├── core/{ai,testing,auth}/
│   │   ├── models/              # SQLAlchemy models
│   │   └── schemas/             # Pydantic schemas
├── docker/
│   ├── web-sandbox/             # Node + Playwright + Lighthouse
│   ├── data-sandbox/            # Python + pandas + jupyter
│   └── localstack/              # AWS emulation
├── packages/{shared,ui,config}/ # Monorepo shared packages
└── turbo.json
```

## API ENDPOINTS (Key Routes)

### ✅ **IMPLEMENTED (Phase 1)**

```
Auth:     POST /api/v1/auth/{register,login,refresh,logout} | GET /api/v1/auth/me
          POST /api/v1/auth/oauth/{github,google}
Health:   GET / | GET /health
```

### 🔄 **PLANNED (Future Phases)**

```
Tracks:   GET /tracks | GET /tracks/{id}/challenges
Challenge: GET /challenges/{id} | GET /challenges/{id}/hints/{n} | POST /challenges/{id}/submit
AI:       POST /ai/chat (streaming SSE) | GET /ai/conversations/{id} | GET /ai/usage
Progress: GET /progress | GET /progress/tracks/{id} | GET /certificates
```

## PRICING MODEL

| Tier       | Price       | Limits                                 |
| ---------- | ----------- | -------------------------------------- |
| Free       | $0          | 5 challenges/track, local SLM only     |
| Pro        | $29/mo      | Unlimited, Claude access, certificates |
| Team       | $49/user/mo | Admin dashboard, shared progress       |
| Enterprise | Custom      | On-premise, SSO, audit logs            |

## CHALLENGE STRUCTURE (Per Challenge)

```json
{
  "id": "uuid", "track_id": "uuid", "title": "string",
  "description": "markdown", "difficulty": "beginner|intermediate|advanced",
  "order": 1, "model_tier": "local|haiku|sonnet", "points": 100,
  "requirements": [{"id": "req1", "text": "...", "points": 20}],
  "constraints": [{"id": "con1", "text": "...", "type": "accessibility|performance|security"}],
  "test_config": {"type": "playwright|pytest", "timeout": 30000, "tests": [...]},
  "hints": ["conceptual nudge", "structural guidance", "partial solution"],
  "is_red_team": false
}
```

## 6-MONTH MILESTONES

| Month | Goal                       | Key Metrics                         |
| ----- | -------------------------- | ----------------------------------- |
| 1     | MVP + Web Track            | 20 beta users, 15 challenges        |
| 2     | Data Track + LocalStack    | 50 users, 2 tracks                  |
| 3     | Cloud Track + Monetization | 500 users, 20 paying, $300 MRR      |
| 4     | University Pilot + Grants  | 1 LOI, TEDCO/MIPS submitted         |
| 5     | Content Scale + B2B        | 150 challenges, 5 B2B leads         |
| 6     | Fundraise Ready            | 2K users, $3K MRR, deck + data room |

## TECH DEPENDENCIES

**Frontend:** next@14, react@18, tailwindcss@3, @shadcn/ui, @monaco-editor/react@4, zustand@4, @tanstack/react-query@5, next-auth@5, zod@3, framer-motion@11
**Backend:** fastapi, uvicorn, sqlalchemy, alembic, pydantic, httpx, anthropic, redis, docker, boto3
**Testing:** vitest, @testing-library/react, playwright, pytest, @axe-core/cli, lighthouse

## SANDBOX SPECS

- Memory: 512MB | CPU: 0.5 | Timeout: 5min | Network: none
- Images: weak-to-strong/{web,data,cloud}-sandbox:latest
- LocalStack services: S3, Lambda, DynamoDB, API Gateway, SQS, SNS

## CRITICAL IMPLEMENTATION NOTES

1. **JWT:** 15min access + 7d refresh, Redis session storage
2. **Rate Limits:** Free=100/hr, Pro=500/hr, Enterprise=unlimited
3. **Streaming:** SSE for AI responses, chunk by chunk
4. **Test Results:** Return {functional, accessibility, performance} scores
5. **Progress Unlock:** 80% pass rate on tier N → unlock tier N+1 model

## WEEK 1 CHECKLIST (Bootstrap)

- [x] GitHub monorepo (turborepo) ✅
- [x] NextAuth (GitHub + email/password) ✅
- [x] Docker sandbox foundation ✅
- [x] FastAPI backend with JWT authentication ✅
- [x] PostgreSQL + Redis setup ✅
- [x] User registration and login flows ✅
- [ ] Domain: weaktostrong.dev
- [ ] Vercel + Railway + Supabase setup
- [ ] Ollama + Llama 3.2 8B local
- [ ] Basic 3-panel UI scaffold

## 🔧 **CURRENT TECH STACK (IMPLEMENTED)**

**Frontend:** Next.js 14, NextAuth, Tailwind CSS, TypeScript
**Backend:** FastAPI, SQLAlchemy, Alembic, Pydantic, JWT, bcrypt
**Database:** PostgreSQL (asyncpg), Redis
**Auth:** GitHub OAuth (Ov23ligZpEMxoOjbXjof), JWT tokens, rate limiting
**DevOps:** Turborepo, GitHub Actions, Husky, ESLint, Prettier, Ruff, Black
**Testing:** FastAPI TestClient, Pydantic validation, auth utilities testing
