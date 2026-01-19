# Backend Architecture

**Migration Date:** 2025-01-22
**Pattern:** Feature-based (Vertical Slices)

## Structure

```
app/
├── catalog/              # Public fabric/color browsing
│   ├── router.py         # GET /catalog
│   ├── schemas.py        # Pydantic models
│   └── service.py        # Load from fabrics.json
│
├── generation/           # AI image generation
│   ├── router.py         # POST /generate, GET /jobs/{id}, POST /upload-swatch
│   ├── schemas.py        # Request/Response models
│   ├── models.py         # GenerationJob ORM
│   ├── generator.py      # SdxlTurboGenerator (main SDXL logic)
│   ├── generator_config.py    # Environment variables
│   ├── generator_mock.py      # MockGenerator (testing)
│   ├── storage.py        # LocalStorage, R2Storage
│   └── watermark.py      # Watermark application
│
├── admin/                # Admin management
│   ├── fabrics/          # Fabric CRUD
│   │   ├── fabrics_router.py
│   │   ├── colors_router.py
│   │   ├── models.py     # FabricFamily, Color ORM
│   │   └── schemas.py
│   ├── generations/      # Generation history
│   │   ├── router.py
│   │   └── schemas.py
│   ├── auth.py           # JWT authentication
│   └── dependencies.py   # FastAPI dependencies
│
├── core/                 # Shared infrastructure
│   ├── config.py         # Pydantic settings
│   └── database.py       # SQLAlchemy session
│
└── main.py               # FastAPI app initialization
```

## Key Changes

**Before (Layer-based):**
- `routers/` → All endpoints
- `models/` → All Pydantic schemas
- `services/` → All business logic (giant generator.py: 2100 lines)
- `admin/` → Mixed pattern

**After (Feature-based):**
- Each feature is self-contained in its own folder
- Related code stays together (router + schemas + logic)
- `generator.py` split into smaller, focused files

## API Endpoints

### Public Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /catalog | Lista familias de tela activas con colores y swatch URLs |
| POST | /generate | Crea job de generacion (retorna job_id inmediatamente) |
| GET | /jobs/{job_id} | Consulta estado del job (polling) |
| POST | /upload-swatch | Sube imagen de tela a R2, retorna URL para IP-Adapter |
| GET | /health | Health check |

### Admin Endpoints (JWT required)

| Method | Path | Description |
|--------|------|-------------|
| GET | /admin/fabrics | Lista todas las familias |
| POST | /admin/fabrics | Crear familia |
| PATCH | /admin/fabrics/{id} | Actualizar familia |
| DELETE | /admin/fabrics/{id} | Eliminar familia |

## Database Schema

### generation_jobs (Job Queue)

```sql
CREATE TABLE generation_jobs (
    id              SERIAL PRIMARY KEY,
    job_id          VARCHAR UNIQUE NOT NULL,  -- UUID for API
    status          VARCHAR NOT NULL,         -- pending, processing, completed, failed
    family_id       VARCHAR NOT NULL,
    color_id        VARCHAR NOT NULL,
    cuts            JSON NOT NULL,            -- ["recto", "cruzado"]
    seed            INTEGER,
    swatch_url      VARCHAR,                  -- URL for IP-Adapter
    result_urls     JSON,                     -- Generated image URLs
    error_message   TEXT,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP
);
```

### fabric_families & colors

```sql
CREATE TABLE fabric_families (
    id            SERIAL PRIMARY KEY,
    family_id     VARCHAR UNIQUE NOT NULL,
    display_name  VARCHAR NOT NULL,
    status        VARCHAR DEFAULT 'active',
    created_at    TIMESTAMP,
    updated_at    TIMESTAMP
);

CREATE TABLE colors (
    id               SERIAL PRIMARY KEY,
    fabric_family_id INTEGER REFERENCES fabric_families(id),
    color_id         VARCHAR UNIQUE NOT NULL,
    name             VARCHAR NOT NULL,
    hex_value        VARCHAR NOT NULL,
    swatch_code      VARCHAR,          -- R2 filename (e.g., "095T-0121")
    swatch_url       VARCHAR,          -- Full URL override
    status           VARCHAR DEFAULT 'active'
);
```

## Async Generation Flow

```
1. Frontend: POST /generate {family_id, color_id, cuts, swatch_url}
                    │
                    ▼
2. Railway API: Crea job en PostgreSQL (status="pending")
                Retorna {job_id} inmediatamente
                    │
                    ▼
3. Frontend: Polling GET /jobs/{job_id} cada 2 segundos
                    │
   ════════════════════════════════════════════════════
                    │
4. RunPod Worker: SELECT * FROM generation_jobs
                  WHERE status='pending'
                  ORDER BY created_at LIMIT 1
                    │
                    ▼
5. Worker: status → "processing"
           Carga SDXL + ControlNet + IP-Adapter
           Descarga swatch_url si existe
           Genera imagenes
           Aplica watermark
           Sube a R2
                    │
                    ▼
6. Worker: status → "completed"
           result_urls: ["https://r2.dev/generated/..."]
                    │
   ════════════════════════════════════════════════════
                    │
                    ▼
7. Frontend: Detecta status="completed"
             Muestra imagenes de result_urls
```

## Storage (Cloudflare R2)

```
bucket/
├── ZEGNA 2025-26/           # Swatches del catalogo
│   ├── 095T-0121.png
│   ├── 095T-0132.png
│   └── ...
│
├── temp-uploads/            # Swatches subidos por usuarios
│   ├── {uuid}.jpg           # Expiran en 24h (R2 Lifecycle Rule)
│   └── {uuid}.png
│
└── generated/               # Imagenes generadas por SDXL
    └── {family_id}/
        └── {color_id}/
            └── {run_id}/
                ├── recto.jpg
                └── cruzado.jpg
```

### Upload Swatch Flow

```
1. Usuario selecciona imagen en frontend
2. POST /upload-swatch (multipart/form-data)
3. Backend valida:
   - Tipo: image/jpeg, image/png, image/webp
   - Tamaño: max 5MB
4. Genera key: temp-uploads/{uuid}.{ext}
5. Sube a R2
6. Retorna: {swatch_url: "https://r2.dev/temp-uploads/abc123.jpg"}
7. Frontend incluye URL en POST /generate
8. Worker usa URL con IP-Adapter para transferir textura
```

**Cleanup:** R2 Lifecycle Rule elimina `temp-uploads/*` despues de 24 horas

## Worker Resilience

- **DB Connection:** `pool_pre_ping=True` handles Neon connection timeouts during long GPU jobs
- **IP-Adapter Fallback:** If swatch URL fails to load, uses blank image with scale=0 (no effect)
- **Multi-cut GPU:** Base model reloaded to GPU between cuts to avoid device mismatch


