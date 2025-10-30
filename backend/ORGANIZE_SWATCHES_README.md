# Organizing Fabric Swatches by Color Family

This guide explains how to automatically categorize your 50-100 fabric swatches into color families using AI color analysis.

## Overview

The process consists of 3 steps:
1. **List** all swatch images from R2
2. **Analyze** dominant colors and categorize by color family
3. **Populate** database with organized families and colors

## Prerequisites

- R2 bucket with swatches in `ZEGNA 2025-26/` folder
- R2 credentials in `.env` file
- Python environment with dependencies installed

## Step 1: List All Swatches

This fetches all PNG files from your R2 bucket.

```bash
python list_r2_swatches.py
```

**Output:**
- Displays all swatch codes found
- Saves list to `swatch_codes_list.txt`
- Shows total count and file sizes

**Expected output:**
```
📦 Listing swatches from bucket: harris-and-frank
📁 Folder: ZEGNA 2025-26/

✅ Found 87 swatch images:

  1. 095T-0121      (  342.5 KB)
  2. 095T-0132      (  298.1 KB)
  3. 095T-017B      (  415.3 KB)
  ...
```

## Step 2: Analyze & Categorize by Color

This downloads each swatch, analyzes the dominant color, and categorizes into families using an AI-powered algorithm.

```bash
python organize_swatches_by_color.py
```

### Advanced Color Detection Algorithm (v2.0)

**Problem Solved:** Previous version classified 77/82 swatches as "Black/White" due to white borders and backgrounds in product photos.

**Solution:** Multi-stage color extraction with intelligent filtering:

1. **Center Cropping (70%)**
   - Crops to center 70% of image to avoid borders
   - Eliminates white backgrounds common in product photography
   ```python
   crop_margin = int(sample_size * 0.15)  # 15% margin on each side
   center_crop = image.crop((margin, margin, size-margin, size-margin))
   ```

2. **Brightness Filtering**
   - Filters out pixels with extreme brightness (borders, flash reflections)
   - Range: 20-235 (out of 255)
   - Skips pure white borders and pure black shadows
   ```python
   if 20 < brightness < 235:  # Keep only mid-range pixels
       filtered_pixels.append((r, g, b))
   ```

3. **Top-N Color Sampling**
   - Analyzes top 10 most frequent colors (increased from 5)
   - Better statistical representation of fabric texture

4. **Saturation-Weighted Averaging**
   - Gives more weight to saturated (colorful) pixels
   - Reduces influence of neutral backgrounds
   ```python
   weight = count * (1 + saturation * 2)
   ```

5. **HSV Color Space Analysis**
   - Converts to Hue-Saturation-Value for accurate categorization
   - Hue: Color type (red, blue, green, etc.)
   - Saturation: Color intensity vs grayness
   - Value: Brightness (dark to light)

6. **Strict Categorization Thresholds**
   - **Black:** V < 0.10 (only very dark)
   - **White:** V > 0.90 AND S < 0.05 (very light + unsaturated)
   - **Gray:** S < 0.12 (low saturation, strict threshold)
   - **Colors:** HSV range matching per family

### Color Families & HSV Ranges

| Family | HSV Range | Conditions |
|--------|-----------|------------|
| **Azules** (Blues) | H: 190-250° | S > 0.2, V > 0.2 |
| **Grises** (Grays) | Any H | S < 0.12, 0.25 < V < 0.75 |
| **Marrones y Beiges** | H: 20-45° | S > 0.15, V > 0.15 |
| **Negros y Blancos** | Any H | V < 0.10 OR (V > 0.90 AND S < 0.05) |
| **Verdes** (Greens) | H: 80-170° | S > 0.2, V > 0.2 |
| **Tonos Cálidos** (Warm) | H: 0-20° | S > 0.3, V > 0.2 |
| **Tonos Fríos** (Cool) | H: 250-290° | S > 0.2, V > 0.2 |

### Spanish Color Name Generation

Names are generated based on Value (brightness):
- **Oscuro** (Dark): V < 0.3
- **Base name**: 0.3 < V < 0.7
- **Claro** (Light): V > 0.7

Examples:
- "Azul Oscuro" (Dark Blue)
- "Azul" (Blue)
- "Azul Claro" (Light Blue)
- "Gris 52" (Gray with 52% brightness)

**Output:**
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

Creates `swatch_categorization.json` with full results.

## Step 3: Preview Organization (Optional)

Before making database changes, preview the organization:

```bash
python populate_color_families.py --preview
```

**Output:**
```
📋 Preview of Organization:

Azules                    18 swatches
Grises                    25 swatches
Marrones y Beiges         22 swatches
...
Total: 87 swatches
```

## Step 4: Populate Database

This creates the fabric families and colors in your database.

```bash
python populate_color_families.py
```

**Prompts for confirmation:**
```
⚠️  This will REPLACE all existing fabric families and colors!
   Continue? (yes/no):
```

Type `yes` to proceed.

**What it does:**
- Clears existing fabric families and colors (test data)
- Creates new families organized by color
- Assigns each swatch to appropriate family
- Sets `swatch_code` for each color (enables automatic URL generation)
- Generates unique `color_id` for each swatch

**Output:**
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

## Step 5: Test Frontend

Once populated, restart your backend and test the frontend:

1. **Restart Railway backend** (or local backend)
2. **Open frontend** in browser
3. **Check color selector** - should show 7 color family categories
4. **Verify swatches** - should display actual fabric images

## Customization

### Adjust Color Categorization

Edit `organize_swatches_by_color.py` if you want to tweak the color ranges:

```python
COLOR_FAMILIES = {
    "azules": {
        "hue_range": (190, 250),  # Adjust blue hue range
        "saturation_min": 0.2,     # Minimum color intensity
    },
    # ...
}
```

### Change Color Names

Edit the color name generation logic in `categorize_color()`:

```python
if v < 0.3:
    return family_id, f"{base_name} Oscuro"  # Dark
elif v > 0.7:
    return family_id, f"{base_name} Claro"   # Light
else:
    return family_id, base_name              # Regular
```

### Modify Family Names

Edit `populate_color_families.py`:

```python
FAMILY_DISPLAY_NAMES = {
    "azules": "Azules",           # Change to "Blues" or "Tonos Azules"
    "grises": "Grises",           # Change to "Grays" or "Neutros"
    # ...
}
```

## Troubleshooting

### Script fails with "Python not found"

Run scripts using the full Python path or activate your virtual environment first.

### R2 connection errors

Check your `.env` file has correct R2 credentials:
```env
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=harris-and-frank
R2_PUBLIC_URL=https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev
```

### Wrong color categorization

Some edge cases might be miscategorized. You can manually fix them:

1. Edit `swatch_categorization.json`
2. Move swatches between families
3. Re-run `populate_color_families.py`

Or update the database directly:

```sql
UPDATE colors
SET fabric_family_id = (SELECT id FROM fabric_families WHERE family_id = 'grises')
WHERE swatch_code = '095T-0121';
```

### Colors not displaying in frontend

1. Check catalog API response includes `swatch_url`
2. Verify R2 URLs are correct
3. Ensure `swatch_code` is populated in database

## File Reference

- `list_r2_swatches.py` - Lists all swatches from R2
- `organize_swatches_by_color.py` - Analyzes and categorizes swatches
- `populate_color_families.py` - Populates database
- `swatch_codes_list.txt` - Generated list of all codes
- `swatch_categorization.json` - Generated categorization results

## Next Steps

After successful population:

1. ✅ Database has 7 color families with ~87 swatches
2. ✅ Each color has `swatch_code` set
3. ✅ Catalog API returns correct `swatch_url` for each color
4. ✅ Frontend displays organized families with swatch images

You can now:
- Add more swatches (just re-run the process)
- Fine-tune categorization
- Customize family names
- Add additional metadata (fabric composition, price, etc.)
