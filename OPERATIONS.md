# OPERATIONS.md - Guía de Operaciones y Handover

Este documento contiene toda la información necesaria para operar, mantener y desplegar el sistema HF Virtual Stylist en producción.

---

## Tabla de Contenidos

1. [Inventario de Servicios](#inventario-de-servicios)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Configuración de RunPod desde Cero](#configuración-de-runpod-desde-cero)
4. [Variables de Entorno](#variables-de-entorno)
5. [Operaciones Rutinarias](#operaciones-rutinarias)
6. [Troubleshooting](#troubleshooting)
7. [Referencia de Credenciales](#referencia-de-credenciales)

---

## Inventario de Servicios

| Servicio | Propósito | Dashboard |
|----------|-----------|-----------|
| **Railway** | API Backend (FastAPI) | https://railway.com/dashboard |
| **Neon** | Base de datos PostgreSQL | https://console.neon.tech/app/org-tiny-lake-15957964/projects |
| **RunPod** | GPU Worker (generación SDXL) | https://console.runpod.io/deploy |
| **Cloudflare R2** | Almacenamiento de imágenes | https://dash.cloudflare.com/438d9ee1e3edea5f2d8a625578fe5889/r2/plans |
| **Vercel** | Frontend (Next.js) | https://vercel.com/hf-virtual-stylists-projects |
| **GitHub** | Repositorio de código | (enlace al repo) |

### Descripción de cada servicio

**Railway**
- Ejecuta la API FastAPI que maneja requests del frontend
- Endpoints: `/catalog`, `/generate`, `/jobs/{id}`, `/admin/*`
- NO ejecuta generación de imágenes - solo crea jobs en la base de datos
- Escala automáticamente según demanda

**Neon (PostgreSQL)**
- Base de datos compartida entre Railway (API) y RunPod (Worker)
- Tablas principales: `fabric_families`, `colors`, `generation_jobs`
- Connection pooling habilitado para manejar múltiples conexiones

**RunPod**
- Ejecuta `worker.py` que hace polling de la BD cada 5 segundos
- Procesa jobs pendientes con SDXL/Inpainting
- Requiere GPU (recomendado: RTX 4090 o A100)
- Sube imágenes generadas a R2

**Cloudflare R2**
- Almacena imágenes generadas y swatches de telas
- Bucket: `harris-and-frank`
- Acceso público habilitado para servir imágenes

**Vercel**
- Hospeda el frontend Next.js
- Proxy automático de `/api/*` hacia Railway
- Deploys automáticos desde GitHub

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USUARIO                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         VERCEL (Frontend)                                │
│                         Next.js 15 + React 19                            │
│                         https://hf-virtual-stylist.vercel.app            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                          /api/* proxy rewrite
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RAILWAY (API Backend)                            │
│                         FastAPI + SQLAlchemy                             │
│                         POST /generate → crea job "pending"              │
│                         GET /jobs/{id} → retorna status                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         NEON (PostgreSQL)                                │
│                         Tabla: generation_jobs                           │
│                         status: pending → processing → completed         │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▲
                          polling cada 5s
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                         RUNPOD (GPU Worker)                              │
│                         worker.py                                        │
│                         SDXL Inpainting + IP-Adapter Plus                │
│                         RTX 4090 / A100                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                          upload imágenes
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLOUDFLARE R2                                    │
│                         Bucket: harris-and-frank                         │
│                         URL pública: https://pub-xxx.r2.dev              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Flujo de generación de imágenes

1. **Usuario** selecciona tela y color en el frontend
2. **Frontend** envía POST a `/api/generate`
3. **Vercel** proxy reescribe a Railway
4. **Railway API** crea registro en `generation_jobs` con `status=pending`
5. **Railway API** retorna `job_id` inmediatamente
6. **Frontend** hace polling a `/api/jobs/{job_id}`
7. **RunPod Worker** detecta job pendiente
8. **Worker** actualiza status a `processing`
9. **Worker** ejecuta SDXL Inpainting con IP-Adapter
10. **Worker** sube imagen a R2
11. **Worker** actualiza job con URLs y `status=completed`
12. **Frontend** recibe URLs en siguiente poll
13. **Usuario** ve imágenes generadas

---

## Configuración de RunPod desde Cero

### Paso 1: Crear cuenta en RunPod

1. Ir a https://console.runpod.io
2. Iniciar sesión
3. Agregar método de pago (créditos prepagados)

### Paso 2: Crear Network Volume

El Network Volume persiste datos entre reinicios del pod (modelos, venv, código).

1. Ir a **Storage** → **Network Volumes**
2. Click **+ New Network Volume**
3. Configurar:
   - **Name**: `hf-stylist-vol` (o similar)
   - **Region**: Seleccionar región cercana (ej: US-East)
   - **Size**: 50GB mínimo (modelos SDXL ocupan ~15GB)
4. Click **Create**

### Paso 3: Crear Pod

1. Ir a **Pods** → **+ Deploy**
2. Seleccionar GPU:
   - **Recomendado**: RTX 4090 (24GB VRAM) o A100 (40GB)
   - **Mínimo**: RTX 3090 (24GB VRAM)
3. Seleccionar template:
   - **RunPod Pytorch 2.1** o similar con CUDA
4. Configurar:
   - **Container Disk**: 20GB
   - **Volume Disk**: Seleccionar el Network Volume creado
   - **Volume Mount Path**: `/workspace`
5. **IMPORTANTE**: Configurar variables de entorno (ver siguiente sección)
6. Click **Deploy**

### Paso 4: Configurar Variables de Entorno

En la configuración del pod, agregar estas variables:

```bash
# ═══════════════════════════════════════════════════════════════════════════
# BASE DE DATOS (Neon PostgreSQL)
# ═══════════════════════════════════════════════════════════════════════════
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# ═══════════════════════════════════════════════════════════════════════════
# ALMACENAMIENTO (Cloudflare R2)
# ═══════════════════════════════════════════════════════════════════════════
R2_ACCOUNT_ID=438d9ee1e3edea5f2d8a625578fe5889
R2_ACCESS_KEY_ID=<access-key-desde-cloudflare>
R2_SECRET_ACCESS_KEY=<secret-key-desde-cloudflare>
R2_BUCKET_NAME=harris-and-frank
R2_PUBLIC_URL=https://pub-<tu-id>.r2.dev

# ═══════════════════════════════════════════════════════════════════════════
# MODO DE GENERACIÓN
# ═══════════════════════════════════════════════════════════════════════════
# Opciones: "inpaint" (recomendado), "full", "mock"
GENERATOR_MODE=inpaint
```

### Paso 5: Ejecutar deploy.sh

1. Conectar al pod via Web Terminal
2. Clonar el repositorio (primera vez):
   ```bash
   cd /workspace
   git clone https://github.com/TU_ORG/hf-virtual-stylist.git app
   ```
3. Ejecutar el script de despliegue:
   ```bash
   cd /workspace/app/backend
   chmod +x devops/runpod/deploy.sh
   ./devops/runpod/deploy.sh
   ```

### Qué hace deploy.sh

El script automatiza todo el setup:

1. **Crea Python 3.11 venv** en `/workspace/py311` (persiste en NV)
2. **Sincroniza código** desde `origin/main`
3. **Instala dependencias** de `requirements.txt`
4. **Configura variables** de entorno para SDXL:
   - Guidance scale, steps, refiner
   - ControlNet (depth + canny)
   - IP-Adapter Plus
   - Rutas de imágenes de control
5. **Verifica CUDA** y conexión a PostgreSQL
6. **Inicia worker.py** que comienza a procesar jobs

### Paso 6: Verificar funcionamiento

```bash
# Ver logs del worker
tail -f /workspace/app/backend/worker.log

# Verificar que está procesando
# Deberías ver: "🚀 [Worker] Starting worker loop (polling every 5s)..."

# Probar generación desde el frontend o con curl:
curl -X POST https://tu-api.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"azul-001","color_id":"azul-marino","cuts":["recto"]}'
```

---

## Dependencias (Requirements)

El backend tiene dos archivos de dependencias:

| Archivo | Uso | Tamaño |
|---------|-----|--------|
| `requirements.txt` | Railway, desarrollo local | ~100 MB |
| `requirements-gpu.txt` | RunPod (GPU worker) | ~3 GB |

**Para desarrollo local:**
```bash
cd backend
pip install -r requirements.txt
```

**Para RunPod:** El script `deploy.sh` usa automáticamente `requirements-gpu.txt`.

**Nota:** `requirements.txt` funciona en cualquier plataforma (macOS, Windows, Linux) y cualquier Python 3.10+. `requirements-gpu.txt` requiere Linux con CUDA y Python 3.11.

---

## Variables de Entorno

### RunPod (Worker GPU)

| Variable | Requerida | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `DATABASE_URL` | ✅ | Connection string PostgreSQL | `postgresql://user:pass@host/db` |
| `R2_ACCOUNT_ID` | ✅ | ID de cuenta Cloudflare | `438d9ee1e3edea5f2d8a625578fe5889` |
| `R2_ACCESS_KEY_ID` | ✅ | Access key del token R2 | `e0e1a12e2886...` |
| `R2_SECRET_ACCESS_KEY` | ✅ | Secret key del token R2 | `3b9d318d5ed8...` |
| `R2_BUCKET_NAME` | ✅ | Nombre del bucket | `harris-and-frank` |
| `R2_PUBLIC_URL` | ✅ | URL pública del bucket | `https://pub-xxx.r2.dev` |
| `GENERATOR_MODE` | ❌ | Modo de generación | `inpaint` (default) |
| `GUIDANCE` | ❌ | CFG scale | `4.3` (default) |
| `TOTAL_STEPS` | ❌ | Pasos de inferencia | `80` (default) |
| `INPAINT_STEPS` | ❌ | Pasos para inpainting | `100` (default) |

### Railway (API Backend)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `DATABASE_URL` | ✅ | Connection string PostgreSQL (mismo que RunPod) |
| `ADMIN_PASSWORD` | ✅ | Contraseña para endpoints admin |
| `JWT_SECRET` | ✅ | Secreto para firmar tokens JWT |
| `JWT_ALGORITHM` | ❌ | Algoritmo JWT (default: `HS256`) |
| `STORAGE_BACKEND` | ❌ | `local` o `r2` (para dev/prod) |

### Vercel (Frontend)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `NEXT_PUBLIC_API_BASE` | ✅ | URL del backend Railway |

---

## Operaciones Rutinarias

### Desplegar cambios de código

**Backend (Railway)**
- Railway detecta automáticamente pushes a `main`
- Deploy automático en ~2-3 minutos
- Verificar en Railway dashboard → Deployments

**Worker (RunPod)**
```bash
# Conectar al pod
# Opción 1: Web Terminal desde RunPod dashboard
# Opción 2: SSH si configuraste keys

# Actualizar código
cd /workspace/app
git fetch origin
git reset --hard origin/main

# Reiniciar worker
pkill -f worker.py
cd backend
source /workspace/py311/bin/activate
python worker.py
```

**Frontend (Vercel)**
- Push a `main` dispara deploy automático
- Verificar en Vercel dashboard → Deployments

### Agregar nuevas telas

**Opción 1: Vía Admin UI**
1. Ir a `https://hf-virtual-stylist-ai.vercel.app/admin`
2. Click "Agregar Familia"
3. Llenar campos y subir swatches

**Opción 2: Vía seed.py**
1. Editar `backend/app/data/fabrics.json`
2. Ejecutar en Railway o localmente:
   ```bash
   cd backend
   python seed.py
   ```

### Reiniciar servicios

**Railway (API)**
- Dashboard → hf-virtual-stylist → Settings → Restart

**RunPod (Worker)**
```bash
# Matar proceso actual
pkill -f worker.py

# Reiniciar
cd /workspace/app/backend
source /workspace/py311/bin/activate
nohup python worker.py > worker.log 2>&1 &
```

**Vercel (Frontend)**
- Hacer un push vacío o usar "Redeploy" en dashboard

### Ver logs

**Railway**
- Dashboard → Tu proyecto → Deployments → View Logs

**RunPod**
```bash
tail -f /workspace/app/backend/worker.log
# o
journalctl -f  # si usas systemd
```

**Vercel**
- Dashboard → Tu proyecto → Logs

### Monitorear jobs de generación

```sql
-- Conectar a Neon y ejecutar:

-- Jobs pendientes
SELECT * FROM generation_jobs WHERE status = 'pending' ORDER BY created_at;

-- Jobs fallidos (últimas 24h)
SELECT * FROM generation_jobs
WHERE status = 'failed'
AND created_at > NOW() - INTERVAL '24 hours';

-- Estadísticas
SELECT status, COUNT(*) FROM generation_jobs GROUP BY status;
```

---

## Troubleshooting

### El worker no procesa jobs

**Síntomas**: Jobs quedan en `pending` indefinidamente

**Verificar**:
1. ¿El pod de RunPod está corriendo?
   ```bash
   # En RunPod
   ps aux | grep worker
   ```

2. ¿Hay errores en los logs?
   ```bash
   tail -100 /workspace/app/backend/worker.log
   ```

3. ¿La conexión a la BD funciona?
   ```bash
   python -c "
   from sqlalchemy import create_engine, text
   import os
   engine = create_engine(os.environ['DATABASE_URL'])
   with engine.connect() as conn:
       print(conn.execute(text('SELECT 1')).scalar())
   "
   ```

**Soluciones comunes**:
- Reiniciar el worker
- Verificar que `DATABASE_URL` esté configurado
- Verificar que el pod tenga GPU disponible

### Imágenes no se muestran en el frontend

**Síntomas**: Jobs completan pero las imágenes no cargan

**Verificar**:
1. ¿Las URLs son correctas?
   ```sql
   SELECT result_urls FROM generation_jobs WHERE status = 'completed' LIMIT 1;
   ```

2. ¿El bucket R2 tiene acceso público?
   - Cloudflare Dashboard → R2 → Bucket → Settings → Public Access

3. ¿El hostname está permitido en `next.config.ts`?
   ```typescript
   // Verificar que el hostname de R2 esté en remotePatterns
   { protocol: "https", hostname: "pub-xxx.r2.dev" }
   ```

**Soluciones comunes**:
- Actualizar `next.config.ts` con el hostname correcto de R2
- Habilitar acceso público en el bucket R2
- Redesplegar frontend en Vercel

### Error de CUDA / GPU

**Síntomas**: `CUDA out of memory` o `CUDA not available`

**Verificar**:
```bash
# En RunPod
python -c "import torch; print(torch.cuda.is_available())"
nvidia-smi
```

**Soluciones**:
- Usar un pod con más VRAM (mínimo 24GB recomendado RTX 4090 / RTX 5090)
- Reducir batch size o resolución
- Reiniciar el pod para liberar memoria

### Jobs fallan con error de timeout

**Síntomas**: Jobs pasan a `failed` con error de conexión

**Causa probable**: Neon cierra conexiones inactivas después de 5 minutos

**Solución**: El worker ya tiene `pool_pre_ping=True` y `pool_recycle=300` configurados. Si persiste:
```bash
# Reiniciar worker para refrescar conexiones
pkill -f worker.py
python worker.py
```

### Frontend muestra error 500

**Verificar**:
1. ¿Railway está funcionando?
   ```bash
   curl hf-virtual-stylist-production.up.railway.app/healthz
   ```

2. ¿Las variables de entorno de Vercel están correctas?
   - `NEXT_PUBLIC_API_BASE` debe apuntar a Railway

3. Revisar logs en Vercel y Railway

---

## Referencia de Credenciales

### Dónde se almacena cada secreto

| Secreto | Ubicación | Cómo acceder |
|---------|-----------|--------------|
| `DATABASE_URL` | Neon Dashboard | Projects → Connection Details |
| R2 Credentials | Cloudflare Dashboard | R2 → Manage R2 API Tokens |
| `ADMIN_PASSWORD` | Railway Dashboard | Variables de entorno |
| `JWT_SECRET` | Railway Dashboard | Variables de entorno |

### Rotación de credenciales

**R2 API Token**:
1. Crear nuevo token en Cloudflare
2. Actualizar en RunPod y Railway
3. Verificar que funciona
4. Revocar token anterior

**DATABASE_URL**:
1. En Neon: Settings → Reset Password
2. Actualizar en Railway y RunPod
3. Reiniciar servicios

**JWT_SECRET**:
1. Generar nuevo secreto: `openssl rand -hex 32`
2. Actualizar en Railway
3. Todos los tokens activos se invalidarán

---

## Contacto y Soporte

Para problemas técnicos:
1. Revisar logs del servicio afectado
2. Consultar sección de Troubleshooting
3. Revisar issues en GitHub
4. Contactar al equipo de desarrollo

---

*Última actualización: Enero 2026*
