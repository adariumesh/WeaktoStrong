# WEAK-TO-STRONG: Systematic Development Plan for Claude Code

> **How to use this file:** Load CLAUDE_MEMORY.md for context, then work through phases sequentially. Each chunk is designed to be completable in 1-3 Claude Code sessions. Test each chunk before moving to the next.

## 🚀 **CURRENT STATUS: PHASE 1 COMPLETE**

**✅ Phase 0: PROJECT BOOTSTRAP** - Complete monorepo setup with CI/CD
**✅ Phase 1: AUTHENTICATION SYSTEM** - Complete NextAuth + FastAPI JWT authentication  
**🔄 Phase 2: CORE UI LAYOUT** - Next: Three-panel resizable layout with Shadcn/ui

## 📁 Related Files

- **CLAUDE_MEMORY.md** - Architecture, schemas, APIs (load every session)
- **ENV_TEMPLATE.md** - Load during Phase 0 setup
- **AI_PROMPTS.md** - Load during Phase 5 (AI Integration)
- **CHALLENGE_CONTENT.md** - Load during Phase 3, Chunk 3.4 (Challenge Seeding)

---

---

## PHASE 0: PROJECT BOOTSTRAP

**Goal:** Repository structure + local dev environment running
**Estimated Sessions:** 1-2

### Chunk 0.1: Monorepo Setup

```bash
# Claude Code should execute:
1. Create turborepo monorepo structure
2. Initialize apps/web (Next.js 14 with App Router)
3. Initialize backend/ (FastAPI with uvicorn)
4. Create packages/{shared,ui,config}
5. Set up turbo.json for task orchestration
6. Create root package.json with workspace scripts
7. Initialize git, add .gitignore, .env.example
```

**Success Criteria:**

- [x] `npm install` works at root ✅
- [x] `npm run dev` starts both frontend and backend ✅
- [x] Directory structure matches spec in memory file ✅

### Chunk 0.2: External Services Setup

```bash
# Claude Code should create config files for:
1. Supabase project connection (env vars)
2. Redis connection (Upstash or local)
3. Ollama installation verification script
4. Docker Compose for local services (postgres, redis, ollama)
```

**Success Criteria:**

- [x] `docker-compose up -d` starts all services ✅
- [x] Backend can connect to database ✅
- [ ] Ollama responds to API calls

### Chunk 0.3: CI/CD Foundation

```bash
# Claude Code should create:
1. GitHub Actions workflow for lint + test on PR
2. Husky pre-commit hooks
3. ESLint + Prettier config (frontend)
4. Ruff + Black config (backend)
```

**Success Criteria:**

- [x] Pre-commit hooks run on commit ✅
- [x] CI passes on push to main ✅

---

## PHASE 1: AUTHENTICATION SYSTEM

**Goal:** Complete auth flow with GitHub OAuth + email/password
**Estimated Sessions:** 2-3

### Chunk 1.1: Database Schema + Models

```python
# Claude Code should create:
1. Alembic setup and initial migration
2. SQLAlchemy models: User, Session
3. Pydantic schemas: UserCreate, UserResponse, TokenResponse
4. Database connection utilities
```

**Success Criteria:**

- [x] `alembic upgrade head` creates tables ✅
- [x] Models match schema in memory file ✅

### Chunk 1.2: NextAuth Integration

```typescript
# Claude Code should create:
1. NextAuth configuration (app/api/auth/[...nextauth]/route.ts)
2. GitHub OAuth provider setup
3. Credentials provider for email/password
4. Session handling with JWT
5. Protected route middleware
```

**Success Criteria:**

- [x] GitHub OAuth login works ✅
- [x] Email/password login works ✅
- [x] Protected routes redirect to login ✅

### Chunk 1.3: Auth API Endpoints

```python
# Claude Code should create:
1. POST /api/v1/auth/register
2. POST /api/v1/auth/login
3. POST /api/v1/auth/refresh
4. POST /api/v1/auth/logout
5. GET /api/v1/auth/me
6. JWT utilities (create, verify, refresh)
7. Password hashing with bcrypt
```

**Success Criteria:**

- [x] All endpoints return correct responses ✅
- [x] Tokens expire correctly ✅
- [x] Rate limiting works (100/hr free tier) ✅

### Chunk 1.4: Auth UI Components

```typescript
# Claude Code should create:
1. Login page with form
2. Signup page with form
3. OAuth buttons (GitHub, Google)
4. Form validation with Zod
5. Error handling and loading states
```

**Success Criteria:**

- [x] Login/signup forms validate input ✅
- [x] OAuth buttons trigger auth flow ✅
- [x] Errors display correctly ✅

---

## PHASE 2: CORE UI LAYOUT

**Goal:** Three-panel responsive layout with navigation
**Estimated Sessions:** 2

### Chunk 2.1: Layout Foundation

```typescript
# Claude Code should create:
1. Root layout with providers (auth, query, theme)
2. Navigation bar component
3. Three-panel resizable layout (react-resizable-panels)
4. Responsive breakpoints (mobile collapse to tabs)
```

**Success Criteria:**

- [ ] Layout renders on all screen sizes
- [ ] Panels are resizable
- [ ] Navigation shows user state

### Chunk 2.2: UI Component Library

```typescript
# Claude Code should set up:
1. Shadcn/ui initialization
2. Core components: Button, Input, Card, Badge, Tabs, Dialog
3. Custom components: ChallengePanel, AIWorkspace, ResourcesPanel
4. Theme provider (dark mode support)
```

**Success Criteria:**

- [ ] All Shadcn components importable
- [ ] Dark mode toggle works
- [ ] Custom components render correctly

### Chunk 2.3: Dashboard Page

```typescript
# Claude Code should create:
1. Dashboard layout with track cards
2. Progress summary component
3. Streak display
4. Quick actions (continue challenge, etc.)
```

**Success Criteria:**

- [ ] Dashboard shows user progress
- [ ] Track cards link to challenges
- [ ] Mobile responsive

---

## PHASE 3: CHALLENGE SYSTEM

**Goal:** Challenge CRUD, display, and test infrastructure
**Estimated Sessions:** 3-4

### Chunk 3.1: Challenge Database + API

```python
# Claude Code should create:
1. SQLAlchemy models: Track, Challenge, Submission, Progress
2. Pydantic schemas for all entities
3. GET /api/v1/tracks
4. GET /api/v1/tracks/{id}/challenges
5. GET /api/v1/challenges/{id}
6. GET /api/v1/challenges/{id}/hints/{n}
```

**Success Criteria:**

- [ ] Tracks and challenges CRUD works
- [ ] Hints return progressively
- [ ] Model matches schema in memory file

### Chunk 3.2: Challenge Panel Component

```typescript
# Claude Code should create:
1. ChallengePanel component (title, description, requirements)
2. RequirementsList with checkmarks
3. ConstraintsList component
4. HintButton with progressive reveal
5. Difficulty badge component
```

**Success Criteria:**

- [ ] Panel displays all challenge data
- [ ] Hints reveal on click
- [ ] Requirements update on test results

### Chunk 3.3: Monaco Editor Integration

```typescript
# Claude Code should create:
1. Monaco Editor wrapper component
2. Language detection based on challenge
3. Editor state management (Zustand)
4. Auto-save to localStorage
5. Syntax highlighting themes
```

**Success Criteria:**

- [ ] Editor loads with correct language
- [ ] Content persists on refresh
- [ ] Theme matches app theme

### Chunk 3.4: Challenge Data Seeding

```python
# Claude Code should create:
1. Seed script for 15 Web Track challenges
2. Challenge JSON files with requirements, tests, hints
3. Reference solutions (for test validation)
4. Migration to load seed data
```

**Challenges to seed:**

1. Profile Card (HTML/CSS)
2. Responsive Nav Bar
3. Pricing Table
4. Hero Section with CTA
5. Red Team: Accessibility Audit
6. Form Validation (JS)
7. Accordion Component
8. Modal with Keyboard Nav
9. Dark Mode Toggle
10. Red Team: XSS Vulnerability
11. React Card Component
12. useState Counter
13. useEffect API Fetch
14. Controlled Form
15. Red Team: Code Review

**Success Criteria:**

- [ ] All 15 challenges in database
- [ ] Each has 3 hints
- [ ] Test configs defined

---

## PHASE 4: SANDBOX & TEST EXECUTION

**Goal:** Isolated code execution with test results
**Estimated Sessions:** 3-4

### Chunk 4.1: Docker Sandbox Images

```dockerfile
# Claude Code should create:
1. docker/web-sandbox/Dockerfile (Node + Playwright + Lighthouse)
2. docker/data-sandbox/Dockerfile (Python + pandas)
3. docker/cloud-sandbox/Dockerfile (AWS CLI + Terraform)
4. Build scripts for all images
```

**Success Criteria:**

- [ ] All images build successfully
- [ ] Images are < 1GB each
- [ ] Security hardened (non-root user)

### Chunk 4.2: Test Runner Service

```python
# Claude Code should create:
1. TestRunner class with Docker SDK
2. Container lifecycle management
3. Timeout and resource limit enforcement
4. Result parsing (Playwright JSON, pytest output)
5. POST /api/v1/challenges/{id}/submit
6. GET /api/v1/challenges/{id}/results
```

**Success Criteria:**

- [ ] Code runs in isolated container
- [ ] Tests return pass/fail results
- [ ] Container cleans up after execution
- [ ] Timeout kills runaway processes

### Chunk 4.3: Test Result UI

```typescript
# Claude Code should create:
1. TestResults component
2. Progress bar for test execution
3. Pass/fail indicators per test
4. Error message display
5. Score calculation display
```

**Success Criteria:**

- [ ] Results update in real-time
- [ ] Errors are human-readable
- [ ] Score matches requirements

### Chunk 4.4: Preview & Terminal

```typescript
# Claude Code should create:
1. PreviewFrame component (iframe sandbox)
2. Terminal component (xterm.js)
3. Tabs to switch between preview/terminal
4. Console log capture
```

**Success Criteria:**

- [ ] HTML/CSS renders in preview
- [ ] Terminal shows command output
- [ ] Console errors display

---

## PHASE 5: AI INTEGRATION

**Goal:** Local + Cloud AI with anti-blind-prompting
**Estimated Sessions:** 3-4

### Chunk 5.1: Ollama Client

```python
# Claude Code should create:
1. OllamaClient class with streaming
2. Message formatting for chat
3. Connection health check
4. Fallback handling when Ollama unavailable
```

**Success Criteria:**

- [ ] Streaming responses work
- [ ] 60-second timeout enforced
- [ ] Graceful failure handling

### Chunk 5.2: Claude Client

```python
# Claude Code should create:
1. ClaudeClient class with Anthropic SDK
2. Streaming response handling
3. Token counting
4. Rate limit handling
```

**Success Criteria:**

- [ ] Streaming works with Claude API
- [ ] Token usage tracked
- [ ] Rate limits respected

### Chunk 5.3: AI Router Service

```python
# Claude Code should create:
1. AIRouter class with model selection logic
2. Anti-blind-prompting validation
3. Model tier progression check
4. POST /api/v1/ai/chat (SSE streaming)
5. GET /api/v1/ai/conversations/{id}
6. GET /api/v1/ai/usage
```

**Success Criteria:**

- [ ] Correct model selected per user/challenge
- [ ] Lazy prompts rejected with helpful message
- [ ] Conversation history persisted

### Chunk 5.4: AI Chat UI

```typescript
# Claude Code should create:
1. ChatMessages component
2. ChatInput with approach prompt
3. useAIChat hook with streaming
4. ApproachModal (pre-generation check)
5. Message formatting (code blocks, etc.)
```

**Success Criteria:**

- [ ] Messages stream in real-time
- [ ] Approach modal blocks lazy prompts
- [ ] Code blocks render with syntax highlighting

### Chunk 5.5: Anti-Blind-Prompting System

```typescript
# Claude Code should create:
1. Pre-generation approach prompt UI
2. Post-generation comprehension quiz
3. "Vibe Gap" tracker component
4. Prompt quality scoring display
```

**Success Criteria:**

- [ ] Users must explain before AI generates
- [ ] Comprehension check appears after generation
- [ ] Vibe Gap shows prediction vs reality

---

## PHASE 6: PROGRESS & GAMIFICATION

**Goal:** Track completion, streaks, certificates
**Estimated Sessions:** 2

### Chunk 6.1: Progress Service

```python
# Claude Code should create:
1. Progress tracking logic
2. Streak calculation
3. Model tier unlock logic
4. GET /api/v1/progress
5. GET /api/v1/progress/tracks/{id}
6. GET /api/v1/progress/streaks
```

**Success Criteria:**

- [ ] Progress updates on submission
- [ ] Streaks calculate correctly
- [ ] Model unlocks at thresholds

### Chunk 6.2: Certificate System

```python
# Claude Code should create:
1. Certificate generation (PDF with reportlab)
2. Certificate verification endpoint
3. GET /api/v1/certificates
4. GET /api/v1/certificates/{id}/pdf
```

**Success Criteria:**

- [ ] PDF generates with user name and track
- [ ] Verification code works
- [ ] PDF downloads correctly

### Chunk 6.3: Progress UI

```typescript
# Claude Code should create:
1. ProgressDashboard component
2. StreakDisplay component
3. CertificateCard component
4. UnlockNotification component
```

**Success Criteria:**

- [ ] Progress bar shows completion
- [ ] Streak displays correctly
- [ ] Certificate download works

---

## PHASE 7: PAYMENTS (Month 3)

**Goal:** Stripe integration with tier management
**Estimated Sessions:** 2

### Chunk 7.1: Stripe Backend

```python
# Claude Code should create:
1. Stripe webhook handler
2. Subscription creation
3. Tier upgrade logic
4. POST /api/v1/payments/create-checkout
5. POST /api/v1/payments/webhook
```

**Success Criteria:**

- [ ] Checkout session creates
- [ ] Webhook updates user tier
- [ ] Subscription cancellation works

### Chunk 7.2: Pricing UI

```typescript
# Claude Code should create:
1. PricingPage component
2. PricingCard components (Free/Pro/Team)
3. Checkout redirect
4. Subscription management page
```

**Success Criteria:**

- [ ] Pricing page displays tiers
- [ ] Checkout flow works
- [ ] User can cancel subscription

---

## PHASE 8: DATA TRACK (Month 2)

**Goal:** Jupyter integration + SQL challenges
**Estimated Sessions:** 3

### Chunk 8.1: Data Sandbox

```python
# Claude Code should create:
1. Jupyter kernel integration
2. Dataset management system
3. SQL sandbox with PostgreSQL
4. Query validation system
```

### Chunk 8.2: Data Challenge Seeding

```python
# Seed 15 Data Track challenges:
1-5: Data cleaning (missing values, deduplication, etc.)
6-10: SQL (JOINs, window functions, aggregations)
11-15: Analysis (correlation, A/B testing, cohort analysis)
```

---

## PHASE 9: CLOUD TRACK (Month 3)

**Goal:** LocalStack integration for AWS challenges
**Estimated Sessions:** 3

### Chunk 9.1: LocalStack Setup

```yaml
# Claude Code should create:
1. docker-compose for LocalStack
2. LocalStackClient wrapper
3. Environment provisioning scripts
4. Teardown automation
```

### Chunk 9.2: Cloud Challenge Seeding

```python
# Seed 15 Cloud Track challenges:
1-5: Deploy basics (S3, Lambda, API Gateway)
6-10: Docker (containerize, push, deploy)
11-15: CI/CD (GitHub Actions, monitoring)
```

---

## TESTING STRATEGY (Throughout)

### Unit Tests (70%)

- Frontend: Vitest + Testing Library
- Backend: pytest

### Integration Tests (20%)

- API endpoint tests with TestClient
- Database integration tests

### E2E Tests (10%)

- Playwright for critical user flows:
  - Signup → First challenge → Completion
  - AI chat → Code → Submit → Results
  - Payment → Upgrade → Access check

---

## DEPLOYMENT CHECKLIST

### Staging

- [ ] Vercel preview deployments for PRs
- [ ] Railway staging environment
- [ ] Staging database (separate Supabase project)

### Production

- [ ] Vercel production deployment
- [ ] Railway production (auto-deploy on main)
- [ ] Database migrations automated
- [ ] Environment variables configured
- [ ] Monitoring: Sentry + PostHog

---

## SESSION WORKFLOW FOR CLAUDE CODE

```
1. Start session: Load CLAUDE_MEMORY.md
2. Identify current chunk from this plan
3. Read chunk requirements carefully
4. Implement code incrementally
5. Test each piece before moving on
6. Commit with conventional commits (feat/fix/docs/test)
7. Mark success criteria as complete
8. Document any blockers or changes
9. End session with summary of progress
```

---

## ERROR RECOVERY

If a chunk fails:

1. Check error logs
2. Verify dependencies installed
3. Check environment variables
4. Review memory file for correct specs
5. Isolate failing component
6. Fix and re-test before continuing

---

## NOTES FOR CLAUDE CODE

- **Always test before moving on.** Each chunk builds on previous chunks.
- **Keep components small.** Easier to debug and modify.
- **Use TypeScript strictly.** No `any` types.
- **Follow the schema.** Database models must match memory file.
- **Security first.** Sandbox isolation, input validation, rate limiting.
- **Document as you go.** Comments for complex logic.
