# 🚀 Inicio Rápido - Sistema Completo End-to-End

Esta guía te permite tener el sistema funcionando en **3 minutos**.

---

## ⚡ Opción 1: Un Solo Comando (Recomendado)

### Windows (PowerShell/CMD):

```bash
cd D:\OneDrive\Escritorio\Dev\hf-virtual-stylist
.\start-all.bat
```

### Mac/Linux:

```bash
cd /path/to/hf-virtual-stylist
chmod +x start-all.sh
./start-all.sh
```

Esto iniciará **3 procesos** en terminales separadas:
1. **Backend API** - Puerto 8000
2. **Worker** - Procesa generaciones con MockGenerator
3. **Frontend** - Puerto 3000

---

## 🔧 Opción 2: Manualmente (3 Terminales)

### Terminal 1: Backend API

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

✅ **Verificar**: Abrir http://localhost:8000/docs - deberías ver la documentación de FastAPI.

---

### Terminal 2: Worker (Procesador de Jobs)

```bash
cd backend
# Activar venv (mismo comando de arriba)
venv\Scripts\activate  # Windows
# o
source venv/bin/activate  # Mac/Linux

# Verificar que USE_MOCK_GENERATOR=true en .env
python worker.py
```

**Deberías ver:**
```
============================================================
🎨 HF Virtual Stylist - Generation Worker
============================================================
Database: postgresql://neondb_owner...
Storage: r2
Generator: Mock
============================================================
✅ [Worker] Using Cloudflare R2 backend.
✅ [Worker] Using Mock generator.
🚀 [Worker] Starting worker loop (polling every 5s)...
```

✅ **Verificar**: El worker está corriendo y haciendo polling cada 5 segundos.

---

### Terminal 3: Frontend

```bash
cd frontend
npm install
npm run dev
```

✅ **Verificar**: Abrir http://localhost:3000 - deberías ver la interfaz del estilista.

---

## 🎨 Probar el Flujo Completo

1. **Abre** http://localhost:3000
2. **Selecciona** una familia de tela (ej: "Algodón Tech")
3. **Selecciona** un color (ej: "Negro")
4. **Click** en "Generar"
5. **Espera** ~5-10 segundos (el worker está procesando)
6. **¡Listo!** Deberías ver 2 imágenes placeholder generadas

---

## 🔍 Troubleshooting

### ❌ Frontend dice "Network error"

**Problema**: Backend no está corriendo.

**Solución**:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

---

### ❌ Job queda en "pending" por siempre

**Problema**: Worker no está corriendo.

**Solución**:
```bash
cd backend
python worker.py
```

**Verificar en .env**:
```env
USE_MOCK_GENERATOR="true"
```

---

### ❌ Worker dice "ModuleNotFoundError"

**Problema**: Dependencias no instaladas o venv no activado.

**Solución**:
```bash
cd backend
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

### ❌ Worker dice "Database connection error"

**Problema**: DATABASE_URL no configurado o base de datos no accesible.

**Solución**:

1. **Para desarrollo local** (SQLite):
```env
# backend/.env
DATABASE_URL=sqlite:///./storage/app.db
```

2. **Ejecutar migraciones**:
```bash
cd backend
alembic upgrade head
python seed.py
```

---

### ❌ Imágenes no se muestran en frontend

**Problema**: Storage mal configurado.

**Solución para desarrollo local**:
```env
# backend/.env
STORAGE_BACKEND=local
PUBLIC_BASE_URL=http://localhost:8000/files
```

**Solución para producción (R2)**:
```env
# backend/.env
STORAGE_BACKEND=r2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=harris-and-frank
R2_PUBLIC_URL=https://pub-xxxxxx.r2.dev
```

---

## 🎯 Siguiente Paso: Conectar al Pod GPU

Para usar **generación real con SDXL** en lugar de MockGenerator:

1. **Desplegar en RunPod**:
```bash
cd backend/devops/runpod
./deploy.sh
```

2. **Cambiar .env**:
```env
USE_MOCK_GENERATOR=false
```

3. **Reiniciar worker**:
```bash
python worker.py
```

---

## 📋 Verificación Completa

- [ ] Backend corriendo en puerto 8000
- [ ] Worker corriendo y haciendo polling
- [ ] Frontend corriendo en puerto 3000
- [ ] Catálogo se carga correctamente
- [ ] Botón "Generar" funciona
- [ ] Imágenes placeholder aparecen en ~5-10 segundos
- [ ] Imágenes son visibles y tienen marca de agua

---

## 🆘 ¿Aún tienes problemas?

Revisa los logs en cada terminal para ver errores específicos.

**Última actualización:** 2025-11-03
