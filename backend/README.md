# Backend – FastAPI & SDXL Service

## Overview
The backend powers catalog management, admin tooling, and SDXL image synthesis. It exposes REST endpoints for the public stylist UI as well as protected admin routes. Image generation defaults to the `SdxlTurboGenerator`, which supports optional ControlNet and IP-Adapter guidance while watermarking every render before it is stored.【F:backend/app/services/generator.py†L1-L117】

## Environment Configuration
Create `backend/.env` before starting the service. Required keys mirror `app/core/config.py` and the storage adapters.【F:backend/app/core/config.py†L1-L31】【F:backend/app/services/storage.py†L1-L60】

| Key | Purpose | Example |
| --- | --- | --- |
| `database_url` | SQLAlchemy connection string. | `sqlite:///./storage/app.db` |
| `admin_password` | Seed credential for admin flows (hash or plain, depending on usage). | `change-me` |
| `jwt_secret` / `jwt_algorithm` | JWT signing secrets for admin endpoints. | `local-secret` / `HS256` |
| `storage_backend` | `local` (default) or `r2`. | `local` |
| `public_base_url` | Optional absolute base used when rewriting local storage URLs. | `http://localhost:8000/files` |
| `r2_*` keys | Cloudflare R2 credentials when `storage_backend=r2`. | _see `.env`_ |
| `HF_HOME`, `WATERMARK_PATH`, `CONTROLNET_*`, `IP_ADAPTER_*` | Advanced generation toggles read directly inside the generator module. | _optional_ |

## Installation & Setup
1. (Optional) Create a Python 3.11 virtual environment.
2. Install dependencies from the repo root: `pip install -r backend/requirements.txt`.
3. Ensure the storage directory exists (`backend/storage/` is created automatically when the app boots).【F:backend/app/main.py†L1-L33】

### Database & Migrations
1. Configure the Alembic connection in `.env` (the CLI reads `database_url`).
2. Apply the latest schema: `alembic upgrade head`. The initial migration creates the `fabric_families` and `colors` tables used by both the catalog and admin experiences.【F:backend/alembic/versions/41832a8aee86_add_fabric_and_color_models.py†L1-L46】
3. Seed fabric data and swatch URLs (optional): `python seed.py`. The script ingests `app/data/fabrics.json` and enriches swatches from `app/data/swatch_mapping.csv`.【F:backend/seed.py†L1-L66】

### Running the API
Launch the development server from `backend/`:
```bash
uvicorn app.main:app --reload --port 8000
```
This mounts generated assets under `/files`, enables CORS for the Next.js dev server, and registers the catalog, generate, and admin routers.【F:backend/app/main.py†L1-L35】

## Storage Backends
- **LocalStorage** – Saves images under `storage/` and rewrites URLs to `/files/...`. Ideal for local workstations or single-node deployments.【F:backend/app/services/storage.py†L16-L38】
- **R2Storage** – Uploads to Cloudflare R2 using S3-compatible credentials and returns the public CDN URL. Enable it by setting `storage_backend=r2` and supplying the R2 keys in `.env`.【F:backend/app/services/storage.py†L40-L60】

## Generation Pipeline
- `SdxlTurboGenerator` performs text-to-image using Stable Diffusion XL, optional refiner steps, ControlNet, and IP-Adapter prompts controlled through environment variables. Outputs are watermarked before storage.【F:backend/app/services/generator.py†L55-L188】
- `MockGenerator` can be toggled by setting `USE_MOCK = True` inside `app/routers/generate.py` for lightweight demos that still exercise watermarking and storage flows.【F:backend/app/services/generator.py†L43-L85】【F:backend/app/routers/generate.py†L1-L40】

## API Reference
| Method & Path | Description |
| --- | --- |
| `GET /healthz` | Returns `{ "ok": true, "version": ... }` for health checks.【F:backend/app/main.py†L27-L33】 |
| `GET /catalog` | Loads active fabric families and colors from the database, merging extra metadata from `app/data/fabrics.json`.【F:backend/app/routers/catalog.py†L1-L55】 |
| `POST /generate` | Accepts a `GenerationRequest` (`family_id`, `color_id`, optional `cuts`, `seed`, `quality`) and returns URLs plus metadata for each generated cut. Local storage URLs are rewritten to absolute URLs when necessary.【F:backend/app/models/generate.py†L1-L24】【F:backend/app/routers/generate.py†L24-L40】 |
| `GET /admin/fabrics` | Lists fabric families with pagination, search, and status filters for the admin dashboard.【F:backend/app/admin/router.py†L1-L34】 |
| `POST /admin/fabrics` | Creates a fabric family with optional color definitions (deduplication is enforced at the DB level).【F:backend/app/admin/router.py†L36-L61】 |
| `PATCH /admin/fabrics/{fabric_id}` | Updates identifiers, display names, status, and replaces associated colors in one call.【F:backend/app/admin/router.py†L63-L95】 |
| `POST /admin/fabrics/{fabric_id}/deactivate` | Convenience endpoint to mark a fabric family as inactive without editing other fields.【F:backend/app/admin/router.py†L97-L111】 |

## Testing
Run the automated suite from `backend/`:
```bash
pytest -q
```

## Deployment
`backend/devops/runpod/deploy.sh` encapsulates the GPU deployment flow: syncing the repo, installing Python 3.11, exporting generation env vars, applying Alembic migrations, seeding data, and starting Uvicorn. Use it as the baseline for RunPod or other GPU orchestrators.【F:backend/devops/runpod/deploy.sh†L1-L134】


---
### Testing
<!-- Recto -->
curl -s -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"algodon-tech","color_id":"negro-001","cuts":["recto"],"seed":123456789}'

  <!-- Cruzado -->
curl -s -X POST http://127.0.0.1:8000/generate \
-H "Content-Type: application/json" \
-d '{"family_id":"algodon-tech","color_id":"negro-001","cuts":["recto"],"seed":123456789}'
