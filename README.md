# HF Virtual Stylist

The HF Virtual Stylist pairs a FastAPI backend with a Next.js front end to let Harris & Frank sales associates design bespoke looks in real time. The system generates SDXL-powered suit renders, manages a structured fabric catalog, and exposes an admin surface for merchandising teams to curate offerings.

## Feature Highlights
- **Photorealistic generation pipeline** – The backend orchestrates Stable Diffusion XL with optional ControlNet and IP-Adapter guidance while watermarking and persisting each render. Local disk storage works out of the box and a Cloudflare R2 backend can be switched on via environment variables.【F:backend/app/services/generator.py†L1-L117】【F:backend/app/services/storage.py†L1-L60】
- **Dynamic catalog management** – Fabric families and colors live in a SQLAlchemy database, can be seeded from `app/data/fabrics.json`, and are exposed both to the public catalog endpoint and to an internal admin API used by the dashboard in `/admin`. Alembic migrations keep the schema in sync.【F:backend/app/routers/catalog.py†L1-L55】【F:backend/alembic/versions/41832a8aee86_add_fabric_and_color_models.py†L1-L46】【F:backend/seed.py†L1-L66】
- **Sales-floor friendly UI** – The Next.js App Router client offers guided fabric selection, live previews, and a modal gallery for generated imagery. It also ships with an admin table that can search, toggle, and create fabric entries against the FastAPI admin routes.【F:frontend/src/app/page.tsx†L1-L70】【F:frontend/src/app/admin/AdminTable.tsx†L1-L228】
- **RunPod-ready deployment** – `backend/devops/runpod/deploy.sh` installs dependencies on GPU pods, wires up ControlNet/IP-Adapter assets, applies migrations, seeds data, and starts the API—mirroring the production pipeline.【F:backend/devops/runpod/deploy.sh†L1-L134】

## Repository Layout
| Path | Description |
| --- | --- |
| `backend/` | FastAPI service, SQLAlchemy models, SDXL generation, Alembic migrations, and deployment tooling. |
| `frontend/` | Next.js 15 App Router project with the client experience and admin dashboard. |

## Local Setup
### Prerequisites
- Python 3.11
- Node.js 18+ and npm
- SQLite (or another database supported by SQLAlchemy) for local development

### Backend
1. Create `backend/.env` with at least:
   ```env
   database_url=sqlite:///./storage/app.db
   admin_password=change-me
   jwt_secret=local-dev-secret
   jwt_algorithm=HS256
   storage_backend=local
   public_base_url=http://localhost:8000/files
   # R2 credentials only when using storage_backend=r2
   # r2_account_id=...
   # r2_access_key_id=...
   # r2_secret_access_key=...
   # r2_bucket_name=...
   # r2_public_url=https://<bucket>.r2.dev
   ```
2. (Optional) Create and activate a virtual environment.
3. Install dependencies: `pip install -r backend/requirements.txt`.
4. Apply migrations from `backend/`: `alembic upgrade head`.
5. Populate fabrics from the bundled data (optional): `python seed.py`.
6. Start the API: `uvicorn app.main:app --reload --port 8000`.

### Frontend
1. Install dependencies from `frontend/`: `npm install`.
2. Create `frontend/.env.local` and point the proxy and admin page to your API:
   ```env
   NEXT_PUBLIC_RUNPOD_URL=http://localhost:8000
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```
   The Next.js config rewrites `/api/*` calls to `NEXT_PUBLIC_RUNPOD_URL`, so the catalog and generation hooks work both locally and on RunPod.【F:frontend/next.config.ts†L1-L21】【F:frontend/src/lib/apiClient.ts†L1-L38】
3. Start the dev server: `npm run dev` (defaults to port 3000).

Visit `http://localhost:3000` for the stylist UI and `http://localhost:3000/admin` for the merchandising console.

## Testing
- Backend: `pytest -q`
- Frontend: `npm run lint`

## Deployment Notes
- Use `backend/devops/runpod/deploy.sh` on RunPod to clone the repo, install Python packages, configure ControlNet/IP-Adapter assets, run migrations, seed data, and launch Uvicorn.【F:backend/devops/runpod/deploy.sh†L1-L134】
- Switch to Cloudflare R2 storage by setting `storage_backend=r2` and providing the R2 credentials in `.env`; URLs are rewritten automatically when `public_base_url` is absent.【F:backend/app/routers/generate.py†L1-L40】【F:backend/app/services/storage.py†L26-L60】

## Additional Documentation
- [`backend/README.md`](backend/README.md) – detailed API contracts, environment variables, and generator internals.
- [`frontend/README.md`](frontend/README.md) – Next.js architecture and admin console details.
