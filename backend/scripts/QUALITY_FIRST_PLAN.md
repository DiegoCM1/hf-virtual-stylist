# Plan de Testing Calidad-Primero: ControlNet → Afinación de Calidad → LoRA

**Creado**: 2025-11-01
**Objetivo**: Generación de trajes con máxima calidad y precisión de tela con cero deformación
**Presupuesto**: <90 segundos por imagen en GPU 4090

---

## 🎯 Resumen Ejecutivo

**El Enfoque Correcto:**
1. **Baseline ControlNet** (Fase 1) - Establecer estructura de traje PERFECTA con CERO deformación
2. **Afinación de Calidad** (Fase 2) - Maximizar calidad dentro del presupuesto de 90s
3. **Identificar la Brecha** (Fase 3) - Confirmar texturas genéricas (esperado)
4. **Entrenamiento LoRA** (Fase 4) - Enseñar a SDXL texturas específicas de tela desde fotos de catálogo

**¿Por Qué Este Orden?**
- ✅ ControlNet proporciona fundación geométrica (estructura)
- ✅ Afinación de calidad pule la fundación
- ✅ LoRA agrega texturas específicas de tela SIN pelear con ControlNet
- ❌ IP-Adapter PELEA con ControlNet y causa deformación

**Entendimiento Crítico:**
> **Las imágenes baseline (Fase 1-3) deben SER YA perfectas** (estructura, calidad, iluminación).
> **LoRA SOLO enseña texturas de tela** - NO arregla problemas de calidad.

---

## 🚫 ¿Por Qué NO IP-Adapter?

**Probamos IP-Adapter y descubrimos:**
- Scale 0.8+ = Toda textura, estructura de traje deformada
- Scale 0.3 = Mejor estructura pero no coincidencia precisa de patrón
- **Conflicto fundamental**: Transferencia de estilo visual de IP-Adapter PELEA con control geométrico de ControlNet

**IP-Adapter es la herramienta INCORRECTA para este caso de uso.**

**LoRA es la herramienta CORRECTA porque:**
- Enseña nuevos conceptos: "algodon-tech-negro-001 se ve ASÍ"
- Funciona ARMONIOSAMENTE con ControlNet (sin conflicto)
- Replicación precisa de patrón/textura desde fotos de catálogo
- Enfoque estándar de la industria para aprendizaje específico de objeto/textura

---

## 📋 Plan de Testing Fase por Fase

### Fase 1: Baseline ControlNet - Cero Deformación (20 minutos)

**Objetivo**: Encontrar pesos de ControlNet que produzcan estructura de traje PERFECTA

**Comandos de Test:**
```bash
# Usar corte único para iteración más rápida
--cuts=recto

# Test 1.1: Pesos de ControlNet Depth (previene deformación de cuerpo/pose)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=0.8
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.0
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.2
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.5

# Test 1.2: Pesos de ControlNet Canny (solapas/botones nítidos)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.5
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.7
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=0.9
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override canny_weight=1.1

# Test 1.3: Verificar combo ganador con segunda seed
python -m scripts.quick_gen --preset=baseline --seed=1234 --cuts=recto --override depth_weight=<GANADOR>,canny_weight=<GANADOR>
```

**Checklist de Evaluación:**
- [ ] Cero deformación en cuerpo/mangas del traje
- [ ] Bordes de solapa nítidos y rectos
- [ ] Filas de botones alineadas
- [ ] Caída profesional de sastrería
- [ ] Sin deformación en absoluto (¡más crítico!)

**Punto de Decisión**: Documentar pesos ganadores de ControlNet (ej., `depth_weight=1.2, canny_weight=0.7`)

---

### Fase 2: Techo de Calidad - Máxima Calidad (15 minutos)

**Objetivo**: Encontrar mejores configuraciones de calidad dentro del presupuesto de 90s

**Config Inicial**: Usar pesos ganadores de ControlNet de Fase 1

**Comandos de Test:**
```bash
# Test 2.1: Conteos de pasos (calidad vs tiempo tradeoff)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=60
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=80
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=100
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=120

# Test 2.2: Impacto del refiner (impulso de calidad vs costo de tiempo)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override refiner=false
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override refiner=true,refiner_split=0.7
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override refiner=true,refiner_split=0.8

# Test 2.3: Escala de guidance (adherencia al prompt vs creatividad)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override guidance=4.5
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override guidance=6.0
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override guidance=7.5

# Test 2.4: Verificar timing (asegurar < 90s en 4090)
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override steps=<GANADOR>,guidance=<GANADOR>,refiner=<GANADOR>
```

**Checklist de Evaluación:**
- [ ] Mejor calidad general de imagen (nitidez, detalle, coherencia)
- [ ] Fondo blanco limpio
- [ ] Iluminación de estudio profesional
- [ ] Dentro de presupuesto de generación de 90s
- [ ] Mantiene cero deformación de Fase 1

**Punto de Decisión**: Documentar config óptima de calidad (ej., `steps=100, guidance=6.5, refiner=true`)

---

### Fase 3: Identificar la Brecha - Análisis de Textura de Tela (5 minutos)

**Objetivo**: Confirmar que el baseline tiene texturas genéricas (no específicas de tela)

**Comandos de Test:**
```bash
# Generar con 2-3 telas diferentes usando config optimizada
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=algodon-tech --color=negro-001
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=lana-super-150 --color=azul-marino
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --fabric=cashmere-blend --color=gris-carbon
```

**Resultados Esperados:**
- ❌ Patrones de tela NO coinciden con catálogo (como se esperaba)
- ❌ Texturas son "tela de traje" genérica de SDXL
- ✅ Estructura de traje es perfecta (de Fase 1)
- ✅ Calidad general es excelente (de Fase 2)

**Insight Crítico:**
> Esto NO es un fracaso - es el baseline esperado.
> Tenemos estructura perfecta + calidad, pero texturas genéricas.
> **Aquí es donde entra LoRA** para cerrar la brecha de textura.

---

### Fase 4: Entrenamiento LoRA - Transferencia Precisa de Textura de Tela

**Requisitos Previos:**
- ✅ Fase 1-3 completa con baseline perfecto
- ✅ Baseline produce imágenes 5 estrellas con texturas genéricas
- ✅ Pesos de ControlNet documentados y bloqueados

**Flujo de Trabajo de Entrenamiento LoRA:**

#### Paso 1: Recolección de Datos (Por Tela - 1 hora por tela)

Recolectar 15-20 fotos de catálogo de alta calidad de cada tela:

```
Requisitos:
- Alta resolución (2048px+ preferido)
- Textura de tela visible claramente
- Iluminación consistente
- Varios ángulos/pliegues mostrando comportamiento de tela
- Fondo mínimo (recortar a tela si es necesario)

Estructura de directorio:
/workspace/lora_training/
├── algodon-tech-negro-001/
│   ├── IMG_0001.jpg  (15-20 imágenes)
├── lana-super-150-azul-marino/
│   ├── IMG_0001.jpg  (15-20 imágenes)
└── cashmere-blend-gris-carbon/
    ├── IMG_0001.jpg  (15-20 imágenes)
```

#### Paso 2: Configuración de Entorno de Entrenamiento (30 minutos)

Instalar Kohya_ss en RunPod:

```bash
cd /workspace
git clone https://github.com/bmaltais/kohya_ss
cd kohya_ss
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Lanzar GUI
python kohya_gui.py
# Acceder en http://localhost:7860
```

#### Paso 3: Entrenar Primer LoRA (30-60 minutos por tela)

**Parámetros LoRA SDXL recomendados:**
- Modelo base: `stabilityai/stable-diffusion-xl-base-1.0`
- Resolución: `1024`
- Learning rate: `1e-4`
- Batch size: `1`
- Epochs: `10-15`
- Network dim: `64`
- Network alpha: `32`
- Optimizer: `AdamW8bit`

**Ejemplo de caption** (`algodon-tech-negro-001_001.txt`):
```
algodon-tech-negro-001, tela de algodón técnico negro, textura de tejido fino, acabado mate, material profesional de traje
```

**Tiempo de entrenamiento**: ~20-30 minutos en 4090, ~40-60 minutos en L4

#### Paso 4: Integración con Generador (15 minutos)

1. Copiar LoRA entrenado a directorio de modelos:
```bash
mkdir -p /workspace/app/backend/models/lora
cp /workspace/kohya_ss/output/algodon-tech-negro-001.safetensors /workspace/app/backend/models/lora/
```

2. Actualizar `.env`:
```bash
USE_LORA=1
LORA_PATH=/workspace/app/backend/models/lora/algodon-tech-negro-001.safetensors
LORA_SCALE=0.8
```

3. Probar LoRA + baseline ControlNet:
```bash
export USE_LORA=1
export LORA_PATH=/workspace/app/backend/models/lora/algodon-tech-negro-001.safetensors
export LORA_SCALE=0.8

# Probar con baseline optimizado de Fase 1-2
python -m scripts.quick_gen --preset=production-baseline --seed=42 --cuts=recto --fabric=algodon-tech --color=negro-001

# Probar diferentes fuerzas de LoRA
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=0.6
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=0.8
python -m scripts.quick_gen --preset=production-baseline --seed=42 --override lora_scale=1.0
```

**Evaluación:**
- ✅ Textura de tela coincide con foto de catálogo
- ✅ Estructura de traje permanece perfecta (ControlNet mantenido)
- ✅ Calidad general permanece alta

**Escala LoRA óptima**: Usualmente 0.7-0.85 para texturas de tela

#### Paso 5: Entrenar 4 LoRAs Restantes

Repetir Pasos 1-4 para cada una de las 5 telas requeridas.

**Estimación de tiempo total**: ~3-5 horas para todos los 5 LoRAs (entrenamiento secuencial)

---

## 📊 Criterios de Éxito por Fase

### Éxito Fase 1:
- ✅ Cero deformación en estructura de traje
- ✅ Solapas nítidas, botones alineados, caída profesional
- ❌ Textura de tela es genérica (esperado en esta etapa)

### Éxito Fase 2:
- ✅ Máxima calidad dentro de presupuesto de 90s
- ✅ Fondos limpios, iluminación profesional
- ✅ Mantiene cero deformación de Fase 1
- ❌ Textura de tela aún genérica (esperado)

### Éxito Fase 3:
- ✅ Confirmado: baseline produce imágenes perfectas
- ✅ Confirmado: texturas de tela son genéricas
- ✅ Brecha identificada: necesitamos texturas específicas de tela

### Éxito Fase 4 (Objetivo Final):
- ✅ Textura de tela coincide precisamente con foto de catálogo
- ✅ Estructura de traje permanece perfecta (ControlNet mantenido)
- ✅ Calidad general permanece excelente
- ✅ **Santo Grial**: Estructura + Calidad + Textura Específica

---

## 🎓 Aprendizajes Clave del Testing de IP-Adapter

**Lo Que Aprendimos:**
1. Transferencia de estilo visual de IP-Adapter CONFLICTUA con control geométrico de ControlNet
2. Escala alta de IP-Adapter (0.8+) → estructura de traje deformada
3. Escala baja de IP-Adapter (0.3) → sin coincidencia precisa de textura
4. IP-Adapter no puede balancear estructura Y textura precisa

**Por Qué LoRA es Mejor:**
1. LoRA enseña conceptos, no transfiere estilos
2. LoRA funciona CON ControlNet, no contra él
3. LoRA es enfoque estándar para aprendizaje específico de objeto/textura
4. Probado en la industria para replicación de textura de tela/material

**Casos de Uso de IP-Adapter** (no el nuestro):
- Transferencia general de estilo (estilos artísticos)
- Pistas de textura de baja precisión
- Prototipado rápido sin entrenamiento

**Casos de Uso de LoRA** (nuestro caso de uso):
- Aprendizaje específico de objeto/concepto
- Replicación precisa de textura/patrón
- Trabajar junto con controles estructurales de ControlNet
- Coincidencia de textura de tela lista para producción

---

## 📁 Estructura de Archivos Actualizada

```
backend/scripts/
├── quick_gen.py                    # Script de testing rápido
├── quick_defaults.json             # Actualizado con presets ControlNet-primero
├── README.md                       # Actualizado con flujo ControlNet → LoRA
└── QUALITY_FIRST_PLAN.md          # Este documento

Presets Actualizados en quick_defaults.json:
- baseline                          # Punto inicial Fase 1
- controlnet-test-1,2,3            # Testing peso ControlNet Fase 1
- quality-baseline-80              # Punto inicial Fase 2
- quality-100, quality-120         # Testing techo calidad Fase 2
- [Presets IP-Adapter deprecados]  # Marcados como experimentales, no recomendados
```

---

## 🚀 Próximos Pasos Inmediatos

### 1. Iniciar Testing Fase 1 (20 minutos)

```bash
# SSH a RunPod
ssh root@<pod-ip> -p <pod-port> -i ~/.ssh/id_ed25519

# Activar entorno
source /workspace/py311/bin/activate
cd /workspace/app/backend

# Jalar últimos cambios
git pull origin main

# Iniciar Fase 1.1: Testing ControlNet Depth
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=0.8
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.0
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.2
python -m scripts.quick_gen --preset=baseline --seed=42 --cuts=recto --override depth_weight=1.5

# Descargar resultados a máquina local
# (Desde terminal NUEVA en Windows)
scp -i ~/.ssh/id_ed25519 -P <port> -r root@<pod-ip>:/workspace/app/backend/outputs/ ./phase1_depth_tests/
```

**Evaluar outputs visualmente:**
- ¿Qué peso depth tiene cero deformación?
- ¿Cuál produce estructura de traje más nítida?

### 2. Completar Fase 1 (40 minutos total)

Continuar con Fase 1.2 (testing Canny) y Fase 1.3 (verificación).

Documentar pesos ganadores de ControlNet en `quick_defaults.json` bajo nuevo preset:
```json
"production-baseline": {
  "description": "Baseline ControlNet optimizado - cero deformación",
  "controlnet_weight": <GANADOR>,
  "controlnet2_weight": <GANADOR>,
  ...
}
```

### 3. Testing Fase 2-3 (30 minutos)

Probar techo de calidad con pesos ganadores de ControlNet bloqueados.

### 4. Recolección de Datos para LoRA (1-2 horas)

Fotografiar/recolectar 15-20 imágenes de catálogo por tela mientras continúa el testing.

### 5. Configuración de Entrenamiento LoRA (30 minutos)

Instalar Kohya_ss en RunPod durante tiempo de inactividad.

### 6. Entrenar Primer LoRA (1 hora)

Iniciar con una tela para validar el enfoque.

---

## 📈 Cronología Esperada

| Fase | Duración | Entregable |
|-------|----------|-------------|
| **Fase 1** | 40 min | Pesos ControlNet para cero deformación |
| **Fase 2** | 30 min | Config calidad dentro de presupuesto 90s |
| **Fase 3** | 10 min | Validación baseline, brecha confirmada |
| **Fase 4 Setup** | 2 horas | Datos recolectados, Kohya_ss instalado |
| **Fase 4 Training** | 3-5 horas | 5 LoRAs entrenados y probados |
| **Total** | **7-9 horas** | Sistema listo para producción con 5 LoRAs de tela |

**Se puede paralelizar:**
- Recolección de datos durante testing Fase 1-3
- Múltiples sesiones de entrenamiento LoRA (secuencial en GPU única)

---

## ✅ Hacer Commit y Desplegar

Una vez Fase 1-3 estén completas:

```bash
# Hacer commit baseline optimizado a git
cd /workspace/app/backend
git add scripts/quick_defaults.json scripts/README.md scripts/QUALITY_FIRST_PLAN.md
git commit -m "feat: enfoque testing ControlNet-primero con roadmap LoRA

- Actualizado flujo de trabajo testing: ControlNet → Calidad → LoRA
- Deprecados presets IP-Adapter (pelea con ControlNet)
- Agregado plan integral entrenamiento LoRA
- Nuevos presets baseline para testing Fase 1-3"

git push origin main
```

---

## 📖 Documentación de Referencia

- **Flujo Testing**: `backend/scripts/README.md` (secciones: "Stack Tecnológico", "Flujo: Plan Testing Calidad-Primero", "Plan Integral Entrenamiento LoRA")
- **Configuraciones Preset**: `backend/scripts/quick_defaults.json`
- **Este Plan**: `backend/scripts/QUALITY_FIRST_PLAN.md`

---

## 💡 Pro Tips

1. **Usar Seeds Fijas**: Siempre usar `--seed=42` y `--seed=1234` para testing A/B
2. **Testing Corte Único**: Usar `--cuts=recto` durante Fase 1-2 para iteración 2x más rápida
3. **Comparación Visual**: Abrir outputs lado a lado al 100% zoom para verificar detalle de tela
4. **Documentar Todo**: Anotar parámetros ganadores en `quick_defaults.json` inmediatamente
5. **No Saltar Fases**: Cada fase se construye sobre la anterior - el orden es crítico

---

**¿Listo para iniciar Fase 1?** ¡Jala últimos cambios en RunPod y ejecuta el primer test depth ControlNet! 🚀
