# Deployment Checklist

## ✅ Pre-Deployment

- [ ] Update GitHub PAT with workflow scope
- [ ] Test CI/CD pipeline passes
- [ ] Environment variables documented

## ✅ Frontend (Vercel)

- [ ] Connect GitHub repository
- [ ] Configure environment variables
- [ ] Set build command: `cd apps/web && npm run build`
- [ ] Set output directory: `apps/web/.next`
- [ ] Deploy and test

## ✅ Backend (Railway)

- [ ] Connect GitHub repository
- [ ] Add PostgreSQL service
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Deploy and test health endpoint

## ✅ Database (Supabase)

- [ ] Create production project
- [ ] Update connection strings
- [ ] Run migrations: `alembic upgrade head`
- [ ] Test database connectivity

## ✅ Services

- [ ] Set up Redis (Upstash)
- [ ] Configure monitoring (optional)
- [ ] Set up custom domain (optional)

## ✅ Testing

- [ ] Test authentication flow end-to-end
- [ ] Verify GitHub OAuth works
- [ ] Test API endpoints
- [ ] Check error logging

## Production URLs

- Frontend: https://your-app.vercel.app
- Backend: https://your-backend.railway.app
- Database: Supabase connection string
- Redis: Upstash connection string
