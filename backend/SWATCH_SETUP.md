# Fabric Swatch Setup Guide

## Overview
This guide helps you configure fabric swatch images to display in the color selector instead of solid hex colors.

## Architecture

### R2 Bucket Structure
```
ZEGNA 2025-26/
├── 095T-0121.png
├── 095T-0132.png
├── 095T-017B.png
├── 095T-B22D.png
└── ... (more swatch images)
```

### Database Fields
Each `Color` record has:
- `color_id`: Unique identifier (e.g., "lc-navy-001")
- `name`: Display name (e.g., "Azul Marino Imperial")
- `hex_value`: Fallback hex color (e.g., "#0A1D3A")
- `swatch_code`: R2 filename without extension (e.g., "095T-0121")
- `swatch_url`: Computed URL (auto-generated from swatch_code)

### URL Generation
The catalog API automatically builds swatch URLs:
```
{R2_PUBLIC_URL}/ZEGNA%202025-26/{swatch_code}.png
```

Example:
```
https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/ZEGNA%202025-26/095T-0121.png
```

## Setup Steps

### 1. Apply Database Migration

Run the migration to add the `swatch_code` column:

```bash
cd backend
alembic upgrade head
```

Or on Railway:
```bash
python -m alembic upgrade head
```

### 2. Map Color IDs to Swatch Codes

Edit `backend/swatch_mapping.py` and fill in the `SWATCH_MAPPING` dictionary:

```python
SWATCH_MAPPING = {
    "lc-navy-001": "095T-0121",     # Azul Marino Imperial
    "lc-charcoal-002": "095T-0132", # Gris Carbón
    "at-black-001": "095T-B22D",    # Negro Técnico
    # ... fill in the rest
}
```

**How to find the correct mapping:**
1. List your R2 bucket contents
2. Match each swatch image to its corresponding color in your catalog
3. Use the filename (without .png extension) as the swatch_code

### 3. Run the Mapping Script

```bash
cd backend
python swatch_mapping.py
```

This will populate the `swatch_code` field for all colors.

### 4. Deploy to Railway

Commit and push changes:

```bash
git add backend/
git commit -m "feat: add fabric swatch image support"
git push origin main
```

Railway will automatically:
1. Run migrations (`alembic upgrade head`)
2. Restart the backend
3. Serve swatch URLs from R2

### 5. Verify Frontend Display

1. Open your frontend: https://your-app.vercel.app
2. Navigate to the color selector
3. You should see fabric swatch images instead of solid colors
4. Fallback to hex colors if swatch_code is missing

## Frontend Behavior

The `CatalogSelector` component automatically handles:
- ✅ Displays swatch image if `swatch_url` is provided
- ✅ Falls back to hex color if `swatch_url` is null
- ✅ Responsive sizing (40px mobile → 64px desktop)
- ✅ Hover and selection states

No frontend changes required!

## Troubleshooting

### Swatches not displaying?

1. **Check R2 configuration**
   ```bash
   # In backend/.env
   R2_PUBLIC_URL=https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev
   ```

2. **Verify swatch_code in database**
   ```sql
   SELECT color_id, name, swatch_code FROM colors;
   ```

3. **Test R2 URL directly**
   ```
   https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/harris-and-frank/ZEGNA%202025-26/{swatch_code}.png
   ```

4. **Check catalog API response**
   ```bash
   curl https://your-railway-app.railway.app/catalog | jq '.families[0].colors[0]'
   ```

   Should include:
   ```json
   {
     "color_id": "lc-navy-001",
     "name": "Azul Marino Imperial",
     "hex": "#0A1D3A",
     "swatch_url": "https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/..."
   }
   ```

### Images returning 404?

- Verify the R2 bucket path is correct
- Check filename matches exactly (case-sensitive)
- Ensure R2 bucket has public read access

### Spaces in filenames?

The API automatically URL-encodes spaces:
- `ZEGNA 2025-26` becomes `ZEGNA%202025-26`
- Filenames with spaces like `095T 0121.png` become `095T%200121.png`

## Adding New Swatches

1. Upload new image to R2: `harris-and-frank/ZEGNA 2025-26/{code}.png`
2. Update database:
   ```sql
   UPDATE colors SET swatch_code = '095T-XXXX' WHERE color_id = 'new-color-id';
   ```
3. Or add to `swatch_mapping.py` and run the script again

## Alternative: Manual URL Assignment

If you prefer to set full URLs directly:

```sql
UPDATE colors
SET swatch_url = 'https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/custom/path/image.png'
WHERE color_id = 'lc-navy-001';
```

The catalog API prioritizes:
1. `swatch_code` (builds URL automatically)
2. `swatch_url` (uses explicit URL)
3. `null` (frontend falls back to hex color)
