# Organización de Muestras de Tela por Familia de Color

Esta guía explica cómo categorizar automáticamente tus 50-100 muestras de tela en familias de color usando análisis de color basado en IA.

## Descripción General

El proceso consiste en 3 pasos:
1. **Listar** todas las imágenes de muestras desde R2
2. **Analizar** colores dominantes y categorizar por familia de color
3. **Poblar** base de datos con familias y colores organizados

## Requisitos Previos

- Bucket R2 con muestras en carpeta `ZEGNA 2025-26/`
- Credenciales R2 en archivo `.env`
- Entorno Python con dependencias instaladas

## Paso 1: Listar Todas las Muestras

Esto obtiene todos los archivos PNG de tu bucket R2.

```bash
python list_r2_swatches.py
```

**Salida:**
- Muestra todos los códigos de muestra encontrados
- Guarda lista en `swatch_codes_list.txt`
- Muestra conteo total y tamaños de archivo

**Salida esperada:**
```
📦 Listing swatches from bucket: harris-and-frank
📁 Folder: ZEGNA 2025-26/

✅ Found 87 swatch images:

  1. 095T-0121      (  342.5 KB)
  2. 095T-0132      (  298.1 KB)
  3. 095T-017B      (  415.3 KB)
  ...
```

## Paso 2: Analizar y Categorizar por Color

Esto descarga cada muestra, analiza el color dominante y categoriza en familias usando un algoritmo potenciado por IA.

```bash
python organize_swatches_by_color.py
```

### Algoritmo Avanzado de Detección de Color (v2.0)

**Problema Resuelto:** La versión anterior clasificaba 77/82 muestras como "Blanco/Negro" debido a bordes blancos y fondos en fotos de producto.

**Solución:** Extracción de color multi-etapa con filtrado inteligente:

1. **Recorte Central (70%)**
   - Recorta al centro 70% de la imagen para evitar bordes
   - Elimina fondos blancos comunes en fotografía de producto
   ```python
   crop_margin = int(sample_size * 0.15)  # 15% margen en cada lado
   center_crop = image.crop((margin, margin, size-margin, size-margin))
   ```

2. **Filtrado de Brillo**
   - Filtra píxeles con brillo extremo (bordes, reflejos de flash)
   - Rango: 20-235 (de 255)
   - Omite bordes blancos puros y sombras negras puras
   ```python
   if 20 < brightness < 235:  # Mantener solo píxeles de rango medio
       filtered_pixels.append((r, g, b))
   ```

3. **Muestreo de Top-N Colores**
   - Analiza los 10 colores más frecuentes (incrementado desde 5)
   - Mejor representación estadística de textura de tela

4. **Promediado Ponderado por Saturación**
   - Da más peso a píxeles saturados (coloridos)
   - Reduce influencia de fondos neutrales
   ```python
   weight = count * (1 + saturation * 2)
   ```

5. **Análisis del Espacio de Color HSV**
   - Convierte a Matiz-Saturación-Valor para categorización precisa
   - Matiz: Tipo de color (rojo, azul, verde, etc.)
   - Saturación: Intensidad del color vs grisáceo
   - Valor: Brillo (oscuro a claro)

6. **Umbrales de Categorización Estrictos**
   - **Negro:** V < 0.10 (solo muy oscuro)
   - **Blanco:** V > 0.90 Y S < 0.05 (muy claro + desaturado)
   - **Gris:** S < 0.12 (baja saturación, umbral estricto)
   - **Colores:** Coincidencia de rango HSV por familia

### Familias de Color y Rangos HSV

| Familia | Rango HSV | Condiciones |
|--------|-----------|------------|
| **Azules** (Blues) | H: 190-250° | S > 0.2, V > 0.2 |
| **Grises** (Grays) | Cualquier H | S < 0.12, 0.25 < V < 0.75 |
| **Marrones y Beiges** | H: 20-45° | S > 0.15, V > 0.15 |
| **Negros y Blancos** | Cualquier H | V < 0.10 O (V > 0.90 Y S < 0.05) |
| **Verdes** (Greens) | H: 80-170° | S > 0.2, V > 0.2 |
| **Tonos Cálidos** (Warm) | H: 0-20° | S > 0.3, V > 0.2 |
| **Tonos Fríos** (Cool) | H: 250-290° | S > 0.2, V > 0.2 |

### Generación de Nombres de Color en Español

Los nombres se generan basados en el Valor (brillo):
- **Oscuro** (Dark): V < 0.3
- **Nombre base**: 0.3 < V < 0.7
- **Claro** (Light): V > 0.7

Ejemplos:
- "Azul Oscuro" (Dark Blue)
- "Azul" (Blue)
- "Azul Claro" (Light Blue)
- "Gris 52" (Gray con 52% brillo)

**Salida:**
```
🔍 Analyzing 87 swatches...
  1. 095T-0121      → azules          Azul Oscuro          #0A1D3A
  2. 095T-0132      → grises          Gris 52              #343434
  3. 095T-017B      → marrones        Marrón               #C19A6B
  ...

📊 Summary by Color Family:
Azules                    18 swatches
Grises                    25 swatches
Marrones y Beiges         22 swatches
Negros y Blancos          12 swatches
Verdes                     6 swatches
Tonos Cálidos              3 swatches
Tonos Fríos                1 swatches
```

Crea `swatch_categorization.json` con resultados completos.

## Paso 3: Previsualizar Organización (Opcional)

Antes de hacer cambios en la base de datos, previsualizar la organización:

```bash
python populate_color_families.py --preview
```

**Salida:**
```
📋 Preview of Organization:

Azules                    18 swatches
Grises                    25 swatches
Marrones y Beiges         22 swatches
...
Total: 87 swatches
```

## Paso 4: Poblar Base de Datos

Esto crea las familias de telas y colores en tu base de datos.

```bash
python populate_color_families.py
```

**Solicita confirmación:**
```
⚠️  This will REPLACE all existing fabric families and colors!
   Continue? (yes/no):
```

Escribir `yes` para proceder.

**Lo que hace:**
- Limpia familias y colores de telas existentes (datos de prueba)
- Crea nuevas familias organizadas por color
- Asigna cada muestra a la familia apropiada
- Establece `swatch_code` para cada color (habilita generación automática de URL)
- Genera `color_id` único para cada muestra

**Salida:**
```
🗑️  Clearing existing fabric families and colors...
✨ Creating new fabric families and colors...

📁 Azules (18 colors)
   └─ 095T-0121             Azul Oscuro               #0A1D3A
   └─ 095T-B22D             Azul Claro                #AEC6CF
   ...

📁 Grises (25 colors)
   └─ 095T-0132             Gris 52                   #343434
   ...

✅ Successfully created:
   Fabric families: 7
   Colors: 87
```

## Paso 5: Probar Frontend

Una vez poblado, reiniciar tu backend y probar el frontend:

1. **Reiniciar backend de Railway** (o backend local)
2. **Abrir frontend** en navegador
3. **Verificar selector de color** - debería mostrar 7 categorías de familias de color
4. **Verificar muestras** - debería mostrar imágenes de tela reales

## Personalización

### Ajustar Categorización de Color

Editar `organize_swatches_by_color.py` si deseas ajustar los rangos de color:

```python
COLOR_FAMILIES = {
    "azules": {
        "hue_range": (190, 250),  # Ajustar rango de matiz azul
        "saturation_min": 0.2,     # Intensidad mínima de color
    },
    # ...
}
```

### Cambiar Nombres de Color

Editar la lógica de generación de nombres de color en `categorize_color()`:

```python
if v < 0.3:
    return family_id, f"{base_name} Oscuro"  # Oscuro
elif v > 0.7:
    return family_id, f"{base_name} Claro"   # Claro
else:
    return family_id, base_name              # Regular
```

### Modificar Nombres de Familia

Editar `populate_color_families.py`:

```python
FAMILY_DISPLAY_NAMES = {
    "azules": "Azules",           # Cambiar a "Blues" o "Tonos Azules"
    "grises": "Grises",           # Cambiar a "Grays" o "Neutros"
    # ...
}
```

## Solución de Problemas

### El script falla con "Python not found"

Ejecutar scripts usando la ruta completa de Python o activar tu entorno virtual primero.

### Errores de conexión R2

Verificar que tu archivo `.env` tiene las credenciales R2 correctas:
```env
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=harris-and-frank
R2_PUBLIC_URL=https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev
```

### Categorización de color incorrecta

Algunos casos límite podrían estar mal categorizados. Puedes corregirlos manualmente:

1. Editar `swatch_categorization.json`
2. Mover muestras entre familias
3. Re-ejecutar `populate_color_families.py`

O actualizar la base de datos directamente:

```sql
UPDATE colors
SET fabric_family_id = (SELECT id FROM fabric_families WHERE family_id = 'grises')
WHERE swatch_code = '095T-0121';
```

### Los colores no se muestran en frontend

1. Verificar que la respuesta de la API del catálogo incluya `swatch_url`
2. Verificar que las URLs de R2 sean correctas
3. Asegurar que `swatch_code` esté poblado en la base de datos

## Referencia de Archivos

- `list_r2_swatches.py` - Lista todas las muestras desde R2
- `organize_swatches_by_color.py` - Analiza y categoriza muestras
- `populate_color_families.py` - Puebla base de datos
- `swatch_codes_list.txt` - Lista generada de todos los códigos
- `swatch_categorization.json` - Resultados de categorización generados

## Próximos Pasos

Después de una población exitosa:

1. ✅ Base de datos tiene 7 familias de color con ~87 muestras
2. ✅ Cada color tiene `swatch_code` establecido
3. ✅ API del catálogo retorna `swatch_url` correcta para cada color
4. ✅ Frontend muestra familias organizadas con imágenes de muestras

Ahora puedes:
- Agregar más muestras (solo re-ejecutar el proceso)
- Afinar la categorización
- Personalizar nombres de familias
- Agregar metadata adicional (composición de tela, precio, etc.)
