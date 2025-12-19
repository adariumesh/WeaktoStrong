# 🚀 Deployment Notes & TODO

## ✅ Vercel Environment Variables Set

| Variable              | Current Value                                  | Status   | Notes                               |
| --------------------- | ---------------------------------------------- | -------- | ----------------------------------- |
| `NEXTAUTH_SECRET`     | `l0vdSvSCfSjScLvCTG3LfgpebKaGvJqoDfTXUPOVh8E=` | ✅ Final | Generated with openssl              |
| `NEXTAUTH_URL`        | `https://weaktostrong-[random].vercel.app`     | ⚠️ TEMP  | **UPDATE after first deployment**   |
| `GITHUB_ID`           | `Ov23ligZpEMxoOjbXjof`                         | ✅ Final | GitHub OAuth App ID                 |
| `GITHUB_SECRET`       | `505e9d69ab3d0abae46b9f02ac15c09a7a03ec2d`     | ✅ Final | GitHub OAuth App Secret             |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000`                        | ⚠️ TEMP  | **UPDATE after Railway deployment** |

## 🔄 Required Updates After Deployment

### 1. After Vercel Frontend Deploys:

```bash
# Get the actual Vercel URL from deployment and update:
vercel env rm NEXTAUTH_URL production
vercel env add NEXTAUTH_URL production
# Enter: https://weaktostrong-ACTUAL-URL.vercel.app
```

### 2. After Railway Backend Deploys:

```bash
# Get the actual Railway URL and update:
vercel env rm NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend.railway.app
```

### 3. Update GitHub OAuth App Settings:

- Go to https://github.com/settings/applications/2464180
- Update "Authorization callback URL" to: `https://weaktostrong-ACTUAL-URL.vercel.app/api/auth/callback/github`

## 📋 Next Steps

1. ✅ Set Vercel env vars (completed)
2. 🔄 Deploy frontend with `vercel --prod`
3. 🔄 Deploy Railway backend
4. 🔄 Update URLs in env vars
5. 🔄 Update GitHub OAuth callback URL
6. ✅ Test end-to-end authentication

## 🔗 Important URLs

- **Vercel Dashboard:** https://vercel.com/umesh-adaris-projects/weaktostrong
- **GitHub OAuth App:** https://github.com/settings/applications/2464180
- **Railway Dashboard:** (TBD after setup)
- **Supabase Dashboard:** (TBD after setup)
