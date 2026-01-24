# CLAUDE.md

Este archivo proporciona orientación a Claude Code cuando trabaja con este repositorio.

## Descripción del Proyecto

HF Virtual Stylist es una aplicación de visualización de trajes potenciada por IA para Harris & Frank. El sistema genera renders fotorrealistas de trajes usando SDXL Inpainting con IP-Adapter para transferencia de texturas de tela.

**Stack tecnológico:**
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL (Neon)
- **Frontend:** Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **IA/ML:** SDXL Inpainting + IP-Adapter Plus
- **Almacenamiento:** Cloudflare R2
- **Despliegue:** Railway (API) + RunPod (GPU Worker) + Vercel (Frontend)

## Arquitectura de Producción

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Vercel    │────▶│   Railway   │────▶│    Neon     │
│  (Frontend) │     │    (API)    │     │ (PostgreSQL)│
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                        polling cada 5s
                                               │
                                        ┌──────▼──────┐
                                        │   RunPod    │
                                        │  (Worker)   │
                                        │  GPU SDXL   │
                                        └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │ Cloudflare  │
                                        │     R2      │
                                        └─────────────┘
```

**Flujo de generación:**
1. Usuario selecciona tela/color en frontend
2. Frontend → POST /generate → Railway API
3. API crea job en PostgreSQL con status="pending", retorna job_id
4. Frontend hace polling GET /jobs/{job_id}
5. Worker (RunPod) detecta job pendiente
6. Worker procesa con SDXL Inpainting + IP-Adapter
7. Worker sube imagen a R2, actualiza job a "completed"
8. Frontend recibe URLs en siguiente poll

## Estructura del Repositorio

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, routers
│   ├── core/
│   │   ├── config.py        # Pydantic settings (env vars)
│   │   └── database.py      # SQLAlchemy session
│   ├── catalog/
│   │   ├── router.py        # GET /catalog
│   │   ├── service.py       # Carga fabrics.json
│   │   └── schemas.py
│   ├── generation/
│   │   ├── router.py        # POST /generate, GET /jobs/{id}, POST /upload-swatch
│   │   ├── generator.py           # SdxlTurboGenerator (full generation)
│   │   ├── generator_inpaint.py   # InpaintGenerator (default mode)
│   │   ├── generator_mock.py      # MockGenerator (testing)
│   │   ├── generator_config.py    # Env vars para generación
│   │   ├── storage.py       # LocalStorage, R2Storage
│   │   ├── models.py        # GenerationJob ORM
│   │   └── watermark.py
│   ├── admin/
│   │   ├── fabrics/         # CRUD familias y colores
│   │   ├── generations/     # Historial de jobs
│   │   ├── auth.py          # JWT
│   │   └── dependencies.py
│   └── data/
│       └── fabrics.json     # Catálogo seed
├── worker.py                # GPU worker (polling loop)
├── seed.py                  # Poblar BD desde fabrics.json
├── alembic/                 # Migraciones
├── devops/runpod/
│   └── deploy.sh            # Setup y ejecución en RunPod
├── requirements.txt         # Dependencias API (Railway, local dev)
└── requirements-gpu.txt     # Dependencias GPU (RunPod)

frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx         # UI principal
│   │   └── admin/           # Dashboard admin
│   ├── components/          # React components
│   ├── hooks/
│   │   └── useVirtualStylist.ts  # Estado de generación
│   ├── lib/
│   │   ├── apiClient.ts     # API pública
│   │   └── adminApi.ts      # API admin
│   └── types/
├── next.config.ts           # Rewrites /api/* → backend
└── package.json
```

## Comandos de Desarrollo

### Backend

```bash
cd backend

# Instalar dependencias (API/local dev)
pip install -r requirements.txt

# Para GPU worker (RunPod) usar: requirements-gpu.txt

# Migraciones
alembic upgrade head

# Poblar datos (opcional)
python seed.py

# Ejecutar API
uvicorn app.main:app --reload --port 8000

# Ejecutar worker (para testing local con mock)
USE_MOCK_GENERATOR=true python worker.py

# Tests
pytest -q
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Lint
npm run lint

# Build
npm run build
```

## Variables de Entorno

### Backend (.env)

```env
# Base de datos (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Admin/Auth
ADMIN_PASSWORD=secure-password
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Storage
STORAGE_BACKEND=r2
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=harris-and-frank
R2_PUBLIC_URL=https://pub-xxx.r2.dev
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### RunPod (GPU Worker)

```env
DATABASE_URL=postgresql://...
GENERATOR_MODE=inpaint          # inpaint (default), full, mock
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=...
R2_PUBLIC_URL=...
```

## Generadores

El sistema tiene 3 modos de generación controlados por `GENERATOR_MODE`:

| Modo | Clase | Uso |
|------|-------|-----|
| `mock` | MockGenerator | Testing sin GPU, genera placeholders |
| `inpaint` | InpaintGenerator | **Producción (default)** - SDXL Inpainting + IP-Adapter Plus |
| `full` | SdxlTurboGenerator | Generación completa con ControlNet (alternativo) |

## API Endpoints

### Públicos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /catalog | Lista familias de tela activas con colores |
| POST | /generate | Crea job de generación, retorna job_id |
| GET | /jobs/{job_id} | Consulta estado del job (polling) |
| POST | /upload-swatch | Sube imagen de tela temporal a R2 |
| GET | /healthz | Health check |

### Admin (requiere JWT)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /admin/fabrics | Lista todas las familias |
| POST | /admin/fabrics | Crear familia |
| PATCH | /admin/fabrics/{id} | Actualizar familia |
| DELETE | /admin/fabrics/{id} | Eliminar familia |

## Despliegue

### Railway (API)
- Deploy automático desde `main`
- Variables de entorno en Railway dashboard
- Ejecuta: `uvicorn app.main:app`

### RunPod (GPU Worker)
- Crear Network Volume + Pod con GPU (RTX 4090 recomendado)
- Configurar env vars en pod
- Ejecutar: `./backend/devops/runpod/deploy.sh`
- El script clona repo, instala deps, y ejecuta `worker.py`

### Vercel (Frontend)
- Deploy automático desde `main`
- Configurar `NEXT_PUBLIC_API_BASE` apuntando a Railway

## Testing de Endpoints

```bash
# Health check
curl http://localhost:8000/healthz

# Catálogo
curl http://localhost:8000/catalog

# Crear job de generación
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"azules","color_id":"az-001","cuts":["recto"]}'

# Consultar estado
curl http://localhost:8000/jobs/{job_id}
```

## Base de Datos

### Tablas principales

**fabric_families**
- `family_id` (unique): Identificador (ej: "azules")
- `display_name`: Nombre visible (ej: "Azules")
- `status`: "active" | "inactive"

**colors**
- `color_id` (unique): Identificador (ej: "az-095T-0121")
- `fabric_family_id`: FK a fabric_families
- `name`: Nombre visible (ej: "Azul Oscuro")
- `hex_value`: Color hex (ej: "#0A1D3A")
- `swatch_code`: Nombre archivo R2 (ej: "095T-0121")

**generation_jobs**
- `job_id` (unique): UUID
- `status`: "pending" | "processing" | "completed" | "failed"
- `family_id`, `color_id`, `cuts`, `seed`, `swatch_url`
- `result_urls`: JSON array con URLs de imágenes generadas

## Documentación Adicional

- [OPERATIONS.md](OPERATIONS.md) - Guía de operaciones y handover
- [backend/docs/ARCHITECTURE.md](backend/docs/ARCHITECTURE.md) - Arquitectura técnica
- [backend/docs/RoadMapProd.md](backend/docs/RoadMapProd.md) - Decisiones técnicas
