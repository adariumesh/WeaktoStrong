# WEAK-TO-STRONG: Environment Variables Template

> Copy to .env.local (frontend) and .env (backend)
>
> **📁 Part of context package.** See CLAUDE_MEMORY.md for architecture, DEVELOPMENT_PLAN.md Phase 0 for setup steps.
>
> **✅ Phase 1 Complete:** Authentication system fully configured with GitHub OAuth working credentials.

# ============================================

# DATABASE

# ============================================

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weaktostrong
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# ============================================

# REDIS

# ============================================

REDIS_URL=redis://localhost:6379

# For Upstash (production):

# REDIS_URL=rediss://default:PASSWORD@YOUR_HOST.upstash.io:6379

# ============================================

# AUTHENTICATION

# ============================================

NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32

# GitHub OAuth ✅ CONFIGURED

GITHUB_ID=Ov23ligZpEMxoOjbXjof
GITHUB_SECRET=505e9d69ab3d0abae46b9f02ac15c09a7a03ec2d

# Google OAuth (optional)

GOOGLE_ID=your_google_client_id
GOOGLE_SECRET=your_google_client_secret

# JWT Settings

JWT_SECRET=generate-with-openssl-rand-base64-64
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7

# ============================================

# AI SERVICES

# ============================================

# Ollama (local)

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:8b

# Anthropic Claude

ANTHROPIC_API_KEY=sk-ant-api03-...
CLAUDE_HAIKU_MODEL=claude-3-haiku-20240307
CLAUDE_SONNET_MODEL=claude-3-5-sonnet-20241022

# AI Rate Limits (tokens per day)

FREE_TIER_DAILY_TOKENS=10000
PRO_TIER_DAILY_TOKENS=100000

# ============================================

# STORAGE

# ============================================

S3_BUCKET=weak-to-strong-uploads
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# For LocalStack (development):

LOCALSTACK_ENDPOINT=http://localhost:4566
USE_LOCALSTACK=true

# ============================================

# PAYMENTS (Stripe)

# ============================================

STRIPE*SECRET_KEY=sk_test*...
STRIPE*PUBLISHABLE_KEY=pk_test*...
STRIPE*WEBHOOK_SECRET=whsec*...
STRIPE*PRICE_PRO=price*...
STRIPE*PRICE_TEAM=price*...

# ============================================

# MONITORING

# ============================================

SENTRY*DSN=https://...@sentry.io/...
POSTHOG_KEY=phc*...
POSTHOG_HOST=https://app.posthog.com

# ============================================

# FEATURE FLAGS

# ============================================

ENABLE_DATA_TRACK=false
ENABLE_CLOUD_TRACK=false
ENABLE_PAYMENTS=false
ENABLE_CERTIFICATES=false

# ============================================

# SANDBOX / DOCKER

# ============================================

DOCKER_HOST=unix:///var/run/docker.sock
SANDBOX_MEMORY_LIMIT=512m
SANDBOX_CPU_LIMIT=0.5
SANDBOX_TIMEOUT_SECONDS=300
SANDBOX_NETWORK_ENABLED=false

# ============================================

# DEVELOPMENT

# ============================================

DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
