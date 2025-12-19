# Weak-to-Strong: AI Supervision Training Platform

> **Phase 1 Complete! ✅** Authentication system with NextAuth + FastAPI is fully operational.

Train AI supervisors, not AI consumers. Learn to supervise AI effectively through hands-on challenges, precision prompting, and verification techniques.

## 🚀 **Current Status: Phase 1 Complete**

**✅ Phase 0: Project Bootstrap**

- Turborepo monorepo with Next.js 14 + FastAPI
- Docker Compose for local development
- CI/CD with GitHub Actions + Husky pre-commit hooks

**✅ Phase 1: Authentication System**

- Complete NextAuth integration (GitHub OAuth + email/password)
- FastAPI JWT-based API with rate limiting
- Protected routes with session handling
- User registration, login, logout, token refresh

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────┐
│ FRONTEND: Next.js 14 + NextAuth + Tailwind         │
│ ├─ GitHub OAuth + Email/Password Auth              │
│ ├─ Protected routes with middleware                │
│ └─ JWT session handling                             │
├─────────────────────────────────────────────────────┤
│ BACKEND: FastAPI + SQLAlchemy + PostgreSQL          │
│ ├─ JWT authentication with refresh tokens          │
│ ├─ Rate limiting (100 req/hr free tier)            │
│ ├─ Async database operations                       │
│ └─ RESTful API with OpenAPI docs                   │
├─────────────────────────────────────────────────────┤
│ DATABASE: PostgreSQL + Redis                       │
│ ├─ User management with OAuth linking              │
│ ├─ Session storage and caching                     │
│ └─ Alembic migrations                               │
└─────────────────────────────────────────────────────┘
```

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
