# WeaktoStrong: AI Supervision Training Platform

> **Current Status**: 🚧 **Foundation Complete - Integration Required (4-6 weeks to launch)**

Train AI supervisors, not AI consumers. Learn to supervise AI effectively through hands-on challenges, precision prompting, and verification techniques.

## 🎯 **Current Status: Foundation Built, Integration Needed**

### ✅ **What's Complete (40% Overall)**

- **✅ Code Architecture**: Comprehensive FastAPI + Next.js foundation
- **✅ Database Models**: All models defined with Alembic migrations
- **✅ API Endpoints**: Complete REST API with authentication
- **✅ Frontend Components**: React components and UI library
- **✅ AI Integration**: Claude + Ollama client implementations
- **✅ Payment System**: Stripe integration with webhooks

### 🚧 **What's Needed for Launch**

- **❌ Environment Setup**: Configure database, Redis, API keys
- **❌ Service Integration**: Connect external services (Stripe, Claude, GitHub)
- **❌ Docker Builds**: Build sandbox execution environments
- **❌ Data Population**: Seed challenges and test content
- **❌ End-to-End Testing**: Verify complete user flows
- **❌ Feature Enablement**: Enable disabled features via environment flags

**📖 See [HANDOVER.md](./HANDOVER.md) for complete technical setup guide**

## 🏗️ **Platform Architecture**

```
┌─────────────────────────────────────────────────────┐
│ FRONTEND: Next.js 14 + NextAuth + Tailwind         │
│ ├─ Three-panel resizable layout                    │
│ ├─ Multi-track learning interface                  │
│ └─ Real-time progress tracking                     │
├─────────────────────────────────────────────────────┤
│ BACKEND: FastAPI + SQLAlchemy + PostgreSQL          │
│ ├─ Multi-track challenge system                    │
│ ├─ AI routing with anti-blind-prompting            │
│ ├─ Progress tracking and certificates              │
│ └─ Stripe payment integration                      │
├─────────────────────────────────────────────────────┤
│ SANDBOX ENVIRONMENTS (Docker-based):               │
│ ├─ Web: Node.js + Playwright testing              │
│ ├─ Data: Python + Jupyter + SQL                   │
│ └─ Cloud: LocalStack + Terraform + AWS            │
├─────────────────────────────────────────────────────┤
│ AI INTEGRATION:                                     │
│ ├─ Local: Ollama (Llama models)                   │
│ ├─ Cloud: Anthropic Claude (tier-based)           │
│ └─ Anti-blind-prompting system                    │
└─────────────────────────────────────────────────────┘
```

## 📚 **Planned Learning Tracks (45 Total Challenges)**

### 🌐 **Web Track (15 Challenges)**

- **Beginner**: HTML/CSS fundamentals, responsive design
- **Intermediate**: JavaScript interactivity, React components
- **Advanced**: Performance optimization, accessibility
- **Security**: XSS prevention, security audits

### 📊 **Data Track (15 Challenges)**

- **Beginner**: Data cleaning, SQL basics
- **Intermediate**: Advanced SQL, aggregations
- **Advanced**: ML modeling, statistical analysis
- **Security**: SQL injection prevention, GDPR compliance

### ☁️ **Cloud Track (15 Challenges)**

- **Beginner**: S3, Lambda, Docker basics
- **Intermediate**: VPC, ECS, Infrastructure as Code
- **Advanced**: Kubernetes, CI/CD pipelines
- **Security**: Infrastructure security assessment

## 🚀 **Quick Development Setup**

### Prerequisites

- Node.js 18+ and Python 3.11+
- PostgreSQL and Redis
- Docker for sandbox environments

### 1. Install Dependencies

```bash
npm install
cd backend && pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment templates
cp .env.example .env
cp apps/web/.env.local.example apps/web/.env.local

# Edit both files with real values (see HANDOVER.md)
```

### 3. Database Setup

```bash
# Start services
docker-compose up -d postgres redis

# Run migrations
cd backend && alembic upgrade head
```

### 4. Start Development

```bash
npm run dev  # Starts both frontend (3000) and backend (8000)
```

## 🔧 **Critical Setup Steps**

### **Week 1: Basic Setup**

1. Configure PostgreSQL database
2. Set up Redis for caching
3. Update environment variables with real values
4. Verify basic frontend-backend connection

### **Week 2: External Services**

1. Set up GitHub OAuth app
2. Configure Anthropic Claude API
3. Set up Stripe account (if payments needed)
4. Enable feature flags in environment

### **Week 3: Sandbox Environment**

1. Build Docker images for code execution
2. Test challenge submission and execution
3. Populate database with challenge content
4. Verify security isolation

### **Week 4: Integration & Testing**

1. Test complete user journeys
2. Verify AI chat functionality
3. Test payment flows (if enabled)
4. Performance optimization and bug fixes

## 📋 **Environment Variables Required**

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/weaktostrong
REDIS_URL=redis://localhost:6379

# API Keys (replace placeholders)
ANTHROPIC_API_KEY=sk-ant-... (real key needed)
GITHUB_ID=Ov23li... (real OAuth app ID needed)
GITHUB_SECRET=... (real OAuth secret needed)
STRIPE_SECRET_KEY=sk_test_... (real Stripe key needed)

# Feature Flags (enable as needed)
ENABLE_PAYMENTS=true
ENABLE_CERTIFICATES=true
ENABLE_DATA_TRACK=false  # Optional
ENABLE_CLOUD_TRACK=false # Optional

# Security
JWT_SECRET_KEY=your-secure-random-string
```

### Frontend (.env.local)

```bash
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secure-random-string
GITHUB_ID=... (same as backend)
GITHUB_SECRET=... (same as backend)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 **Testing Commands**

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd apps/web && npm test

# Build verification
npm run build

# Linting
npm run lint
```

## 🚨 **Known Issues & Quick Fixes**

### Issue 1: Database Connection

- **Problem**: PostgreSQL connection errors
- **Fix**: Verify PostgreSQL is running and DATABASE_URL is correct

### Issue 2: API Key Errors

- **Problem**: External service 401 errors
- **Fix**: Replace placeholder API keys with real values

### Issue 3: Docker Image Missing

- **Problem**: "image not found" errors in code execution
- **Fix**: Build Docker images or update image names in code

### Issue 4: Feature Not Working

- **Problem**: Core features seem broken
- **Fix**: Check feature flags in .env - many are disabled by default

## 🎯 **Success Criteria**

### **Week 1**: Basic Platform Running

- [ ] Frontend and backend start without errors
- [ ] Database connection working
- [ ] User can register and login

### **Week 2**: Core Features Working

- [ ] AI chat responds to user input
- [ ] Challenge data loads in interface
- [ ] Basic code submission working

### **Week 4**: Launch Ready

- [ ] Complete user journey functional
- [ ] All enabled features working
- [ ] Performance meets targets
- [ ] Ready for user testing

## 📞 **Next Steps**

1. **Read [HANDOVER.md](./HANDOVER.md)** - Complete technical setup guide
2. **Set up development environment** - Follow quick setup above
3. **Configure external services** - Get real API keys and credentials
4. **Build and test** - Verify each component works independently
5. **Integration testing** - Test complete user workflows
6. **Launch preparation** - Performance optimization and monitoring

---

**This platform has strong technical foundations and excellent market potential. The architecture is production-ready - focus on configuration and integration to bring it to life.** 🚀
