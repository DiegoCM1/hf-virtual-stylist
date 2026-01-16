# Backend – Servicio FastAPI & SDXL

## Descripción General
El backend potencia la gestión del catálogo, herramientas de administración y síntesis de imágenes SDXL. Expone endpoints REST para la UI pública del estilista así como rutas de administración protegidas. La generación de imágenes usa por defecto el `SdxlTurboGenerator`, que soporta guía opcional de ControlNet e IP-Adapter mientras marca con agua cada render antes de almacenarlo.【F:backend/app/services/generator.py†L1-L117】

## Configuración del Entorno
Crear `backend/.env` antes de iniciar el servicio. Las claves requeridas reflejan `app/core/config.py` y los adaptadores de almacenamiento.【F:backend/app/core/config.py†L1-L31】【F:backend/app/services/storage.py†L1-L60】

| Clave | Propósito | Ejemplo |
| --- | --- | --- |
| `DATABASE_URL` | Cadena de conexión PostgreSQL (Railway/Neon). | `postgresql://user:pass@host:5432/db` |
| `admin_password` | Credencial seed para flujos admin (hash o plano, dependiendo del uso). | `change-me` |
| `jwt_secret` / `jwt_algorithm` | Secretos de firma JWT para endpoints admin. | `local-secret` / `HS256` |
| `storage_backend` | `r2` para producción. | `r2` |
| `r2_*` claves | Credenciales de Cloudflare R2: `r2_account_id`, `r2_access_key_id`, `r2_secret_access_key`, `r2_bucket_name`, `r2_public_url`. | _ver `.env`_ |
| `HF_HOME`, `WATERMARK_PATH`, `CONTROLNET_*`, `IP_ADAPTER_*` | Toggles avanzados de generación leídos directamente dentro del módulo generador. | _opcional_ |

## Instalación y Configuración
1. (Opcional) Crear un entorno virtual Python 3.11.
2. Instalar dependencias desde la raíz del repo: `pip install -r backend/requirements.txt`.
3. Asegurar que el directorio de almacenamiento existe (`backend/storage/` se crea automáticamente cuando la app inicia).【F:backend/app/main.py†L1-L33】

### Base de Datos y Migraciones
1. Configurar la conexión Alembic en `.env` (el CLI lee `database_url`).
2. Aplicar el esquema más reciente: `alembic upgrade head`. La migración inicial crea las tablas `fabric_families` y `colors` usadas tanto por el catálogo como por las experiencias admin.【F:backend/alembic/versions/41832a8aee86_add_fabric_and_color_models.py†L1-L46】
3. Cargar datos de telas y URLs de muestras (opcional): `python seed.py`. El script ingiere `app/data/fabrics.json` y enriquece las muestras desde `app/data/swatch_mapping.csv`.【F:backend/seed.py†L1-L66】

### Ejecutar la API
Lanzar el servidor de desarrollo desde `backend/`:
```bash
uvicorn app.main:app --reload --port 8000
```
Esto monta los assets generados bajo `/files`, habilita CORS para el servidor dev de Next.js, y registra los routers de catálogo, generación y admin.【F:backend/app/main.py†L1-L35】

## Backends de Almacenamiento
- **LocalStorage** – Guarda imágenes bajo `storage/` y reescribe URLs a `/files/...`. Ideal para estaciones de trabajo locales o despliegues de nodo único.【F:backend/app/services/storage.py†L16-L38】
- **R2Storage** – Sube a Cloudflare R2 usando credenciales compatibles con S3 y retorna la URL pública del CDN. Habilitarlo estableciendo `storage_backend=r2` y proporcionando las claves R2 en `.env`.【F:backend/app/services/storage.py†L40-L60】

## Pipeline de Generación
- `SdxlTurboGenerator` realiza text-to-image usando Stable Diffusion XL, pasos opcionales de refiner, ControlNet y prompts de IP-Adapter controlados a través de variables de entorno. Los outputs se marcan con agua antes del almacenamiento.【F:backend/app/services/generator.py†L55-L188】
- `MockGenerator` puede alternarse estableciendo `USE_MOCK = True` dentro de `app/routers/generate.py` para demos ligeros que aún ejercitan los flujos de marca de agua y almacenamiento.【F:backend/app/services/generator.py†L43-L85】【F:backend/app/routers/generate.py†L1-L40】

## Referencia de API
| Método y Ruta | Descripción |
| --- | --- |
| `GET /healthz` | Retorna `{ "ok": true, "version": ... }` para health checks.【F:backend/app/main.py†L27-L33】 |
| `GET /catalog` | Carga familias de telas activas y colores desde la base de datos, fusionando metadata extra desde `app/data/fabrics.json`.【F:backend/app/routers/catalog.py†L1-L55】 |
| `POST /generate` | Acepta un `GenerationRequest` (`family_id`, `color_id`, `cuts` opcionales, `seed`, `quality`) y retorna URLs más metadata para cada corte generado. Las URLs de almacenamiento local se reescriben a URLs absolutas cuando es necesario.【F:backend/app/models/generate.py†L1-L24】【F:backend/app/routers/generate.py†L24-L40】 |
| `GET /admin/fabrics` | Lista familias de telas con paginación, búsqueda y filtros de estado para el dashboard admin.【F:backend/app/admin/router.py†L1-L34】 |
| `POST /admin/fabrics` | Crea una familia de telas con definiciones de color opcionales (la deduplicación se aplica a nivel de BD).【F:backend/app/admin/router.py†L36-L61】 |
| `PATCH /admin/fabrics/{fabric_id}` | Actualiza identificadores, nombres de visualización, estado y reemplaza colores asociados en una sola llamada.【F:backend/app/admin/router.py†L63-L95】 |
| `POST /admin/fabrics/{fabric_id}/deactivate` | Endpoint de conveniencia para marcar una familia de telas como inactiva sin editar otros campos.【F:backend/app/admin/router.py†L97-L111】 |

## Testing
Ejecutar la suite automatizada desde `backend/`:
```bash
pytest -q
```

## Despliegue

### Arquitectura
```
Frontend (Vercel) → Railway (API + PostgreSQL) ← RunPod (GPU Worker)
                                                        ↓
                                                 Cloudflare R2 (images)
```

### RunPod (GPU Worker)
`backend/devops/runpod/deploy.sh` configura el pod como **worker** que:
1. Conecta a PostgreSQL de Railway (no usa DB local)
2. Corre `worker.py` que hace polling por jobs pendientes
3. Procesa generaciones con SDXL y sube resultados a R2

Variables requeridas en RunPod:
```env
DATABASE_URL=postgresql://...  # De Railway
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=...
R2_PUBLIC_URL=https://pub-xxx.r2.dev
```


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
