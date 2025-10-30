# HF Virtual Stylist - Complete Setup Guide

## 📚 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Fabric Swatch System](#fabric-swatch-system)
4. [Color Organization Pipeline](#color-organization-pipeline)
5. [Deployment Guide](#deployment-guide)
6. [Troubleshooting](#troubleshooting)

---

## Project Overview

**HF Virtual Stylist** is an AI-powered digital suit styling and visualization application that generates photorealistic suit renders using Stable Diffusion XL. Sales associates select fabrics and colors, and the system produces SDXL-powered visualizations.

### Tech Stack
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL (Neon) + Alembic migrations
- **Frontend:** Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **AI/ML:** Stable Diffusion XL + ControlNet + IP-Adapter
- **Storage:** Cloudflare R2 (for swatches and generated images)
- **Deployment:** Railway (backend) + Vercel (frontend)

### Key Features
- ✅ 83 fabric swatches organized by color family
- ✅ AI-powered color detection and categorization
- ✅ Photorealistic suit generation with pose control
- ✅ Job-based async generation with polling
- ✅ Admin dashboard for fabric management
- ✅ Responsive mobile-friendly UI

---

## Architecture

### System Flow
```
User Selection → Frontend → Backend API → Job Queue → SDXL Pipeline → R2 Storage → Display
     ↓                                         ↓
Catalog API ← Database ← Color Analysis ← R2 Swatches
```

### Component Overview

**Backend** (`backend/`)
```
app/
├── admin/              # Admin auth, CRUD, schemas
├── core/               # Config, database session
├── models/             # Pydantic schemas
├── routers/            # FastAPI route handlers
│   ├── catalog.py      # Public catalog endpoint
│   └── generate.py     # Generation job endpoints
├── services/           # Business logic
│   ├── generator.py    # SDXL generation
│   └── storage.py      # R2/local storage
└── data/               # Seed data (fabrics.json)
```

**Frontend** (`frontend/`)
```
src/
├── app/                # Next.js App Router
│   ├── page.tsx        # Main stylist UI
│   └── admin/          # Admin dashboard
├── components/         # React components
│   ├── CatalogSelector.tsx    # Fabric/color picker
│   └── GeneratedImageGallery.tsx
├── hooks/              # Custom React hooks
│   └── useVirtualStylist.ts   # State management
└── lib/                # API clients
    ├── apiClient.ts    # Public API
    └── adminApi.ts     # Admin API
```

---

## Fabric Swatch System

### R2 Bucket Structure
```
R2 Bucket: harris-and-frank
Public URL: https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev

├── ZEGNA 2025-26/          ← 83 fabric swatches (PNG, ~1-1.5 MB each)
│   ├── 095T-0121.png
│   ├── 095T-0132.png
│   ├── 33125.png
│   └── ... (80 more)
└── generated/              ← AI-generated images
    └── {family_id}/{color_id}/{run_id}/{cut}.jpg
```

**Important Path Notes:**
- ❌ **NOT** `harris-and-frank/ZEGNA 2025-26/` (nested)
- ✅ **IS** `ZEGNA 2025-26/` (root level of bucket)

### Database Schema

**FabricFamily Table:**
```sql
CREATE TABLE fabric_families (
    id INTEGER PRIMARY KEY,
    family_id VARCHAR UNIQUE NOT NULL,  -- e.g., "azules", "grises"
    display_name VARCHAR NOT NULL,       -- e.g., "Azules", "Grises"
    status VARCHAR NOT NULL DEFAULT 'active'
);
```

**Color Table:**
```sql
CREATE TABLE colors (
    id INTEGER PRIMARY KEY,
    fabric_family_id INTEGER REFERENCES fabric_families(id) ON DELETE CASCADE,
    color_id VARCHAR UNIQUE NOT NULL,    -- e.g., "az-095T-0121"
    name VARCHAR NOT NULL,                -- e.g., "Azul Oscuro"
    hex_value VARCHAR NOT NULL,           -- e.g., "#0A1D3A"
    swatch_code VARCHAR,                  -- e.g., "095T-0121" (R2 filename)
    swatch_url VARCHAR                    -- Auto-generated or explicit URL
);
```

### URL Generation

**Automatic (preferred):** Set `swatch_code` and the API builds the URL:

```python
# backend/app/routers/catalog.py:53-56
if c.swatch_code and settings.r2_public_url:
    swatch_path = f"ZEGNA%202025-26/{quote(c.swatch_code)}.png"
    swatch_url = f"{settings.r2_public_url}/{swatch_path}"
```

**Manual (fallback):** Set `swatch_url` directly in database.

**Generated URL Example:**
```
https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/ZEGNA%202025-26/095T-0121.png
```

### Frontend Integration

The `CatalogSelector` component (`frontend/src/components/CatalogSelector.tsx:51-66`) automatically handles swatch display:

```typescript
{color.swatch_url ? (
  <Image
    src={color.swatch_url}
    alt={color.name}
    fill
    className="object-cover"
    sizes="(max-width: 768px) 100px, 150px"
  />
) : (
  <div style={{ backgroundColor: color.hex }} />  // Fallback to hex
)}
```

**No frontend changes needed!**

---

## Color Organization Pipeline

### Overview
Automatically categorizes 50-100+ fabric swatches into color families using AI-powered color analysis.

### Process Flow
```
1. List Swatches (R2)
   ↓
2. Download & Analyze Colors (AI)
   ↓
3. Categorize into Families
   ↓
4. Generate Spanish Names
   ↓
5. Populate Database
```

### Scripts

#### 1. `list_r2_swatches.py` - List All Swatches

**Purpose:** Fetch all swatch filenames from R2 bucket

**Usage:**
```bash
python list_r2_swatches.py
```

**Output:**
- Console: List of all swatch codes with sizes
- File: `swatch_codes_list.txt`

**Example Output:**
```
📦 Listing swatches from bucket: harris-and-frank
📁 Folder: ZEGNA 2025-26/

✅ Found 83 swatch images:

  1. 095T-0121      (  1.38 MB)
  2. 095T-0132      (  1.43 MB)
  ...
 83. P993N-913P     (  0.91 MB)
```

#### 2. `organize_swatches_by_color.py` - AI Color Analysis

**Purpose:** Download swatches, analyze dominant colors, categorize into families

**Algorithm:**
1. **Download** swatch image from R2
2. **Crop** to center 70% (avoid borders/backgrounds)
3. **Filter** extreme brightness values (borders, flash)
4. **Extract** top 10 most frequent colors
5. **Weight** by saturation (prefer colorful over neutral)
6. **Convert** to HSV color space
7. **Categorize** by hue, saturation, and value
8. **Generate** Spanish color names

**Color Families:**
- **Azules** (Blues): H 190-250°, S > 0.2
- **Grises** (Grays): S < 0.12, V 0.25-0.75
- **Marrones y Beiges** (Browns): H 20-45°, S > 0.15
- **Negros y Blancos** (Black/White): V < 0.10 or V > 0.90 + S < 0.05
- **Verdes** (Greens): H 80-170°, S > 0.2
- **Tonos Cálidos** (Warm): H 0-20°, S > 0.3
- **Tonos Fríos** (Cool): H 250-290°, S > 0.2

**Usage:**
```bash
python organize_swatches_by_color.py
```

**Output:**
- Console: Real-time analysis progress
- File: `swatch_categorization.json`

**Example Output:**
```
🔍 Analyzing 83 swatches...
  1. 095T-0121      → azules          Azul Oscuro          #0A1D3A
  2. 095T-0132      → grises          Gris 52              #343434
  3. 33125          → marrones        Marrón               #C19A6B
 ...
 83. P993N-913P     → grises          Gris Claro           #E8E8E8

📊 Summary by Color Family:
Azules                    18 swatches
Grises                    22 swatches
Marrones y Beiges         20 swatches
Negros y Blancos           8 swatches
Verdes                     9 swatches
Tonos Cálidos              4 swatches
Tonos Fríos                2 swatches
```

**Algorithm Improvements (Latest):**
- ✅ Center-crop to avoid white borders
- ✅ Filter extreme brightness (20-235 range)
- ✅ Saturation-weighted color averaging
- ✅ Stricter black/white thresholds (0.10/0.90 vs 0.15/0.85)
- ✅ Top 10 colors for better accuracy

#### 3. `populate_color_families.py` - Database Population

**Purpose:** Create fabric families and colors in database from categorization

**Usage:**
```bash
# Preview first (recommended)
python populate_color_families.py --preview

# Populate database
python populate_color_families.py
```

**What it does:**
1. Reads `swatch_categorization.json`
2. Clears existing families/colors (optional)
3. Creates 7 fabric families
4. Creates ~83 color records
5. Sets `swatch_code` for each color
6. Commits to database

**Safety Features:**
- `--preview` flag to preview without changes
- Confirmation prompt before deletion
- Transaction rollback on errors

**Output:**
```
🎨 Fabric Family Population Script

⚠️  This will REPLACE all existing fabric families and colors!
   Continue? (yes/no): yes

🗑️  Clearing existing fabric families and colors...
✨ Creating new fabric families and colors...

📁 Azules (18 colors)
   └─ 095T-0121             Azul Oscuro               #0A1D3A
   └─ 1421-0617             Azul                      #000080
   ...

✅ Successfully created:
   Fabric families: 7
   Colors: 83
```

---

## Deployment Guide

### Railway (Backend)

**Prerequisites:**
- Railway account
- GitHub repo connected
- PostgreSQL (Neon) database provisioned

**Environment Variables:**
```env
# Database
DATABASE_URL=postgresql://user:pass@host/db

# Admin
ADMIN_PASSWORD=secure-password
JWT_SECRET=long-random-string
JWT_ALGORITHM=HS256

# Storage
STORAGE_BACKEND=r2
R2_ACCOUNT_ID=227469b74b82faacc40b017f9123aa27
R2_ACCESS_KEY_ID=5025ea72fa42e55d568f775f62f5ef63
R2_SECRET_ACCESS_KEY=945657b921de4459a6c0a70a33a685b8dbbb92b2ce0fa8ec4b6c2343678dfb62
R2_BUCKET_NAME=harris-and-frank
R2_PUBLIC_URL=https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev

# Generation (optional - for GPU pods)
CONTROLNET_ENABLED=1
IP_ADAPTER_ENABLED=1
...
```

**Deployment Steps:**
1. Push code to `main` branch
2. Railway auto-deploys
3. Run migrations: `alembic upgrade head`
4. Run organization scripts (see below)
5. Verify catalog endpoint

**Post-Deploy Tasks:**
```bash
# SSH into Railway container
railway shell

# Run migrations
python -m alembic upgrade head

# Organize swatches
python list_r2_swatches.py
python organize_swatches_by_color.py
python populate_color_families.py

# Verify
curl https://your-app.railway.app/catalog | jq '.families | length'
# Should return: 7
```

### Vercel (Frontend)

**Prerequisites:**
- Vercel account
- GitHub repo connected

**Environment Variables:**
```env
NEXT_PUBLIC_API_BASE=https://hf-virtual-stylist-production.up.railway.app
```

**Deployment:**
1. Push code to `main`
2. Vercel auto-deploys
3. Set environment variable in Vercel dashboard
4. Redeploy if needed

**Verification:**
```bash
# Test catalog from frontend
curl https://your-app.vercel.app/api/catalog | jq '.families[0].colors[0]'

# Should include swatch_url:
{
  "color_id": "az-095T-0121",
  "name": "Azul Oscuro",
  "hex": "#0A1D3A",
  "swatch_url": "https://pub-56...r2.dev/ZEGNA%202025-26/095T-0121.png"
}
```

---

## Troubleshooting

### Swatches Not Displaying (404 errors)

**Symptoms:**
```
⨯ upstream image response failed for https://pub-.../fabrics/095T-0121.png 404
```

**Causes & Solutions:**

1. **Wrong R2 path:**
   - ❌ `/fabrics/` or `/harris-and-frank/ZEGNA 2025-26/`
   - ✅ `/ZEGNA 2025-26/`
   - **Fix:** Run `python fix_swatch_paths.py`

2. **Missing `swatch_code` in database:**
   ```sql
   SELECT color_id, swatch_code FROM colors WHERE swatch_code IS NULL;
   ```
   - **Fix:** Re-run `populate_color_families.py`

3. **R2 not publicly accessible:**
   - Check Cloudflare R2 dashboard → Public Access settings
   - **Fix:** Enable public read or create public URL domain

4. **Wrong R2_PUBLIC_URL:**
   ```bash
   # Check .env
   echo $R2_PUBLIC_URL
   # Should be: https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev
   ```

### Color Detection Issues

**Problem:** Most swatches categorized as "Negros y Blancos"

**Cause:** White borders or backgrounds in swatch images

**Solution:** Algorithm already handles this (v2):
- ✅ Crops to center 70%
- ✅ Filters extreme brightness
- ✅ Weights by saturation

**If still issues:**
- Adjust thresholds in `organize_swatches_by_color.py`
- Manually edit `swatch_categorization.json`
- Re-run `populate_color_families.py`

### Database Migration Errors

**Error:** `Target database is not up to date`

**Solution:**
```bash
# Check current version
alembic current

# Apply all migrations
alembic upgrade head

# If issues, check migration history
alembic history --verbose
```

**Error:** `Multiple head revisions present`

**Solution:**
```bash
# Merge heads
alembic merge heads -m "merge migrations"
alembic upgrade head
```

### Frontend Not Loading Catalog

**Symptoms:** Empty color selector, loading forever

**Debugging:**
```bash
# Test backend directly
curl https://your-railway-app.railway.app/catalog

# Check browser console (F12)
# Look for CORS errors, 404s, or network failures

# Verify Next.js rewrites
# Check frontend/next.config.ts:
async rewrites() {
  return [{ source: "/api/:path*", destination: `${API_BASE}/:path*` }];
}
```

**Solutions:**
- Check `NEXT_PUBLIC_API_BASE` environment variable
- Restart frontend dev server
- Clear `.next` cache: `rm -rf .next`

---

## File Reference

### Backend Scripts
- `list_r2_swatches.py` - Lists all swatches from R2
- `organize_swatches_by_color.py` - AI color analysis
- `populate_color_families.py` - Database population
- `fix_swatch_paths.py` - Fixes incorrect swatch URLs
- `swatch_mapping.py` - Manual swatch code mapping (alternative)

### Generated Files
- `swatch_codes_list.txt` - Plain text list of codes
- `swatch_categorization.json` - Full analysis results with HSV values

### Documentation
- `COMPLETE_SETUP_GUIDE.md` - This file
- `ORGANIZE_SWATCHES_README.md` - Color organization details
- `SWATCH_SETUP.md` - Swatch system setup (legacy)
- `CLAUDE.md` - Project overview for AI assistant

---

## Latest Updates

### 2025-10-30: Path Corrections & Algorithm Improvements
- ✅ Fixed R2 path from `/fabrics/` to `/ZEGNA 2025-26/`
- ✅ Improved color detection algorithm (center crop, saturation weighting)
- ✅ Stricter black/white thresholds (0.10/0.90)
- ✅ Tested with 83 actual swatches from ZEGNA collection
- ✅ Railway backend successfully deployed
- ✅ Vercel frontend displaying swatch images

### 2025-10-29: Initial Swatch System
- ✅ Added `swatch_code` column to Color model
- ✅ Created Alembic migration
- ✅ Implemented automatic URL generation
- ✅ Created color organization pipeline

---

## Support & Contributing

**For Issues:**
1. Check this guide first
2. Review recent git commits
3. Check Railway/Vercel logs
4. Consult backend API documentation

**For Development:**
- Backend: `backend/README.md`
- Frontend: `frontend/CLAUDE.md`
- API Docs: `/docs` endpoint (FastAPI)

---

**Last Updated:** 2025-10-30
**Version:** 1.0.0
**Maintainers:** Development Team
