# Scripts de Generación Rápida para Testing Rápido de SDXL

Este directorio contiene herramientas para **iteración rápida** en parámetros de generación SDXL sin la sobrecarga del stack completo API/DB.

## Comparación de Velocidad

| Flujo de Trabajo | Tiempo por Test | Notas |
|----------|---------------|-------|
| **Stack Completo** (Frontend → Railway → RunPod) | ~25-30s | Incluye API, DB, delays de polling |
| **Solo API** (curl → worker.py) | ~20-25s | Delay de polling 5s + generación |
| **quick_gen.py** | **~2-3s** | Generación directa, modelos permanecen en RAM ⚡ |

**¡Iteración ~8-10x más rápida** para testing de parámetros!

---

## Archivos

- **`quick_defaults.json`** - Configuraciones preset (versionado controlado)
- **`quick_gen.py`** - Script de generación standalone
- **`README.md`** - Este archivo

---

## Inicio Rápido en RunPod

### 1. SSH al Pod GPU de RunPod

```bash
ssh root@<pod-ip> -p <pod-port> -i ~/.ssh/id_ed25519
```

### 2. Activar Entorno

```bash
source /workspace/py311/bin/activate
cd /workspace/app/backend
```

### 3. Listar Presets Disponibles

```bash
python -m scripts.quick_gen --list-presets
```

Salida:
```
[Available Presets]

  baseline             - Config de producción actual - ControlNet dual con refiner
  fast-no-refiner      - Saltar refiner por velocidad - probar si calidad es aceptable
  aggressive-depth     - ControlNet depth pesado para guía de pose más fuerte
  aggressive-canny     - ControlNet canny pesado para bordes de solapa/botón más nítidos
  balanced-60          - Config balanceado con pasos reducidos por velocidad
  ultra-fast           - Pasos mínimos para testing rápido - puede sufrir calidad
  ...
```

### 4. Ejecutar un Test Simple

```bash
python -m scripts.quick_gen \
  --preset=aggressive-depth \
  --fabric=algodon-tech \
  --color=negro-001
```

**Primera ejecución**: ~8-10s (carga modelos SDXL en VRAM)
**Ejecuciones subsecuentes**: ~2-3s (modelos en caché)

### 5. Comparar Múltiples Presets

```bash
python -m scripts.quick_gen \
  --compare baseline,aggressive-depth,ultra-fast \
  --fabric=algodon-tech \
  --color=negro-001
```

Genera imágenes para los 3 presets en menos de 10 segundos total.

### 6. Sobrescribir Parámetros Específicos

```bash
python -m scripts.quick_gen \
  --preset=baseline \
  --override guidance=6.0,steps=100 \
  --fabric=algodon-tech
```

### 7. Probar un Solo Corte

```bash
python -m scripts.quick_gen \
  --preset=ultra-fast \
  --cuts=recto \
  --fabric=algodon-tech
```

---

## Flujo de Trabajo: Encontrar Parámetros Óptimos

### Fase 1: Testing Baseline (15 minutos)

Probar config de producción actual vs variantes optimizadas para velocidad:

```bash
# Probar baseline vs no-refiner
python -m scripts.quick_gen --compare baseline,fast-no-refiner

# Probar conteos de pasos
python -m scripts.quick_gen --compare balanced-60,baseline,quality-100

# Probar ControlNets únicos
python -m scripts.quick_gen --compare depth-only,canny-only,baseline
```

**Objetivo**: Determinar si el refiner vale el tiempo, conteo óptimo de pasos, impacto de ControlNet.

### Fase 2: Afinación de Peso de ControlNet (10 minutos)

```bash
# Probar pesos de depth
python -m scripts.quick_gen --preset=baseline --override depth_weight=0.7
python -m scripts.quick_gen --preset=baseline --override depth_weight=1.0
python -m scripts.quick_gen --preset=baseline --override depth_weight=1.3

# Probar pesos de canny
python -m scripts.quick_gen --preset=baseline --override canny_weight=0.5
python -m scripts.quick_gen --preset=baseline --override canny_weight=0.8
python -m scripts.quick_gen --preset=baseline --override canny_weight=1.0
```

**Objetivo**: Encontrar punto óptimo para guía de pose vs flexibilidad de tela.

### Fase 3: Testing de Escala de Guidance (5 minutos)

```bash
python -m scripts.quick_gen --compare low-cfg,baseline,high-cfg
```

**Objetivo**: Balancear adherencia al prompt vs libertad creativa.

### Fase 4: Documentar Hallazgos (5 minutos)

Editar `quick_defaults.json` para agregar configs ganadoras:

```json
{
  "production-v2": {
    "description": "Config optimizado después de testing - más rápido, mejor calidad",
    "guidance": 5.5,
    "total_steps": 60,
    "use_refiner": false,
    "controlnet_weight": 1.1,
    "controlnet2_weight": 0.7,
    ...
  }
}
```

Hacer commit a git para compartir con equipo.

---

## Agregar Nuevos Presets

Editar `scripts/quick_defaults.json`:

```json
{
  "my-custom-preset": {
    "description": "Breve descripción de qué prueba esto",
    "guidance": 4.5,
    "total_steps": 60,
    "use_refiner": true,
    "refiner_split": 0.7,
    "controlnet_enabled": true,
    "controlnet_weight": 0.9,
    "controlnet_guidance_start": 0.0,
    "controlnet_guidance_end": 0.5,
    "controlnet2_enabled": true,
    "controlnet2_weight": 0.65,
    "controlnet2_guidance_start": 0.05,
    "controlnet2_guidance_end": 0.88,
    "ip_adapter_enabled": false
  }
}
```

Luego probar inmediatamente:

```bash
python -m scripts.quick_gen --preset=my-custom-preset
```

---

## Referencia de Parámetros

### Claves de Sobrescritura Disponibles

| Nombre Corto | Clave de Config Completa | Tipo | Descripción |
|------------|-----------------|------|-------------|
| `guidance` | `guidance` | float | Escala CFG (2.0-8.0 típico) |
| `steps` | `total_steps` | int | Pasos de inferencia (40-100) |
| `refiner` | `use_refiner` | bool | Habilitar refiner SDXL |
| `refiner_split` | `refiner_split` | float | Transición Base→Refiner (0.0-1.0) |
| `depth_weight` | `controlnet_weight` | float | Fuerza de ControlNet Depth |
| `canny_weight` | `controlnet2_weight` | float | Fuerza de ControlNet Canny |
| `ip_adapter` | `ip_adapter_enabled` | bool | Habilitar IP-Adapter |
| `ip_scale` | `ip_adapter_scale` | float | Fuerza de blend de IP-Adapter |

### Ejemplos de Combinaciones de Sobrescritura

```bash
# Más rápido, guía depth más ligera
--override steps=50,depth_weight=0.8,refiner=false

# Calidad máxima
--override steps=120,guidance=5.0,refiner=true,refiner_split=0.8

# Probar sin ningún ControlNet
--override controlnet_enabled=false,controlnet2_enabled=false
```

---

## Ubicación de Salida

Imágenes guardadas en: `backend/outputs/`

Patrón de nombre de archivo: `{fabric_id}_{color_id}_{cut}_{timestamp}.png`

---

## Solución de Problemas

### "ModuleNotFoundError: No module named 'app'"

**Fix**: Ejecutar desde directorio `backend/`:
```bash
cd /workspace/app/backend
python -m scripts.quick_gen ...
```

### "CUDA out of memory"

**Fix**: Modelos demasiado grandes para GPU. Verificar:
```bash
nvidia-smi  # Debería mostrar <20GB uso de VRAM con L4
```

Si aún hay OOM, probar preset `ultra-fast` (ControlNet único, sin refiner).

### "Control image not found"

**Fix**: Verificar que existen imágenes de ControlNet:
```bash
ls -la /workspace/app/backend/assets/control/
```

Debería contener:
- `recto_depth.png`
- `cruzado_depth.png`
- `recto_canny.png`
- `cruzado_canny.png`

### Modelos descargando lentamente

**Fix**: Primera ejecución descarga ~12GB de modelos desde HuggingFace. Ejecuciones subsecuentes usan caché en `/workspace/.cache/huggingface`.

---

## Próximos Pasos Después de Testing

Una vez encontrados los parámetros óptimos:

1. **Actualizar `quick_defaults.json`** con preset ganador
2. **Portar a producción**: Actualizar `app/services/generator.py` o variables de entorno
3. **Actualizar `devops/runpod/deploy.sh`** con nuevos defaults
4. **Probar end-to-end**: Frontend → Railway → RunPod con nueva config
5. **Desplegar a producción**

---

## Tips

- **Mantener modelos cargados**: No reiniciar Python entre tests (penalización de recarga 10s)
- **Probar sistemáticamente**: Cambiar un parámetro a la vez
- **Documentar hallazgos**: Actualizar descripciones de presets con notas
- **Versionado**: Hacer commit de presets ganadores a git
- **Comparar visualmente**: Abrir `outputs/` en visor de imágenes lado a lado
- **Usar seed fija**: Agregar `--seed=42` para tests reproducibles

---

## Sesión de Ejemplo

```bash
# Iniciar RunPod, SSH
ssh root@<pod> -p <port>
source /workspace/py311/bin/activate
cd /workspace/app/backend

# Listar presets
python -m scripts.quick_gen --list-presets

# Probar baseline (primera ejecución, carga modelos ~10s)
python -m scripts.quick_gen --preset=baseline

# Comparar 3 presets (~6s total, modelos ya cargados)
python -m scripts.quick_gen --compare baseline,fast-no-refiner,ultra-fast

# Ajustar ganador
python -m scripts.quick_gen --preset=fast-no-refiner --override guidance=5.5,steps=70

# Probar con tela diferente
python -m scripts.quick_gen --preset=fast-no-refiner --fabric=lana-super-150 --color=azul-marino

# Ver outputs
ls -lh outputs/
# Copiar mejor preset a quick_defaults.json como "production-v2"
```

**Tiempo total**: ~2 minutos para 6+ iteraciones de test 🚀
