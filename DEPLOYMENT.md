# Deployment Guide - Railway + Vercel

This guide covers deploying the HF Virtual Stylist application with Railway (backend) and Vercel (frontend).

## Architecture Overview

```
Frontend (Vercel)
    ↓ API calls
Backend (Railway)
    ↓ Database
Neon PostgreSQL
    ↓ Storage
Cloudflare R2
```

## Prerequisites

- [Railway account](https://railway.app)
- [Vercel account](https://vercel.com)
- [Neon PostgreSQL database](https://neon.tech) (already set up)
- [Cloudflare R2 bucket](https://www.cloudflare.com/products/r2/) (already set up)
- GitHub repository connected

---

## Backend Deployment (Railway)

### 1. Create New Railway Project

1. Go to [Railway](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Select the `backend` directory as the root

### 2. Configure Environment Variables

In Railway dashboard, go to **Variables** and add the following:

#### Database Configuration
```bash
DATABASE_URL=postgresql://neondb_owner:npg_gsrpD6Mdan7i@ep-weathered-pine-ahme9ks2-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
```

#### Storage Configuration
```bash
STORAGE_BACKEND=r2
R2_ACCOUNT_ID=227469b74b82faacc40b017f9123aa27
R2_ACCESS_KEY_ID=5025ea72fa42e55d568f775f62f5ef63
R2_SECRET_ACCESS_KEY=945657b921de4459a6c0a70a33a685b8dbbb92b2ce0fa8ec4b6c2343678dfb62
R2_BUCKET_NAME=harris-and-frank
R2_PUBLIC_URL=https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev
```

#### Authentication & Security
```bash
ADMIN_PASSWORD=your-strong-password-here
JWT_SECRET=your-long-random-secret-string-here
JWT_ALGORITHM=HS256
```

#### Generation Settings
```bash
USE_MOCK_GENERATOR=false
```

**Optional - SDXL Generation Settings** (if using GPU):
```bash
GUIDANCE=4.3
TOTAL_STEPS=80
USE_REFINER=1
REFINER_SPLIT=0.70
CONTROLNET_ENABLED=1
CONTROLNET_WEIGHT=1.15
IP_ADAPTER_ENABLED=1
IP_ADAPTER_SCALE=0.70
```

#### Application Settings
```bash
APP_VERSION=1.0.0
PUBLIC_BASE_URL=${{RAILWAY_PUBLIC_DOMAIN}}
```

### 3. Configure Build & Deploy

Railway should auto-detect the configuration from `railway.toml`, but verify:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Healthcheck Path**: `/healthz`

### 4. Set Up Domain (Optional)

1. Go to **Settings** > **Networking**
2. Click "Generate Domain" to get a Railway domain like: `your-app.railway.app`
3. Or add custom domain

### 5. Deploy

1. Click "Deploy" or push to main branch
2. Railway will:
   - Install dependencies
   - Run database migrations
   - Start the FastAPI server
3. Check logs for any errors
4. Test healthcheck: `https://your-app.railway.app/healthz`

### 6. Verify Deployment

```bash
# Test healthcheck
curl https://your-app.railway.app/healthz

# Test catalog endpoint
curl https://your-app.railway.app/catalog

# Should return: {"ok": true, "version": "1.0.0"}
```

---

## Frontend Deployment (Vercel)

### 1. Create New Vercel Project

1. Go to [Vercel](https://vercel.com)
2. Click "Add New..." > "Project"
3. Import your GitHub repository
4. Select the `frontend` directory as the root
5. Framework Preset: **Next.js**

### 2. Configure Environment Variables

In Vercel dashboard, go to **Settings** > **Environment Variables** and add:

#### Production
```bash
NEXT_PUBLIC_API_BASE=https://your-app.railway.app
```

#### Preview (optional - for PR deployments)
```bash
NEXT_PUBLIC_API_BASE=https://your-app.railway.app
```

#### Development (optional)
```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### 3. Configure Build Settings

Vercel should auto-detect Next.js, but verify:

- **Framework**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`
- **Root Directory**: `frontend`

### 4. Deploy

1. Click "Deploy"
2. Vercel will:
   - Install dependencies
   - Build Next.js app
   - Deploy to global CDN
3. Your app will be live at: `https://hf-virtual-stylist.vercel.app`

### 5. Configure Custom Domain (Optional)

1. Go to **Settings** > **Domains**
2. Add your custom domain
3. Configure DNS records as instructed

### 6. Verify Deployment

Visit your Vercel URL and test:
- Catalog loads
- Fabric selection works
- Image generation works
- Swatch images display

---

## Post-Deployment Tasks

### 1. Seed Database (First Time Only)

SSH into Railway or run locally:

```bash
# Connect to Railway
railway shell

# Run seed script
python seed.py
```

Or use Railway CLI:
```bash
railway run python seed.py
```

### 2. Update Frontend API URL

If you change the Railway URL, update Vercel environment variable:
```bash
NEXT_PUBLIC_API_BASE=https://new-railway-url.railway.app
```

Then redeploy frontend.

### 3. Test Full Flow

1. Visit frontend: `https://hf-virtual-stylist.vercel.app`
2. Select fabric family
3. Select color
4. Upload image
5. Generate visualization
6. Verify image displays

---

## Environment Variables Reference

### Backend (Railway) - Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `STORAGE_BACKEND` | Storage provider (local or r2) | `r2` |
| `R2_ACCOUNT_ID` | Cloudflare R2 account ID | `227469b74b82faacc40b017f9123aa27` |
| `R2_ACCESS_KEY_ID` | R2 access key | `5025ea72fa42e55d568f775f62f5ef63` |
| `R2_SECRET_ACCESS_KEY` | R2 secret key | `945657b921de4459a6c0a70a33a685b8db...` |
| `R2_BUCKET_NAME` | R2 bucket name | `harris-and-frank` |
| `R2_PUBLIC_URL` | R2 public URL | `https://pub-xxx.r2.dev` |
| `ADMIN_PASSWORD` | Admin panel password | `strong-password-123` |
| `JWT_SECRET` | JWT signing secret | `long-random-string` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |

### Backend (Railway) - Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_MOCK_GENERATOR` | Use mock generator instead of SDXL | `false` |
| `APP_VERSION` | Application version | `1.0.0` |
| `PUBLIC_BASE_URL` | Public backend URL | Railway domain |
| `GUIDANCE` | SDXL CFG scale | `4.3` |
| `TOTAL_STEPS` | SDXL inference steps | `80` |

### Frontend (Vercel) - Required

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE` | Backend API URL | `https://your-app.railway.app` |

---

## Troubleshooting

### Backend Issues

**Migration errors:**
```bash
# Reset database (destructive!)
railway run alembic downgrade base
railway run alembic upgrade head
```

**Image upload failing:**
- Check R2 credentials are correct
- Verify `STORAGE_BACKEND=r2`
- Test R2 bucket permissions

**CORS errors:**
- Verify Vercel URL is allowed in `app/main.py`
- Check frontend uses correct API URL

### Frontend Issues

**API calls failing:**
- Verify `NEXT_PUBLIC_API_BASE` is correct
- Check Railway backend is running
- Inspect browser console for errors

**Images not displaying:**
- Check R2 URL in `next.config.ts` remote patterns
- Verify swatch URLs in database are correct

**Build failures:**
- Check Node.js version (need 20+)
- Clear `.next` directory
- Verify all dependencies install

---

## Production Checklist

Before going live:

- [ ] Backend deployed to Railway
- [ ] Database migrations applied
- [ ] Database seeded with fabric data
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set on both platforms
- [ ] Custom domains configured (if applicable)
- [ ] CORS properly configured
- [ ] HTTPS enabled (automatic on Railway/Vercel)
- [ ] Health check endpoint responding
- [ ] Image storage working (R2)
- [ ] Full user flow tested
- [ ] Admin panel accessible and working
- [ ] Error monitoring configured (optional)

---

## Useful Commands

### Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run commands in Railway environment
railway run python seed.py

# SSH into container
railway shell
```

### Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod

# View logs
vercel logs

# List deployments
vercel list
```

---

## Security Best Practices

1. **Never commit secrets** - use environment variables
2. **Strong passwords** - use password managers
3. **Rotate secrets** - regularly update JWT_SECRET and API keys
4. **Monitor logs** - check for suspicious activity
5. **HTTPS only** - never use HTTP in production
6. **Rate limiting** - consider adding rate limits to API
7. **Input validation** - all inputs validated on backend

---

## Cost Optimization

### Railway
- Free tier: $5/month credit
- Backend with database: ~$5-10/month
- Monitor usage in dashboard

### Vercel
- Free tier: Generous for hobby projects
- Hobby plan: Free
- Pro plan: $20/month if needed

### Neon PostgreSQL
- Free tier: 0.5 GB storage
- Pro: $19/month for more storage/compute

### Cloudflare R2
- Free tier: 10 GB storage
- Very cheap beyond free tier

**Total estimated cost: $0-15/month** (depending on usage)

---

## Support

- Backend issues: Check `backend/README.md`
- Frontend issues: Check `frontend/CLAUDE.md`
- Deployment issues: Railway/Vercel documentation
- Database issues: Neon documentation
