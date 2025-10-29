# Railway Deployment Instructions
**For: Person deploying HF Virtual Stylist backend**

## Prerequisites
- Railway account (sign up at https://railway.app)
- Access to GitHub repository: `hf-virtual-stylist`
- Credit card for Railway billing

---

## Step-by-Step Deployment

### 1. Create New Project
1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. If first time: Click **"Configure GitHub App"** to connect your GitHub
5. Select the **`hf-virtual-stylist`** repository
6. Railway will ask for **Root Directory** → enter: `backend`

### 2. Add Environment Variables
1. In your new Railway project, click **"Variables"** tab
2. Click **"New Variable"** and add each of these **one by one**:

```
DATABASE_URL
postgresql://neondb_owner:npg_gsrpD6Mdan7i@ep-weathered-pine-ahme9ks2-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require

STORAGE_BACKEND
r2

R2_ACCOUNT_ID
227469b74b82faacc40b017f9123aa27

R2_ACCESS_KEY_ID
5025ea72fa42e55d568f775f62f5ef63

R2_SECRET_ACCESS_KEY
945657b921de4459a6c0a70a33a685b8dbbb92b2ce0fa8ec4b6c2343678dfb62

R2_BUCKET_NAME
harris-and-frank

R2_PUBLIC_URL
https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev

ADMIN_PASSWORD
YourStrongPasswordHere123!

JWT_SECRET
your-very-long-random-secret-string-here-make-it-long

JWT_ALGORITHM
HS256

USE_MOCK_GENERATOR
false

APP_VERSION
1.0.0
```

**IMPORTANT**: Replace `ADMIN_PASSWORD` and `JWT_SECRET` with your own secure values!

### 3. Verify Configuration
1. Click **"Settings"** tab
2. Click **"Service"** section
3. Verify:
   - **Root Directory**: `backend`
   - Railway should auto-detect `railway.toml` configuration

### 4. Deploy
1. Click **"Deployments"** tab
2. Railway will automatically start building
3. Watch the **"Logs"** - you should see:
   ```
   Installing Python dependencies...
   Running alembic upgrade head...
   Starting uvicorn...
   Application startup complete
   ```
4. Wait for status to show **"Success"** (green checkmark)

### 5. Generate Public URL
1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Railway will give you a URL like: `hf-virtual-stylist-production.up.railway.app`
4. **COPY THIS URL** - send it to the frontend team

### 6. Verify Deployment
Test the health check endpoint:
```
https://your-railway-url.up.railway.app/healthz
```

Open in browser - should see:
```json
{"ok": true, "version": "1.0.0"}
```

### 7. Seed Database (First Time Only)
1. In Railway dashboard, find your project
2. Click the **"..."** menu (three dots)
3. Select **"Run a command"**
4. Enter: `python seed.py`
5. Click **"Run"**
6. This loads the initial fabric catalog

---

## Adding Collaborators (Optional)

To give the developer access without billing:
1. Go to **"Settings"** → **"Members"**
2. Click **"Invite Member"**
3. Enter developer's email
4. They'll get view/deploy access
5. **Billing stays on your account**

---

## Monitoring & Maintenance

### View Logs
- Click **"Deployments"** → Select latest deployment → **"View Logs"**

### Redeploy
- When code changes are pushed to GitHub, Railway auto-deploys
- Or manually: Click **"Deployments"** → **"..."** → **"Redeploy"**

### Stop/Pause Service
- **"Settings"** → **"Service"** → **"Remove Service"** (to stop billing)

---

## Costs

- **Free Tier**: $5 credit/month
- **Starter Plan**: $5/month after free credit
- **Backend cost**: ~$5-10/month depending on usage
- Monitor usage in **"Billing"** tab

---

## Troubleshooting

### Build Failed
- Check **Logs** for errors
- Verify all environment variables are set
- Verify root directory is `backend`

### Database Connection Error
- Check `DATABASE_URL` is correct
- Verify Neon database is running

### Health Check Failing
- Check **Logs** for startup errors
- Verify port is not hardcoded (Railway uses `$PORT` variable)

---

## Need Help?
Contact the developer with:
1. Screenshot of error
2. Relevant logs from Railway
3. Your Railway project URL

---

## Summary Checklist

- [ ] Railway account created
- [ ] Project created from GitHub repo
- [ ] Root directory set to `backend`
- [ ] All environment variables added (11 total)
- [ ] Deployment successful (green checkmark)
- [ ] Public domain generated
- [ ] Health check URL working
- [ ] Database seeded with `python seed.py`
- [ ] Public URL sent to frontend team
- [ ] Developer added as collaborator (optional)

**You're done! The backend is live.** 🚀
