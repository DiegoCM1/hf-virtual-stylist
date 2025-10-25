# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HF Virtual Stylist is a monorepo with a **FastAPI backend** (`backend/`) and a **Next.js 15 frontend** (`frontend/`) that generates photorealistic suit renders using Stable Diffusion XL. Sales associates select fabrics and colors, and the system produces SDXL-powered visualizations with optional ControlNet/IP-Adapter guidance.

## Repository Structure

```
backend/
├── app/
│   ├── admin/           # Admin CRUD, auth (JWT), schemas for fabric management
│   ├── core/            # config.py (Pydantic settings), database.py (SQLAlchemy session)
│   ├── models/          # Pydantic request/response schemas (catalog, generate)
│   ├── routers/         # FastAPI route handlers (catalog, generate, admin)
│   ├── services/        # Core logic: generator.py (SDXL), storage.py (local/R2), watermark.py
│   ├── data/            # fabrics.json (catalog metadata), swatch_mapping.csv
│   └── main.py          # FastAPI app initialization, CORS, static file mount
├── alembic/             # Database migrations
├── devops/runpod/       # deploy.sh for GPU pod deployment
├── storage/             # Local file storage (created at runtime)
├── tests/               # Pytest test suite
├── requirements.txt     # Python dependencies
├── seed.py              # Populates database from fabrics.json
└── alembic.ini          # Alembic configuration

frontend/
├── src/
│   ├── app/             # Next.js App Router pages (page.tsx, /admin)
│   ├── components/      # React components (gallery, modals, catalog selector)
│   ├── hooks/           # useVirtualStylist.ts (state machine for generation flow)
│   ├── lib/             # apiClient.ts (public API), adminApi.ts (admin API)
│   └── types/           # TypeScript type definitions
├── next.config.ts       # API proxy rewrites to backend
└── package.json         # Node scripts and dependencies
```

## Development Commands

### Backend (Python 3.11, FastAPI, SQLAlchemy)

**Environment Setup:**
1. Create `backend/.env` with required keys (see backend/README.md for full list):
   - `database_url=sqlite:///./storage/app.db`
   - `admin_password=change-me`
   - `jwt_secret=local-dev-secret`
   - `jwt_algorithm=HS256`
   - `storage_backend=local`
   - `public_base_url=http://localhost:8000/files`

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Seed initial data (optional):
   ```bash
   python seed.py
   ```

**Running the API:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Testing:**
```bash
cd backend
pytest -q
```

**Database Migrations:**
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Frontend (Next.js 15, React 19, TypeScript)

**Environment Setup:**
Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Running the dev server:**
```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

**Linting:**
```bash
npm run lint
```

**Building:**
```bash
npm run build
npm start  # Production server
```

## Architecture & Key Concepts

### Backend Architecture

**Request Flow:**
1. Client → Next.js `/api/*` proxy → FastAPI router
2. Router validates request (Pydantic schemas in `app/models/`)
3. Service layer (`app/services/`) handles business logic
4. Database operations via SQLAlchemy (`app/core/database.py`)
5. Response returned to client

**Generation Pipeline (app/services/generator.py):**
- `SdxlTurboGenerator`: Main production generator
  - Loads SDXL base model + optional refiner
  - Supports ControlNet (openpose, canny) for pose guidance
  - Supports IP-Adapter for fabric texture transfer
  - Watermarks outputs via `apply_watermark_image()`
  - Saves to storage backend (local or R2)
- `MockGenerator`: Lightweight fallback for testing (toggle via `USE_MOCK` in generate.py)

**Storage Backends (app/services/storage.py):**
- `LocalStorage`: Saves to `storage/` directory, URLs rewritten to `/files/*`
- `R2Storage`: Uploads to Cloudflare R2 using boto3, returns public CDN URLs
- Selected via `storage_backend` env var

**Admin System (app/admin/):**
- JWT-based authentication (`app/admin/auth.py`)
- CRUD operations for fabric families and colors (`app/admin/crud.py`)
- Protected routes mounted under `/admin/fabrics`

**Database Models:**
- Defined in `app/admin/models.py`: `FabricFamily`, `Color`
- SQLAlchemy ORM with declarative base from `app/core/database.py`
- Migrations in `alembic/versions/`

### Frontend Architecture

**State Management:**
- `useVirtualStylist` hook (`hooks/useVirtualStylist.ts`) manages entire generation flow:
  - Fetches catalog on mount
  - Tracks fabric/color selection
  - Handles generation requests and loading states
  - Manages generated image results

**API Communication:**
- Public endpoints: `fetchCatalog()`, `generateImages()` in `lib/apiClient.ts`
- Admin endpoints: `listFabrics()`, `createFabric()`, etc. in `lib/adminApi.ts`
- All requests proxied through `/api/*` → backend (configured in `next.config.ts`)

**Key Components:**
- `GeneratedImageGallery`: Thumbnail grid with modal support
- `ImageModal`: Full-screen image viewer with metadata
- `AdminTable` (`app/admin/AdminTable.tsx`): Fabric management UI with search/filter

### Environment Variables by Module

**Generator (SDXL):**
- `GUIDANCE=4.3` - CFG scale
- `TOTAL_STEPS=80` - Inference steps
- `USE_REFINER=1` - Enable SDXL refiner
- `REFINER_SPLIT=0.70` - Base/refiner transition point
- `CONTROLNET_ENABLED=1` - Enable ControlNet
- `CONTROLNET_MODEL` - HuggingFace model ID
- `CONTROLNET_WEIGHT=1.15` - ControlNet strength
- `CONTROL_IMAGE_RECTO`, `CONTROL_IMAGE_CRUZADO` - Pose reference images
- `IP_ADAPTER_ENABLED=1` - Enable IP-Adapter
- `IP_ADAPTER_SCALE=0.70` - Image prompt strength
- `HF_HOME` - Hugging Face cache directory
- `WATERMARK_PATH` - Path to watermark image

**Storage:**
- `storage_backend=local|r2` - Storage provider
- `public_base_url` - Public URL base for local storage
- `r2_account_id`, `r2_access_key_id`, `r2_secret_access_key`, `r2_bucket_name`, `r2_public_url` - R2 credentials

## Testing API Endpoints

**Generate endpoint (POST /generate):**
```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"algodon-tech","color_id":"negro-001","cuts":["recto"],"seed":123456789}'
```

**Catalog endpoint (GET /catalog):**
```bash
curl http://127.0.0.1:8000/catalog
```

**Health check (GET /healthz):**
```bash
curl http://127.0.0.1:8000/healthz
```

## Deployment (RunPod GPU Pods)

The `backend/devops/runpod/deploy.sh` script handles full deployment:
1. Creates Python 3.11 venv on network volume (`/workspace/py311`)
2. Clones/updates repo from `origin/main`
3. Installs dependencies
4. Sets generation environment variables (ControlNet, IP-Adapter paths)
5. Applies database migrations
6. Seeds fabric data
7. Starts Uvicorn on port 8000

**Key deployment paths:**
- `/workspace/app` - Repository clone
- `/workspace/py311` - Persistent Python 3.11 venv
- `/workspace/.cache/huggingface` - Model cache (HF_HOME)

## Common Workflows

**Adding a new fabric:**
1. Add entry to `backend/app/data/fabrics.json`
2. Run `python seed.py` to populate database
3. Or use admin UI at `http://localhost:3000/admin`

**Modifying generation parameters:**
1. Update environment variables in `.env` or deployment script
2. Restart backend server
3. No code changes needed for tuning guidance/steps/weights

**Switching storage backends:**
1. Set `storage_backend=r2` in `.env`
2. Provide R2 credentials
3. Restart backend - storage layer is dependency-injected

**Adding new database fields:**
1. Modify models in `app/admin/models.py`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Apply: `alembic upgrade head`

## Code Style & Conventions

- **Backend**: FastAPI dependency injection pattern, Pydantic for validation, SQLAlchemy ORM
- **Frontend**: React hooks for state, TypeScript strict mode, Tailwind for styling
- **File references**: Use pattern `file_path:line_number` when referencing code locations
- **Error handling**: Custom error handlers in `app/errors.py`, FastAPI HTTPException for API errors
