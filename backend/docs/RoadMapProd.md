 ---
  Arquitectura Actual

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                              FLUJO COMPLETO                                  │
  └─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────┐         ┌──────────┐         ┌──────────────┐
    │  Vercel  │         │ Railway  │         │   Railway    │
    │ Frontend │ ──────► │   API    │ ──────► │  PostgreSQL  │
    │ Next.js  │         │ FastAPI  │         │     DB       │
    └──────────┘         └──────────┘         └──────┬───────┘
         │                                          │
         │                                          │ polling cada 5s
         │                                          ▼
         │                                   ┌──────────────┐
         │                                   │   RunPod     │
         │                                   │  worker.py   │
         │                                   │    (GPU)     │
         │                                   └──────┬───────┘
         │                                          │
         │                                          │ genera imágenes
         │                                          ▼
         │                                   ┌──────────────┐
         │                                   │ Cloudflare   │
         │◄──────────────────────────────────│     R2       │
         │   URLs públicas de imágenes       │   Storage    │
         └───────────────────────────────────└──────────────┘

  ---
  Flujo Detallado

  1. Usuario selecciona tela + color en Frontend
                      │
                      ▼
  2. POST /generate → Railway API
     {family_id, color_id, cuts, swatch_url}
                      │
                      ▼
  3. API crea job en PostgreSQL
     status: "pending"
     Retorna: {job_id} inmediatamente
                      │
                      ▼
  4. Frontend hace polling: GET /jobs/{job_id}
     (cada 2-3 segundos)
                      │
     ═══════════════════════════════════════
                      │
  5. RunPod worker.py (loop infinito)
     - Query: SELECT * FROM jobs WHERE status='pending' ORDER BY created_at
     - Toma el job más viejo
                      │
                      ▼
  6. Worker procesa:
     - status → "processing"
     - Carga modelos SDXL (singleton, cacheados)
     - Genera imagen con ControlNet + IP-Adapter
     - Aplica watermark
     - Sube a R2
                      │
                      ▼
  7. Worker actualiza job:
     - status → "completed"
     - result_urls: ["https://r2.dev/image1.jpg", ...]
                      │
     ═══════════════════════════════════════
                      │
                      ▼
  8. Frontend polling detecta status="completed"
     - Muestra imágenes usando las URLs de R2

  ---
  Decisiones Técnicas YA TOMADAS ✅
  ┌───────────────┬────────────────────────────────────┬────────────────────────────────────────────────┐
  │     Área      │              Decisión              │                 Justificación                  │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Base de Datos │ PostgreSQL único (Neon)         │ Simplicidad, sin SQLite                        │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Arquitectura  │ Worker separado (no API en RunPod) │ API ligera en Railway, GPU solo genera         │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Storage       │ Cloudflare R2                      │ CDN global, S3-compatible, económico           │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Job Queue     │ Polling DB (no Redis/RabbitMQ)     │ Simplicidad, suficiente para el volumen        │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Generación    │ SDXL + ControlNet + IP-Adapter     │ Calidad fotorrealista + guía de pose + textura │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Watermark     │ Aplicado antes de subir a R2       │ Protección de imágenes                         │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Frontend      │ Vercel + Next.js                   │ Deploy automático, edge functions              │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Swatch URLs   │ Híbrido: DB + User Upload          │ Catálogo desde DB, usuarios suben a R2 temp    │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ User Uploads  │ POST /upload-swatch → R2 temp      │ Consistencia con arquitectura R2 existente     │
  ├───────────────┼────────────────────────────────────┼────────────────────────────────────────────────┤
  │ Temp Cleanup  │ R2 Lifecycle Rules (24h)           │ Zero code, fully managed, auto-delete          │
  └───────────────┴────────────────────────────────────┴────────────────────────────────────────────────┘

  ---
  Detalle: Swatch URLs (RESUELTO ✅)

  Flujo para swatches del catálogo:
  1. DB tiene campo `swatch_code` (ej: "095T-0121")
  2. GET /catalog construye URL: {R2_PUBLIC_URL}/ZEGNA%202025-26/{swatch_code}.png
  3. Frontend recibe swatch_url listo para usar

  Flujo para uploads de usuario:
  1. Usuario selecciona imagen en frontend
  2. POST /upload-swatch con FormData
  3. Backend valida (tipo: jpeg/png/webp, tamaño: max 5MB)
  4. Sube a R2: temp-uploads/{uuid}.{ext}
  5. Retorna URL pública
  6. Frontend incluye URL en POST /generate → se guarda en generation_jobs.swatch_url
  7. Worker usa esa URL con IP-Adapter

  Cleanup automático:
  - R2 Lifecycle Rule: objetos en temp-uploads/ expiran en 24 horas
  - Configurado en Cloudflare Dashboard (no requiere código)

  ---
  Decisiones PENDIENTES ❓
  Área: Escalabilidad
  Pregunta: ¿Múltiples workers en RunPod?
  Opciones: A) Un solo pod siempre encendido, B) Múltiples pods, C) Serverless (encender/apagar)
  ────────────────────────────────────────
  Área: Autenticación
  Pregunta: ¿Proteger endpoint /generate?
  Opciones: A) Abierto (actual), B) API key, C) JWT
  ────────────────────────────────────────
  Área: Rate Limiting
  Pregunta: ¿Limitar requests por usuario/IP?
  Opciones: A) Sin límite, B) X requests/minuto
  ────────────────────────────────────────
  Área: Costos RunPod
  Pregunta: ¿Pod siempre encendido o on-demand?
  Opciones: A) Siempre on ($$$), B) On-demand (latencia inicial)
  ────────────────────────────────────────
  Área: Admin Panel
  Pregunta: ¿Donde se accede?
  Opciones: Ya existe en /admin pero ¿autenticación?
  ---