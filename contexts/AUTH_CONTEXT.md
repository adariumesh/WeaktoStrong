# Auth System Context

> **Domain:** Authentication & User Management  
> **Context Size:** ~3K tokens  
> **Session Focus:** Auth improvements, user management, OAuth

## 📁 Files in This Domain

### Frontend Components

```
apps/web/app/auth/
├── signin/page.tsx              # Sign-in page
└── signup/page.tsx              # Sign-up page

apps/web/app/api/auth/
└── [...nextauth]/route.ts       # NextAuth API route

apps/web/lib/
├── auth.ts                      # NextAuth configuration
└── types/auth.ts                # Auth TypeScript types
```

### Backend Services

```
backend/app/api/v1/
└── auth.py                      # Auth API endpoints

backend/app/core/
├── auth.py                      # JWT utilities
└── deps.py                      # Auth dependencies

backend/app/models/
├── user.py                      # User model
└── session.py                   # Session model

backend/app/services/
└── auth.py                      # Auth business logic

backend/app/schemas/
└── auth.py                      # Pydantic auth schemas
```

## ⚡ Current Implementation Status

### ✅ Completed Features

- NextAuth integration with GitHub OAuth
- JWT token generation and validation
- User registration and login endpoints
- Password hashing with bcrypt
- Rate limiting (100 requests/hour)
- Session management
- Protected routes middleware
- Database models with Alembic migrations

### 🔧 Key Components

**NextAuth Configuration:**

- GitHub OAuth provider
- JWT strategy
- Session callbacks
- Custom sign-in/sign-up pages

**FastAPI Auth Service:**

- JWT token creation/validation
- Password hashing with salt
- Rate limiting per IP
- User CRUD operations
- Session management

**Database Schema:**

- Users table: id, email, password_hash, name, tier
- Sessions table: token, user_id, expires_at

## 🔌 API Endpoints

```python
# Authentication Endpoints
POST /api/v1/auth/register       # User registration
POST /api/v1/auth/login          # User login
POST /api/v1/auth/refresh        # Token refresh
POST /api/v1/auth/logout         # User logout
GET  /api/v1/auth/me             # Current user info
POST /api/v1/auth/oauth/github   # GitHub OAuth
```

## 🎯 Development Focus Areas

### Immediate Opportunities

- [ ] Password reset functionality
- [ ] Email verification
- [ ] Two-factor authentication
- [ ] Admin role management
- [ ] OAuth with Google

### Technical Improvements

- [ ] Refresh token rotation
- [ ] Session cleanup automation
- [ ] Auth event logging
- [ ] Rate limiting per user
- [ ] Account lockout protection

## 🔧 Development Commands

### Start Auth Development Session

```bash
npm run ctx auth                 # Load auth context
cd backend && python -m pytest test_auth_endpoints.py  # Run auth tests
```

### Common Auth Tasks

```bash
# Test auth endpoints
curl -X POST localhost:8000/api/v1/auth/register -d '{"email":"test@example.com","password":"test123"}'

# Check database
psql $DATABASE_URL -c "SELECT * FROM users LIMIT 5;"

# Test rate limiting
for i in {1..10}; do curl localhost:8000/api/v1/auth/me; done
```

### File Navigation

```bash
npm run find auth               # Find auth-related files
npm run find user               # Find user-related files
npm run find jwt                # Find JWT-related files
```

## 📊 Database Schema (Auth Tables Only)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    tier VARCHAR(20) DEFAULT 'free',
    tokens_used_today INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔐 Security Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your-nextauth-secret

# GitHub OAuth
GITHUB_ID=your-github-oauth-app-id
GITHUB_SECRET=your-github-oauth-app-secret

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Security Features

- Password hashing with bcrypt (cost factor 12)
- JWT tokens with short expiration
- Rate limiting by IP address
- CSRF protection
- Secure session cookies
- Input validation with Pydantic

## 🐛 Common Issues & Solutions

### Issue: JWT Token Expired

```bash
# Solution: Implement refresh token flow
POST /api/v1/auth/refresh
```

### Issue: Rate Limit Exceeded

```bash
# Solution: Check rate limit headers
curl -I localhost:8000/api/v1/auth/me
# Headers: X-RateLimit-Limit, X-RateLimit-Remaining
```

### Issue: GitHub OAuth Not Working

```bash
# Check environment variables
echo $GITHUB_ID $GITHUB_SECRET $NEXTAUTH_URL
```

---

**Quick Start:** `npm run ctx auth` to load this context for auth development sessions.
