# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) cuando trabaja con código en este repositorio.

## Descripción General del Proyecto

HF Virtual Stylist es un monorepo con un **backend FastAPI** (`backend/`) y un **frontend Next.js 15** (`frontend/`) que genera renders fotorrealistas de trajes usando Stable Diffusion XL. Los asociados de ventas seleccionan telas y colores, y el sistema produce visualizaciones potenciadas por SDXL con guía opcional de ControlNet/IP-Adapter.

## Estructura del Repositorio

```
backend/
├── app/
│   ├── admin/           # Admin CRUD, auth (JWT), esquemas para gestión de telas
│   ├── core/            # config.py (configuración Pydantic), database.py (sesión SQLAlchemy)
│   ├── models/          # Esquemas Pydantic de request/response (catalog, generate)
│   ├── routers/         # Manejadores de rutas FastAPI (catalog, generate, admin)
│   ├── services/        # Lógica central: generator.py (SDXL), storage.py (local/R2), watermark.py
│   ├── data/            # fabrics.json (metadata del catálogo), swatch_mapping.csv
│   └── main.py          # Inicialización de app FastAPI, CORS, montaje de archivos estáticos
├── alembic/             # Migraciones de base de datos
├── devops/runpod/       # deploy.sh para despliegue en pods GPU
├── storage/             # Almacenamiento local de archivos (creado en runtime)
├── tests/               # Suite de tests Pytest
├── requirements.txt     # Dependencias Python
├── seed.py              # Puebla la base de datos desde fabrics.json
└── alembic.ini          # Configuración Alembic

frontend/
├── src/
│   ├── app/             # Páginas Next.js App Router (page.tsx, /admin)
│   ├── components/      # Componentes React (gallery, modals, catalog selector)
│   ├── hooks/           # useVirtualStylist.ts (máquina de estado para flujo de generación)
│   ├── lib/             # apiClient.ts (API pública), adminApi.ts (API admin)
│   └── types/           # Definiciones de tipos TypeScript
├── next.config.ts       # Rewrites de proxy API al backend
└── package.json         # Scripts Node y dependencias
```

## Comandos de Desarrollo

### Backend (Python 3.11, FastAPI, SQLAlchemy)

**Configuración del Entorno:**
1. Crear `backend/.env` con las claves requeridas (ver backend/README.md para la lista completa):
   - `DATABASE_URL=postgresql://user:pass@host:5432/dbname` (Railway/Neon)
   - `admin_password=change-me`
   - `jwt_secret=local-dev-secret`
   - `jwt_algorithm=HS256`
   - `storage_backend=r2`
   - R2 credentials: `r2_account_id`, `r2_access_key_id`, `r2_secret_access_key`, `r2_bucket_name`, `r2_public_url`

2. Instalar dependencias:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Ejecutar migraciones de base de datos:
   ```bash
   alembic upgrade head
   ```

4. Cargar datos iniciales (opcional):
   ```bash
   python seed.py
   ```

**Ejecutar la API:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Testing:**
```bash
cd backend
pytest -q
```

**Migraciones de Base de Datos:**
```bash
# Crear una nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir una migración
alembic downgrade -1
```

### Frontend (Next.js 15, React 19, TypeScript)

**Configuración del Entorno:**
Crear `frontend/.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Ejecutar el servidor de desarrollo:**
```bash
cd frontend
npm install
npm run dev  # Inicia en http://localhost:3000
```

**Linting:**
```bash
npm run lint
```

**Build:**
```bash
npm run build
npm start  # Servidor de producción
```

## Arquitectura y Conceptos Clave

### Arquitectura del Backend

**Flujo de Request:**
1. Cliente → Proxy Next.js `/api/*` → Router FastAPI
2. Router valida request (esquemas Pydantic en `app/models/`)
3. Capa de servicio (`app/services/`) maneja la lógica de negocio
4. Operaciones de base de datos vía SQLAlchemy (`app/core/database.py`)
5. Respuesta retornada al cliente

**Pipeline de Generación (app/services/generator.py):**
- `SdxlTurboGenerator`: Generador de producción principal
  - Carga modelo SDXL base + refiner opcional
  - Soporta ControlNet (openpose, canny) para guía de pose
  - Soporta IP-Adapter para transferencia de textura de tela
  - Marca de agua en outputs vía `apply_watermark_image()`
  - Guarda en backend de almacenamiento (local o R2)
- `MockGenerator`: Fallback ligero para testing (alternar vía `USE_MOCK` en generate.py)

**Backends de Almacenamiento (app/services/storage.py):**
- `LocalStorage`: Guarda en directorio `storage/`, URLs reescritas a `/files/*`
- `R2Storage`: Sube a Cloudflare R2 usando boto3, retorna URLs públicas CDN
- Seleccionado vía variable de entorno `storage_backend`

**Sistema Admin (app/admin/):**
- Autenticación basada en JWT (`app/admin/auth.py`)
- Operaciones CRUD para familias de telas y colores (`app/admin/crud.py`)
- Rutas protegidas montadas bajo `/admin/fabrics`

**Modelos de Base de Datos:**
- Definidos en `app/admin/models.py`: `FabricFamily`, `Color`
- ORM SQLAlchemy con base declarativa desde `app/core/database.py`
- Migraciones en `alembic/versions/`

### Arquitectura del Frontend

**Gestión de Estado:**
- Hook `useVirtualStylist` (`hooks/useVirtualStylist.ts`) gestiona todo el flujo de generación:
  - Obtiene catálogo al montar
  - Rastrea selección de tela/color
  - Maneja requests de generación y estados de carga
  - Gestiona resultados de imágenes generadas

**Comunicación API:**
- Endpoints públicos: `fetchCatalog()`, `generateImages()` en `lib/apiClient.ts`
- Endpoints admin: `listFabrics()`, `createFabric()`, etc. en `lib/adminApi.ts`
- Todos los requests proxy a través de `/api/*` → backend (configurado en `next.config.ts`)

**Componentes Clave:**
- `GeneratedImageGallery`: Grid de thumbnails con soporte de modal
- `ImageModal`: Visor de imagen a pantalla completa con metadata
- `AdminTable` (`app/admin/AdminTable.tsx`): UI de gestión de telas con búsqueda/filtro

### Variables de Entorno por Módulo

**Generador (SDXL):**
- `GUIDANCE=4.3` - Escala CFG
- `TOTAL_STEPS=80` - Pasos de inferencia
- `USE_REFINER=1` - Habilitar refiner SDXL
- `REFINER_SPLIT=0.70` - Punto de transición base/refiner
- `CONTROLNET_ENABLED=1` - Habilitar ControlNet
- `CONTROLNET_MODEL` - ID del modelo HuggingFace
- `CONTROLNET_WEIGHT=1.15` - Fuerza de ControlNet
- `CONTROL_IMAGE_RECTO`, `CONTROL_IMAGE_CRUZADO` - Imágenes de referencia de pose
- `IP_ADAPTER_ENABLED=1` - Habilitar IP-Adapter
- `IP_ADAPTER_SCALE=0.70` - Fuerza del prompt de imagen
- `HF_HOME` - Directorio de caché Hugging Face
- `WATERMARK_PATH` - Ruta a imagen de marca de agua

**Almacenamiento:**
- `storage_backend=local|r2` - Proveedor de almacenamiento
- `public_base_url` - Base de URL pública para almacenamiento local
- `r2_account_id`, `r2_access_key_id`, `r2_secret_access_key`, `r2_bucket_name`, `r2_public_url` - Credenciales R2

## Testeo de Endpoints de API

**Endpoint de generación (POST /generate):**
```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"algodon-tech","color_id":"negro-001","cuts":["recto"],"seed":123456789}'
```

**Endpoint de catálogo (GET /catalog):**
```bash
curl http://127.0.0.1:8000/catalog
```

**Health check (GET /healthz):**
```bash
curl http://127.0.0.1:8000/healthz
```

## Despliegue (RunPod GPU Pods)

El script `backend/devops/runpod/deploy.sh` maneja el despliegue completo:
1. Crea venv Python 3.11 en volumen de red (`/workspace/py311`)
2. Clona/actualiza repo desde `origin/main`
3. Instala dependencias
4. Establece variables de entorno de generación (ControlNet, rutas IP-Adapter)
5. Aplica migraciones de base de datos
6. Carga datos de telas
7. Inicia Uvicorn en puerto 8000

**Rutas clave de despliegue:**
- `/workspace/app` - Clon del repositorio
- `/workspace/py311` - Venv Python 3.11 persistente
- `/workspace/.cache/huggingface` - Caché de modelos (HF_HOME)

## Flujos de Trabajo Comunes

**Agregar una nueva tela:**
1. Agregar entrada a `backend/app/data/fabrics.json`
2. Ejecutar `python seed.py` para poblar la base de datos
3. O usar la UI admin en `http://localhost:3000/admin`

**Modificar parámetros de generación:**
1. Actualizar variables de entorno en `.env` o script de despliegue
2. Reiniciar servidor backend
3. No se necesitan cambios de código para ajustar guidance/steps/weights

**Cambiar backends de almacenamiento:**
1. Establecer `storage_backend=r2` en `.env`
2. Proporcionar credenciales R2
3. Reiniciar backend - la capa de almacenamiento está inyectada por dependencia

**Agregar nuevos campos de base de datos:**
1. Modificar modelos en `app/admin/models.py`
2. Crear migración: `alembic revision --autogenerate -m "descripción"`
3. Revisar migración generada en `alembic/versions/`
4. Aplicar: `alembic upgrade head`

## Estilo de Código y Convenciones

- **Backend**: Patrón de inyección de dependencias FastAPI, Pydantic para validación, ORM SQLAlchemy
- **Frontend**: Hooks de React para estado, TypeScript modo estricto, Tailwind para estilos
- **Referencias de archivos**: Usar patrón `file_path:line_number` cuando se referencien ubicaciones de código
- **Manejo de errores**: Manejadores de error personalizados en `app/errors.py`, FastAPI HTTPException para errores de API
