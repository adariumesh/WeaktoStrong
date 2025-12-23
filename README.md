# Weak-to-Strong: AI Supervision Training Platform

> **Phases 8 & 9 Complete! 🎉** Full multi-track platform with Web, Data Science, and Cloud Infrastructure learning paths.

Train AI supervisors, not AI consumers. Learn to supervise AI effectively through hands-on challenges, precision prompting, and verification techniques.

## 🚀 **Current Status: Phases 8 & 9 Complete - Full Multi-Track Platform**

**✅ Phase 0: Project Bootstrap** - Turborepo monorepo with Next.js 14 + FastAPI

**✅ Phase 1: Authentication System** - NextAuth + FastAPI JWT with OAuth

**✅ Phase 2: Core UI Layout** - Three-panel resizable layout with Shadcn/ui

**✅ Phase 3: Challenge System** - Challenge CRUD, display, and test infrastructure

**✅ Phase 4: Sandbox & Test Execution** - Isolated code execution with test results

**✅ Phase 5: AI Integration** - Local + Cloud AI with anti-blind-prompting system

**✅ Phase 5.5: Production Readiness** - Testing infrastructure, monitoring, and scalability

**✅ Phase 6: Progress & Gamification** - Complete tracking, certificates, and UI

**✅ Phase 7: Payments & Subscriptions** - Complete Stripe integration with billing management

**✅ Phase 8: Data Track** - Complete data science challenges with Jupyter and SQL

**✅ Phase 9: Cloud Track** - Complete cloud infrastructure challenges with AWS/LocalStack

### 🎯 **Latest Completion Highlights:**

**Phase 8 - Data Science Track:**

- **Jupyter Integration**: Complete data science environment with pandas, numpy, scikit-learn
- **SQL Sandbox**: PostgreSQL integration with comprehensive query challenges
- **15 Data Challenges**: Data cleaning → SQL mastery → ML modeling → GDPR compliance
- **Red Team Security**: SQL injection prevention and data privacy challenges

**Phase 9 - Cloud Infrastructure Track:**

- **LocalStack Integration**: Full AWS emulation for cloud development
- **Infrastructure as Code**: Terraform and CloudFormation deployment challenges
- **15 Cloud Challenges**: S3 basics → Kubernetes deployment → security assessment
- **Production Pipelines**: CI/CD, monitoring, and infrastructure security

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────┐
│ FRONTEND: Next.js 14 + NextAuth + Tailwind         │
│ ├─ Three-panel resizable layout (Challenge|Work|AI)│
│ ├─ Multi-track learning interface                  │
│ └─ Real-time progress and gamification UI          │
├─────────────────────────────────────────────────────┤
│ BACKEND: FastAPI + SQLAlchemy + PostgreSQL          │
│ ├─ Multi-track challenge system (Web/Data/Cloud)   │
│ ├─ Progress tracking and certificate generation    │
│ ├─ Stripe integration for subscriptions            │
│ └─ AI routing with anti-blind-prompting            │
├─────────────────────────────────────────────────────┤
│ SANDBOX ENVIRONMENTS:                               │
│ ├─ Web: Node.js + Playwright + Lighthouse          │
│ ├─ Data: Python + Jupyter + pandas + SQL           │
│ └─ Cloud: LocalStack + Terraform + Docker          │
├─────────────────────────────────────────────────────┤
│ AI INTEGRATION:                                     │
│ ├─ Local: Ollama + Llama 3.2 8B                    │
│ ├─ Cloud: Claude Haiku/Sonnet (tier-based)         │
│ └─ Anti-blind-prompting enforcement                │
└─────────────────────────────────────────────────────┘
```

## 📚 **Learning Tracks (45 Total Challenges)**

### 🌐 **Web Track (15 Challenges)**

- **Beginner**: HTML/CSS fundamentals, responsive design
- **Intermediate**: JavaScript interactivity, React components
- **Advanced**: Performance optimization, accessibility, PWAs
- **Red Team**: XSS prevention, security audits

### 📊 **Data Track (15 Challenges)**

- **Beginner**: Data cleaning, SQL basics, data validation
- **Intermediate**: Advanced SQL, aggregations, performance tuning
- **Advanced**: Statistical analysis, ML modeling, A/B testing
- **Red Team**: SQL injection prevention, GDPR compliance

### ☁️ **Cloud Track (15 Challenges)**

- **Beginner**: S3, Lambda, Docker basics
- **Intermediate**: VPC, ECS, Infrastructure as Code
- **Advanced**: Kubernetes, CI/CD, monitoring
- **Red Team**: Security assessment, infrastructure hardening

## 🛠️ **Quick Start**

### Prerequisites

- Node.js 18+ and Python 3.11+
- PostgreSQL and Redis (or use Docker)
- GitHub OAuth app configured

### 1. Install Dependencies

```bash
# Root dependencies
npm install

# Backend dependencies
cd backend
python -m pip install -r requirements.txt
cd ..
```

### 2. Environment Setup

```bash
# Frontend (.env.local)
cp apps/web/.env.local.example apps/web/.env.local

# Backend (.env)
cp backend/.env.example backend/.env
```

### 3. Start Services

```bash
# Option A: Docker (recommended)
docker-compose up -d postgres redis

# Option B: Local PostgreSQL & Redis
# (configure connection strings in .env files)
```

### 4. Database Setup

```bash
cd backend
alembic upgrade head
cd ..
```

### 5. Development Servers

```bash
# Start both frontend and backend
npm run dev

# Or individually:
npm run dev:web      # Frontend: http://localhost:3000
npm run dev:backend  # Backend: http://localhost:8000
```

## 🔐 **Authentication Flow**

### **GitHub OAuth (Working)**

- ✅ OAuth app configured: `Ov23ligZpEMxoOjbXjof`
- ✅ Callback URL: `http://localhost:3000/api/auth/callback/github`
- ✅ Auto-linking to existing accounts by email

### **Email/Password (Working)**

- ✅ bcrypt password hashing
- ✅ Email validation with Pydantic
- ✅ Account verification flow ready

### **JWT Tokens**

- ✅ 15-minute access tokens
- ✅ 7-day refresh tokens
- ✅ Automatic token refresh in NextAuth
- ✅ Rate limiting: 100 requests/hour (free tier)

## 📊 **API Endpoints (Ready)**

### Authentication

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - Email/password login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Current user info
- `POST /api/v1/auth/oauth/github` - GitHub OAuth handler

### Health & Info

- `GET /` - API status
- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation

## 🧪 **Testing**

```bash
# Test backend auth utilities
cd backend
python test_auth_endpoints.py

# Test API endpoints
python -c "from fastapi.testclient import TestClient; from main import app; print(TestClient(app).get('/health').json())"

# Test frontend build
npm run build

# Run linting
npm run lint              # Frontend
cd backend && ruff check . # Backend
```

## 📁 **Project Structure**

```
weak-to-strong/
├── apps/web/                    # Next.js frontend
│   ├── app/(auth)/             # Auth pages
│   │   ├── signin/page.tsx     # Login form
│   │   └── signup/page.tsx     # Registration form
│   ├── app/dashboard/          # Protected dashboard
│   ├── lib/auth.ts             # NextAuth configuration
│   └── middleware.ts           # Route protection
├── backend/                    # FastAPI backend
│   ├── app/api/v1/auth.py      # Auth endpoints
│   ├── app/core/               # Core utilities
│   │   ├── auth.py             # JWT & password utils
│   │   ├── database.py         # Database connection
│   │   └── deps.py             # FastAPI dependencies
│   ├── app/models/             # SQLAlchemy models
│   │   ├── user.py             # User model
│   │   └── session.py          # Session model
│   ├── app/schemas/            # Pydantic schemas
│   └── alembic/                # Database migrations
├── docker-compose.yml          # Local development services
├── scripts/                    # Setup automation
└── .github/workflows/          # CI/CD pipeline
```

## 🎯 **Next Phase: Core UI Layout**

**Phase 2 Goals:**

- Three-panel resizable layout (Challenge | Workspace | Resources)
- Shadcn/ui component library integration
- Responsive design with mobile-first approach
- Dark mode support with theme persistence

## 🔧 **Development Commands**

```bash
# Start everything
npm run dev               # Both servers + watch mode
npm run dev:web          # Frontend only (port 3000)
npm run dev:backend      # Backend only (port 8000)

# Building & Testing
npm run build            # Build all packages
npm run lint             # Lint all code
npm run typecheck        # TypeScript checking

# Backend specific
cd backend
python test_auth_endpoints.py  # Test auth utilities
uvicorn main:app --reload      # Start backend manually
alembic revision --autogenerate -m "description"  # New migration
alembic upgrade head           # Apply migrations

# Database
docker-compose up -d postgres redis  # Start services
docker-compose down               # Stop services
```

## 📝 **Environment Variables**

### Frontend (apps/web/.env.local)

```bash
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
GITHUB_ID=Ov23ligZpEMxoOjbXjof
GITHUB_SECRET=505e9d69ab3d0abae46b9f02ac15c09a7a03ec2d
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (backend/.env)

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weaktostrong
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-jwt-secret-here
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7
GITHUB_ID=Ov23ligZpEMxoOjbXjof
GITHUB_SECRET=505e9d69ab3d0abae46b9f02ac15c09a7a03ec2d
```

## 📚 **Additional Documentation**

- `CLAUDE_MEMORY.md` - Architecture & technical specifications
- `DEVELOPMENT_PLAN.md` - 9-phase systematic development plan
- `ENV_TEMPLATE.md` - Complete environment variable guide
- `AI_PROMPTS.md` - System prompts for AI features
- `CHALLENGE_CONTENT.md` - Challenge specifications

---

**🎉 Ready to test the complete authentication flow!**

Visit `http://localhost:3000` after running `npm run dev` to test GitHub OAuth and email registration.
