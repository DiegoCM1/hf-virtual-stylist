# Guía de Configuración de Muestras de Tela

## Descripción General
Esta guía te ayuda a configurar imágenes de muestras de tela para mostrar en el selector de color en lugar de colores hex sólidos.

## Arquitectura

### Estructura del Bucket R2
```
ZEGNA 2025-26/
├── 095T-0121.png
├── 095T-0132.png
├── 095T-017B.png
├── 095T-B22D.png
└── ... (más imágenes de muestras)
```

### Campos de Base de Datos
Cada registro `Color` tiene:
- `color_id`: Identificador único (ej. "lc-navy-001")
- `name`: Nombre para mostrar (ej. "Azul Marino Imperial")
- `hex_value`: Color hex de respaldo (ej. "#0A1D3A")
- `swatch_code`: Nombre de archivo R2 sin extensión (ej. "095T-0121")
- `swatch_url`: URL computada (auto-generada desde swatch_code)

### Generación de URL
La API del catálogo construye automáticamente las URLs de muestras:
```
{R2_PUBLIC_URL}/ZEGNA%202025-26/{swatch_code}.png
```

Ejemplo:
```
https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/ZEGNA%202025-26/095T-0121.png
```

## Pasos de Configuración

### 1. Aplicar Migración de Base de Datos

Ejecutar la migración para agregar la columna `swatch_code`:

```bash
cd backend
alembic upgrade head
```

O en Railway:
```bash
python -m alembic upgrade head
```

### 2. Mapear IDs de Color a Códigos de Muestra

Editar `backend/swatch_mapping.py` y llenar el diccionario `SWATCH_MAPPING`:

```python
SWATCH_MAPPING = {
    "lc-navy-001": "095T-0121",     # Azul Marino Imperial
    "lc-charcoal-002": "095T-0132", # Gris Carbón
    "at-black-001": "095T-B22D",    # Negro Técnico
    # ... llenar el resto
}
```

**Cómo encontrar el mapeo correcto:**
1. Listar el contenido de tu bucket R2
2. Coincidir cada imagen de muestra con su color correspondiente en tu catálogo
3. Usar el nombre de archivo (sin extensión .png) como swatch_code

### 3. Ejecutar el Script de Mapeo

```bash
cd backend
python swatch_mapping.py
```

Esto poblará el campo `swatch_code` para todos los colores.

### 4. Desplegar en Railway

Hacer commit y push de cambios:

```bash
git add backend/
git commit -m "feat: agregar soporte de imágenes de muestras de tela"
git push origin main
```

Railway automáticamente:
1. Ejecutará migraciones (`alembic upgrade head`)
2. Reiniciará el backend
3. Servirá URLs de muestras desde R2

### 5. Verificar Visualización en Frontend

1. Abrir tu frontend: https://your-app.vercel.app
2. Navegar al selector de color
3. Deberías ver imágenes de muestras de tela en lugar de colores sólidos
4. Respaldo a colores hex si falta swatch_code

## Comportamiento del Frontend

El componente `CatalogSelector` maneja automáticamente:
- ✅ Muestra imagen de muestra si se proporciona `swatch_url`
- ✅ Respaldo a color hex si `swatch_url` es null
- ✅ Tamaño responsive (40px móvil → 64px desktop)
- ✅ Estados de hover y selección

¡No se requieren cambios en el frontend!

## Solución de Problemas

### ¿Las muestras no se muestran?

1. **Verificar configuración R2**
   ```bash
   # En backend/.env
   R2_PUBLIC_URL=https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev
   ```

2. **Verificar swatch_code en base de datos**
   ```sql
   SELECT color_id, name, swatch_code FROM colors;
   ```

3. **Probar URL R2 directamente**
   ```
   https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/harris-and-frank/ZEGNA%202025-26/{swatch_code}.png
   ```

4. **Verificar respuesta de API del catálogo**
   ```bash
   curl https://your-railway-app.railway.app/catalog | jq '.families[0].colors[0]'
   ```

   Debería incluir:
   ```json
   {
     "color_id": "lc-navy-001",
     "name": "Azul Marino Imperial",
     "hex": "#0A1D3A",
     "swatch_url": "https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/..."
   }
   ```

### ¿Las imágenes retornan 404?

- Verificar que la ruta del bucket R2 sea correcta
- Verificar que el nombre de archivo coincida exactamente (sensible a mayúsculas)
- Asegurar que el bucket R2 tenga acceso de lectura público

### ¿Espacios en nombres de archivo?

La API automáticamente codifica URLs con espacios:
- `ZEGNA 2025-26` se convierte en `ZEGNA%202025-26`
- Nombres de archivo con espacios como `095T 0121.png` se convierten en `095T%200121.png`

## Agregar Nuevas Muestras

1. Subir nueva imagen a R2: `harris-and-frank/ZEGNA 2025-26/{code}.png`
2. Actualizar base de datos:
   ```sql
   UPDATE colors SET swatch_code = '095T-XXXX' WHERE color_id = 'new-color-id';
   ```
3. O agregar a `swatch_mapping.py` y ejecutar el script nuevamente

## Alternativa: Asignación Manual de URL

Si prefieres establecer URLs completas directamente:

```sql
UPDATE colors
SET swatch_url = 'https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/custom/path/image.png'
WHERE color_id = 'lc-navy-001';
```

La API del catálogo prioriza:
1. `swatch_code` (construye URL automáticamente)
2. `swatch_url` (usa URL explícita)
3. `null` (frontend respaldo a color hex)
