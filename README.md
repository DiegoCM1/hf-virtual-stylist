# HF Virtual Stylist

The HF Virtual Stylist pairs a FastAPI backend with a Next.js front end to let Harris & Frank sales associates design bespoke looks in real time. The system generates SDXL-powered suit renders, manages a structured fabric catalog, and exposes an admin surface for merchandising teams to curate offerings.

## Feature Highlights
- **Photorealistic generation pipeline** – The backend orchestrates Stable Diffusion XL with optional ControlNet and IP-Adapter guidance while watermarking and persisting each render. Local disk storage works out of the box and a Cloudflare R2 backend can be switched on via environment variables.
- **Dynamic catalog management** – Fabric families and colors live in a SQLAlchemy database, can be seeded from `app/data/fabrics.json`, and are exposed both to the public catalog endpoint and to an internal admin API used by the dashboard in `/admin`. Alembic migrations keep the schema in sync.
- **Sales-floor friendly UI** – The Next.js App Router client offers guided fabric selection, live previews, and a modal gallery for generated imagery. It also ships with an admin table that can search, toggle, and create fabric entries against the FastAPI admin routes.
- **RunPod-ready deployment** – `backend/devops/runpod/deploy.sh` installs dependencies on GPU pods, wires up ControlNet/IP-Adapter assets, and starts the worker to process generation jobs.

## Repository Layout
| Path | Description |
| --- | --- |
| `backend/` | FastAPI service, SQLAlchemy models, SDXL generation, Alembic migrations, and deployment tooling. |
| `frontend/` | Next.js 15 App Router project with the client experience and admin dashboard. |

## Local Setup
### Prerequisites
- Python 3.11
- Node.js 18+ and npm
- PostgreSQL database (use Railway or Neon for hosted option)

### Backend
1. Create `backend/.env` with at least:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   admin_password=change-me
   jwt_secret=local-dev-secret
   jwt_algorithm=HS256
   storage_backend=r2
   # R2 credentials (required for production)
   r2_account_id=...
   r2_access_key_id=...
   r2_secret_access_key=...
   r2_bucket_name=...
   r2_public_url=https://<bucket>.r2.dev
   ```
2. (Optional) Create and activate a virtual environment.
3. Install dependencies: `pip install -r backend/requirements.txt`.
4. Apply migrations from `backend/`: `alembic upgrade head`.
5. Populate fabrics from the bundled data (optional): `python seed.py`.
6. Start the API: `uvicorn app.main:app --reload --port 8000`.

### Frontend
1. Install dependencies from `frontend/`: `npm install`.
2. Create `frontend/.env.local` and point the proxy to your API:
   ```env
   NEXT_PUBLIC_API_BASE=http://localhost:8000
   ```
   The Next.js config rewrites `/api/*` calls to this URL, so the catalog and generation hooks work both locally and in production.
3. Start the dev server: `npm run dev` (defaults to port 3000).

Visit `http://localhost:3000` for the stylist UI and `http://localhost:3000/admin` for the merchandising console.

## Arquitectura de Generación (Background Jobs)

El sistema usa una **arquitectura de jobs en segundo plano** para separar la API de la generación intensiva:

```
Frontend → Backend API → Database (crea job "pending")
                            ↓
                         Worker (polling cada 5s)
                            ↓
                    Procesa job → SDXL/MockGenerator
                            ↓
                    Actualiza job "completed" con URLs
                            ↓
            Frontend (polling) → Obtiene resultados
```

### Componentes:

1. **Backend API** (`uvicorn app.main:app`)
   - Endpoint `/generate` crea un job en BD con status="pending"
   - Endpoint `/jobs/{job_id}` retorna status y resultados
   - **No ejecuta SDXL** - retorna inmediatamente

2. **Worker** (`python worker.py`)
   - Proceso separado que hace polling de la BD cada 5 segundos
   - Toma jobs "pending", ejecuta generación (Mock o SDXL)
   - Actualiza job a "completed" con URLs de imágenes
   - **Debe estar corriendo** para que las generaciones funcionen

3. **Generadores:**
   - `MockGenerator`: Genera imágenes placeholder (sin GPU) - para desarrollo
   - `InpaintGenerator`: Inpainting con SDXL + IP-Adapter Plus (requiere GPU) - **modo por defecto**
   - `SdxlTurboGenerator`: Generación completa con SDXL + ControlNet (requiere GPU) - alternativo

### Variables de Entorno Clave:

```env
# Usar MockGenerator (sin GPU) o SdxlTurboGenerator (con GPU)
USE_MOCK_GENERATOR=true   # true = Mock, false = SDXL

# Storage backend
STORAGE_BACKEND=local     # local o r2
```

## Testing
- Backend: `pytest -q`
- Frontend: `npm run lint`

## Deployment Architecture

```
Frontend (Vercel) → Railway (API) → Neon (PostgreSQL) ← RunPod (GPU Worker)
                                                                ↓
                                                         Cloudflare R2 (images)
```

### Components:
- **Railway**: Runs the FastAPI backend API
- **Neon**: Hosts the PostgreSQL database (shared between Railway and RunPod)
- **RunPod**: Runs `worker.py` which polls PostgreSQL for pending jobs and processes them with SDXL
- **Vercel**: Hosts the Next.js frontend
- **Cloudflare R2**: Stores generated images

### RunPod Setup
Use `backend/devops/runpod/deploy.sh` on RunPod GPU pods. Configure these environment variables in RunPod:
```env
DATABASE_URL=postgresql://...  # From Neon dashboard
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=...
R2_PUBLIC_URL=https://pub-xxx.r2.dev
```
The script runs `worker.py` which connects to Neon's PostgreSQL to process generation jobs.

## Production Operations

See **[OPERATIONS.md](OPERATIONS.md)** for complete production documentation:
- Service inventory (Railway, Neon, RunPod, Cloudflare R2, Vercel)
- RunPod GPU worker setup from scratch
- Environment variables reference
- Deployment procedures
- Troubleshooting guide
- Credentials management

## Additional Documentation
- [`backend/README.md`](backend/README.md) – detailed API contracts, environment variables, and generator internals.
- [`frontend/README.md`](frontend/README.md) – Next.js architecture and admin console details.
- [`OPERATIONS.md`](OPERATIONS.md) – production operations, deployment, and handover guide.
