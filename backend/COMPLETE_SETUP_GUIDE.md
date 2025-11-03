# HF Virtual Stylist - Guía de Configuración Completa

## 📚 Tabla de Contenidos
1. [Descripción General del Proyecto](#descripción-general-del-proyecto)
2. [Arquitectura](#arquitectura)
3. [Sistema de Muestras de Tela](#sistema-de-muestras-de-tela)
4. [Pipeline de Organización de Color](#pipeline-de-organización-de-color)
5. [Guía de Despliegue](#guía-de-despliegue)
6. [Solución de Problemas](#solución-de-problemas)

---

## Descripción General del Proyecto

**HF Virtual Stylist** es una aplicación de visualización y estilismo digital de trajes potenciada por IA que genera renders fotorrealistas de trajes usando Stable Diffusion XL. Los asociados de ventas seleccionan telas y colores, y el sistema produce visualizaciones potenciadas por SDXL.

### Stack Tecnológico
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL (Neon) + Migraciones Alembic
- **Frontend:** Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **IA/ML:** Stable Diffusion XL + ControlNet + IP-Adapter
- **Almacenamiento:** Cloudflare R2 (para muestras e imágenes generadas)
- **Despliegue:** Railway (backend) + Vercel (frontend)

### Características Clave
- ✅ 83 muestras de tela organizadas por familia de color
- ✅ Detección de color potenciada por IA y categorización
- ✅ Generación fotorrealista de trajes con control de pose
- ✅ Generación asíncrona basada en trabajos con polling
- ✅ Dashboard admin para gestión de telas
- ✅ UI responsive y móvil-amigable

---

## Arquitectura

### Flujo del Sistema
```
Selección Usuario → Frontend → Backend API → Cola de Trabajos → Pipeline SDXL → Almacenamiento R2 → Visualización
     ↓                                         ↓
API Catálogo ← Base de Datos ← Análisis de Color ← Muestras R2
```

### Descripción de Componentes

**Backend** (`backend/`)
```
app/
├── admin/              # Auth admin, CRUD, esquemas
├── core/               # Config, sesión base de datos
├── models/             # Esquemas Pydantic
├── routers/            # Manejadores de ruta FastAPI
│   ├── catalog.py      # Endpoint público del catálogo
│   └── generate.py     # Endpoints de trabajo de generación
├── services/           # Lógica de negocio
│   ├── generator.py    # Generación SDXL
│   └── storage.py      # Almacenamiento R2/local
└── data/               # Datos seed (fabrics.json)
```

**Frontend** (`frontend/`)
```
src/
├── app/                # Next.js App Router
│   ├── page.tsx        # UI principal del estilista
│   └── admin/          # Dashboard admin
├── components/         # Componentes React
│   ├── CatalogSelector.tsx    # Selector de tela/color
│   └── GeneratedImageGallery.tsx
├── hooks/              # Hooks React personalizados
│   └── useVirtualStylist.ts   # Gestión de estado
└── lib/                # Clientes API
    ├── apiClient.ts    # API pública
    └── adminApi.ts     # API admin
```

---

## Sistema de Muestras de Tela

### Estructura del Bucket R2
```
Bucket R2: harris-and-frank
URL Pública: https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev

├── ZEGNA 2025-26/          ← 83 muestras de tela (PNG, ~1-1.5 MB cada una)
│   ├── 095T-0121.png
│   ├── 095T-0132.png
│   ├── 33125.png
│   └── ... (80 más)
└── generated/              ← Imágenes generadas por IA
    └── {family_id}/{color_id}/{run_id}/{cut}.jpg
```

**Notas Importantes de Ruta:**
- ❌ **NO** `harris-and-frank/ZEGNA 2025-26/` (anidado)
- ✅ **ES** `ZEGNA 2025-26/` (nivel raíz del bucket)

### Esquema de Base de Datos

**Tabla FabricFamily:**
```sql
CREATE TABLE fabric_families (
    id INTEGER PRIMARY KEY,
    family_id VARCHAR UNIQUE NOT NULL,  -- ej. "azules", "grises"
    display_name VARCHAR NOT NULL,       -- ej. "Azules", "Grises"
    status VARCHAR NOT NULL DEFAULT 'active'
);
```

**Tabla Color:**
```sql
CREATE TABLE colors (
    id INTEGER PRIMARY KEY,
    fabric_family_id INTEGER REFERENCES fabric_families(id) ON DELETE CASCADE,
    color_id VARCHAR UNIQUE NOT NULL,    -- ej. "az-095T-0121"
    name VARCHAR NOT NULL,                -- ej. "Azul Oscuro"
    hex_value VARCHAR NOT NULL,           -- ej. "#0A1D3A"
    swatch_code VARCHAR,                  -- ej. "095T-0121" (nombre de archivo R2)
    swatch_url VARCHAR                    -- URL auto-generada o explícita
);
```

### Generación de URL

**Automática (preferida):** Establecer `swatch_code` y la API construye la URL:

```python
# backend/app/routers/catalog.py:53-56
if c.swatch_code and settings.r2_public_url:
    swatch_path = f"ZEGNA%202025-26/{quote(c.swatch_code)}.png"
    swatch_url = f"{settings.r2_public_url}/{swatch_path}"
```

**Manual (respaldo):** Establecer `swatch_url` directamente en la base de datos.

**Ejemplo de URL Generada:**
```
https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/ZEGNA%202025-26/095T-0121.png
```

### Integración Frontend

El componente `CatalogSelector` (`frontend/src/components/CatalogSelector.tsx:51-66`) maneja automáticamente la visualización de muestras:

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
  <div style={{ backgroundColor: color.hex }} />  // Respaldo a hex
)}
```

**¡No se necesitan cambios en el frontend!**

---

## Pipeline de Organización de Color

### Descripción General
Categoriza automáticamente 50-100+ muestras de tela en familias de color usando análisis de color potenciado por IA.

### Flujo del Proceso
```
1. Listar Muestras (R2)
   ↓
2. Descargar y Analizar Colores (IA)
   ↓
3. Categorizar en Familias
   ↓
4. Generar Nombres en Español
   ↓
5. Poblar Base de Datos
```

### Scripts

#### 1. `list_r2_swatches.py` - Listar Todas las Muestras

**Propósito:** Obtener todos los nombres de archivo de muestras del bucket R2

**Uso:**
```bash
python list_r2_swatches.py
```

**Salida:**
- Consola: Lista de todos los códigos de muestra con tamaños
- Archivo: `swatch_codes_list.txt`

**Ejemplo de Salida:**
```
📦 Listing swatches from bucket: harris-and-frank
📁 Folder: ZEGNA 2025-26/

✅ Found 83 swatch images:

  1. 095T-0121      (  1.38 MB)
  2. 095T-0132      (  1.43 MB)
  ...
 83. P993N-913P     (  0.91 MB)
```

#### 2. `organize_swatches_by_color.py` - Análisis de Color IA

**Propósito:** Descargar muestras, analizar colores dominantes, categorizar en familias

**Algoritmo:**
1. **Descargar** imagen de muestra desde R2
2. **Recortar** al centro 70% (evitar bordes/fondos)
3. **Filtrar** valores de brillo extremos (bordes, flash)
4. **Extraer** los 10 colores más frecuentes
5. **Ponderar** por saturación (preferir colorido sobre neutral)
6. **Convertir** a espacio de color HSV
7. **Categorizar** por matiz, saturación y valor
8. **Generar** nombres de color en español

**Familias de Color:**
- **Azules** (Blues): H 190-250°, S > 0.2
- **Grises** (Grays): S < 0.12, V 0.25-0.75
- **Marrones y Beiges** (Browns): H 20-45°, S > 0.15
- **Negros y Blancos** (Black/White): V < 0.10 o V > 0.90 + S < 0.05
- **Verdes** (Greens): H 80-170°, S > 0.2
- **Tonos Cálidos** (Warm): H 0-20°, S > 0.3
- **Tonos Fríos** (Cool): H 250-290°, S > 0.2

**Uso:**
```bash
python organize_swatches_by_color.py
```

**Salida:**
- Consola: Progreso de análisis en tiempo real
- Archivo: `swatch_categorization.json`

**Ejemplo de Salida:**
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

**Mejoras del Algoritmo (Última Versión):**
- ✅ Recorte central para evitar bordes blancos
- ✅ Filtrar brillo extremo (rango 20-235)
- ✅ Promediado de color ponderado por saturación
- ✅ Umbrales negro/blanco más estrictos (0.10/0.90 vs 0.15/0.85)
- ✅ Top 10 colores para mejor precisión

#### 3. `populate_color_families.py` - Población de Base de Datos

**Propósito:** Crear familias de telas y colores en la base de datos desde categorización

**Uso:**
```bash
# Previsualizar primero (recomendado)
python populate_color_families.py --preview

# Poblar base de datos
python populate_color_families.py
```

**Lo que hace:**
1. Lee `swatch_categorization.json`
2. Limpia familias/colores existentes (opcional)
3. Crea 7 familias de telas
4. Crea ~83 registros de color
5. Establece `swatch_code` para cada color
6. Hace commit a la base de datos

**Características de Seguridad:**
- Flag `--preview` para previsualizar sin cambios
- Prompt de confirmación antes de eliminación
- Rollback de transacción en errores

**Salida:**
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

## Guía de Despliegue

### Railway (Backend)

**Requisitos Previos:**
- Cuenta Railway
- Repo GitHub conectado
- Base de datos PostgreSQL (Neon) provisionada

**Variables de Entorno:**
```env
# Base de Datos
DATABASE_URL=postgresql://user:pass@host/db

# Admin
ADMIN_PASSWORD=secure-password
JWT_SECRET=long-random-string
JWT_ALGORITHM=HS256

# Almacenamiento
STORAGE_BACKEND=r2
R2_ACCOUNT_ID=227469b74b82faacc40b017f9123aa27
R2_ACCESS_KEY_ID=5025ea72fa42e55d568f775f62f5ef63
R2_SECRET_ACCESS_KEY=945657b921de4459a6c0a70a33a685b8dbbb92b2ce0fa8ec4b6c2343678dfb62
R2_BUCKET_NAME=harris-and-frank
R2_PUBLIC_URL=https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev

# Generación (opcional - para pods GPU)
CONTROLNET_ENABLED=1
IP_ADAPTER_ENABLED=1
...
```

**Pasos de Despliegue:**
1. Push código a rama `main`
2. Railway auto-despliega
3. Ejecutar migraciones: `alembic upgrade head`
4. Ejecutar scripts de organización (ver abajo)
5. Verificar endpoint del catálogo

**Tareas Post-Despliegue:**
```bash
# SSH al contenedor Railway
railway shell

# Ejecutar migraciones
python -m alembic upgrade head

# Organizar muestras
python list_r2_swatches.py
python organize_swatches_by_color.py
python populate_color_families.py

# Verificar
curl https://your-app.railway.app/catalog | jq '.families | length'
# Debería retornar: 7
```

### Vercel (Frontend)

**Requisitos Previos:**
- Cuenta Vercel
- Repo GitHub conectado

**Variables de Entorno:**
```env
NEXT_PUBLIC_API_BASE=https://hf-virtual-stylist-production.up.railway.app
```

**Despliegue:**
1. Push código a `main`
2. Vercel auto-despliega
3. Establecer variable de entorno en dashboard Vercel
4. Re-desplegar si es necesario

**Verificación:**
```bash
# Probar catálogo desde frontend
curl https://your-app.vercel.app/api/catalog | jq '.families[0].colors[0]'

# Debería incluir swatch_url:
{
  "color_id": "az-095T-0121",
  "name": "Azul Oscuro",
  "hex": "#0A1D3A",
  "swatch_url": "https://pub-56...r2.dev/ZEGNA%202025-26/095T-0121.png"
}
```

---

## Solución de Problemas

### Muestras No Se Visualizan (errores 404)

**Síntomas:**
```
⨯ upstream image response failed for https://pub-.../fabrics/095T-0121.png 404
```

**Causas y Soluciones:**

1. **Ruta R2 incorrecta:**
   - ❌ `/fabrics/` o `/harris-and-frank/ZEGNA 2025-26/`
   - ✅ `/ZEGNA 2025-26/`
   - **Fix:** Ejecutar `python fix_swatch_paths.py`

2. **Falta `swatch_code` en base de datos:**
   ```sql
   SELECT color_id, swatch_code FROM colors WHERE swatch_code IS NULL;
   ```
   - **Fix:** Re-ejecutar `populate_color_families.py`

3. **R2 no es públicamente accesible:**
   - Verificar dashboard Cloudflare R2 → configuración de Acceso Público
   - **Fix:** Habilitar lectura pública o crear dominio de URL pública

4. **R2_PUBLIC_URL incorrecta:**
   ```bash
   # Verificar .env
   echo $R2_PUBLIC_URL
   # Debería ser: https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev
   ```

### Problemas de Detección de Color

**Problema:** La mayoría de muestras categorizadas como "Negros y Blancos"

**Causa:** Bordes blancos o fondos en imágenes de muestras

**Solución:** El algoritmo ya maneja esto (v2):
- ✅ Recorta al centro 70%
- ✅ Filtra brillo extremo
- ✅ Ponderación por saturación

**Si persisten problemas:**
- Ajustar umbrales en `organize_swatches_by_color.py`
- Editar manualmente `swatch_categorization.json`
- Re-ejecutar `populate_color_families.py`

### Errores de Migración de Base de Datos

**Error:** `Target database is not up to date`

**Solución:**
```bash
# Verificar versión actual
alembic current

# Aplicar todas las migraciones
alembic upgrade head

# Si hay problemas, verificar historial de migración
alembic history --verbose
```

**Error:** `Multiple head revisions present`

**Solución:**
```bash
# Fusionar heads
alembic merge heads -m "merge migrations"
alembic upgrade head
```

### Frontend No Carga Catálogo

**Síntomas:** Selector de color vacío, cargando indefinidamente

**Debugging:**
```bash
# Probar backend directamente
curl https://your-railway-app.railway.app/catalog

# Verificar consola del navegador (F12)
# Buscar errores CORS, 404s, o fallos de red

# Verificar rewrites de Next.js
# Verificar frontend/next.config.ts:
async rewrites() {
  return [{ source: "/api/:path*", destination: `${API_BASE}/:path*` }];
}
```

**Soluciones:**
- Verificar variable de entorno `NEXT_PUBLIC_API_BASE`
- Reiniciar servidor dev frontend
- Limpiar caché `.next`: `rm -rf .next`

---

## Referencia de Archivos

### Scripts Backend
- `list_r2_swatches.py` - Lista todas las muestras desde R2
- `organize_swatches_by_color.py` - Análisis de color IA
- `populate_color_families.py` - Población de base de datos
- `fix_swatch_paths.py` - Corrige URLs de muestras incorrectas
- `swatch_mapping.py` - Mapeo manual de código de muestra (alternativa)

### Archivos Generados
- `swatch_codes_list.txt` - Lista de texto plano de códigos
- `swatch_categorization.json` - Resultados de análisis completo con valores HSV

### Documentación
- `COMPLETE_SETUP_GUIDE.md` - Este archivo
- `ORGANIZE_SWATCHES_README.md` - Detalles de organización de color
- `SWATCH_SETUP.md` - Configuración del sistema de muestras (legacy)
- `CLAUDE.md` - Descripción general del proyecto para asistente IA

---

## Últimas Actualizaciones

### 2025-10-30: Correcciones de Ruta y Mejoras de Algoritmo
- ✅ Corregida ruta R2 de `/fabrics/` a `/ZEGNA 2025-26/`
- ✅ Mejorado algoritmo de detección de color (recorte central, ponderación por saturación)
- ✅ Umbrales negro/blanco más estrictos (0.10/0.90)
- ✅ Probado con 83 muestras reales de colección ZEGNA
- ✅ Backend Railway desplegado exitosamente
- ✅ Frontend Vercel mostrando imágenes de muestras

### 2025-10-29: Sistema Inicial de Muestras
- ✅ Agregada columna `swatch_code` al modelo Color
- ✅ Creada migración Alembic
- ✅ Implementada generación automática de URL
- ✅ Creado pipeline de organización de color

---

## Soporte y Contribución

**Para Problemas:**
1. Verificar esta guía primero
2. Revisar commits recientes de git
3. Verificar logs de Railway/Vercel
4. Consultar documentación API del backend

**Para Desarrollo:**
- Backend: `backend/README.md`
- Frontend: `frontend/CLAUDE.md`
- Docs API: endpoint `/docs` (FastAPI)

---

**Última Actualización:** 2025-10-30
**Versión:** 1.0.0
**Mantenedores:** Equipo de Desarrollo
