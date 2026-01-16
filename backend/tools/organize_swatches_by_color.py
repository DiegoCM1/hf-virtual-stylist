"""
Analyze swatch images and organize them by color family.

This script:
1. Downloads swatches from R2
2. Analyzes dominant colors using PIL
3. Categorizes into color families (Blues, Grays, Browns, etc.)
4. Generates Spanish color names
5. Creates database-ready output
"""

import io
import boto3
import colorsys
from PIL import Image
from collections import Counter
from app.core.config import settings

# Color family definitions with HSV ranges
COLOR_FAMILIES = {
    "azules": {
        "display_name": "Azules",
        "hue_range": (190, 250),  # Blue hues
        "saturation_min": 0.2,
        "value_min": 0.2,
    },
    "grises": {
        "display_name": "Grises",
        "hue_range": (0, 360),  # Any hue
        "saturation_max": 0.15,  # Low saturation
        "value_min": 0.15,
    },
    "marrones": {
        "display_name": "Marrones y Beiges",
        "hue_range": (20, 45),  # Orange-brown hues
        "saturation_min": 0.15,
        "value_min": 0.15,
    },
    "neutros": {
        "display_name": "Negros y Blancos",
        "hue_range": (0, 360),
        "value_check": "extreme",  # Very dark or very light
    },
    "verdes": {
        "display_name": "Verdes",
        "hue_range": (80, 170),  # Green hues
        "saturation_min": 0.2,
        "value_min": 0.2,
    },
    "tonos-calidos": {
        "display_name": "Tonos Cálidos",
        "hue_range": (0, 20),  # Red-orange
        "saturation_min": 0.3,
        "value_min": 0.2,
    },
    "tonos-frios": {
        "display_name": "Tonos Fríos",
        "hue_range": (250, 290),  # Purple-blue
        "saturation_min": 0.2,
        "value_min": 0.2,
    },
}


def download_swatch_from_r2(key):
    """Download a single swatch image from R2."""
    s3_client = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

    response = s3_client.get_object(Bucket=settings.r2_bucket_name, Key=key)
    image_data = response['Body'].read()
    return Image.open(io.BytesIO(image_data))


def get_dominant_color(image, sample_size=150):
    """Extract dominant color from image using center-weighted sampling."""
    # Resize for faster processing
    image = image.resize((sample_size, sample_size))
    image = image.convert("RGB")

    # Crop to center 70% to avoid borders/backgrounds
    crop_margin = int(sample_size * 0.15)
    center_crop = image.crop((
        crop_margin,
        crop_margin,
        sample_size - crop_margin,
        sample_size - crop_margin
    ))

    # Get all colors and count frequency
    pixels = list(center_crop.getdata())

    # Filter out extreme values (pure white/black borders)
    filtered_pixels = []
    for r, g, b in pixels:
        # Skip pixels that are too white or too black (likely borders)
        brightness = (r + g + b) / 3
        if 20 < brightness < 235:  # Exclude extreme values
            filtered_pixels.append((r, g, b))

    # If we filtered out too much, use original
    if len(filtered_pixels) < len(pixels) * 0.3:
        filtered_pixels = pixels

    color_counter = Counter(filtered_pixels)

    # Get top 10 most common colors (more samples for better accuracy)
    top_colors = color_counter.most_common(10)

    # Calculate weighted average, giving more weight to saturated colors
    total_weight = 0
    weighted_r = 0
    weighted_g = 0
    weighted_b = 0

    for (r, g, b), count in top_colors:
        # Calculate saturation
        max_rgb = max(r, g, b)
        min_rgb = min(r, g, b)
        saturation = (max_rgb - min_rgb) / max_rgb if max_rgb > 0 else 0

        # Weight by both count and saturation (prefer more colorful pixels)
        weight = count * (1 + saturation * 2)
        total_weight += weight
        weighted_r += r * weight
        weighted_g += g * weight
        weighted_b += b * weight

    if total_weight > 0:
        avg_r = int(weighted_r / total_weight)
        avg_g = int(weighted_g / total_weight)
        avg_b = int(weighted_b / total_weight)
    else:
        # Fallback
        avg_r = sum(r for (r, g, b), _ in top_colors) // len(top_colors)
        avg_g = sum(g for (r, g, b), _ in top_colors) // len(top_colors)
        avg_b = sum(b for (r, g, b), _ in top_colors) // len(top_colors)

    return (avg_r, avg_g, avg_b)


def rgb_to_hsv(r, g, b):
    """Convert RGB to HSV."""
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return (h * 360, s, v)  # H in degrees, S and V in 0-1


def categorize_color(rgb):
    """Categorize an RGB color into a color family."""
    r, g, b = rgb
    h, s, v = rgb_to_hsv(r, g, b)

    # Check for true black/white (very strict thresholds)
    if v < 0.10:  # Very dark
        return "neutros", "Negro"
    if v > 0.90 and s < 0.05:  # Very light and unsaturated
        return "neutros", "Blanco"

    # Check for browns FIRST (before grays) to avoid misclassification
    # Browns have low-medium saturation but are in the brown hue range
    if 20 <= h <= 45 and 0.08 <= s < 0.25 and v > 0.15:
        return "marrones", "Marrón"

    # Check grays (low saturation, but exclude brown hue range)
    if s < 0.10:  # Very strict threshold for true grays
        if v < 0.25:
            return "neutros", "Negro Carbón"
        elif v > 0.75:
            return "grises", "Gris Claro"
        else:
            return "grises", f"Gris {int(v * 100)}"

    # Check color families by hue
    for family_id, family_def in COLOR_FAMILIES.items():
        if family_id in ["neutros", "grises"]:
            continue  # Already handled

        hue_min, hue_max = family_def["hue_range"]
        sat_min = family_def.get("saturation_min", 0)

        # Handle hue wraparound (e.g., reds that cross 0°)
        if hue_min > hue_max:
            in_range = (h >= hue_min or h <= hue_max)
        else:
            in_range = (hue_min <= h <= hue_max)

        if in_range and s >= sat_min:
            # Generate color name based on value (lightness)
            base_name = family_def["display_name"].split()[0].rstrip('s')  # "Azul", "Verde"
            if v < 0.3:
                return family_id, f"{base_name} Oscuro"
            elif v > 0.7:
                return family_id, f"{base_name} Claro"
            else:
                return family_id, base_name

    # Default fallback
    if s > 0.3:
        return "tonos-calidos", "Tono Mixto"
    return "grises", "Gris Neutro"


def rgb_to_hex(r, g, b):
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def analyze_all_swatches():
    """Main function to analyze all swatches and categorize them."""
    from list_r2_swatches import list_r2_swatches

    print("🎨 Analyzing swatches from R2...\n")

    # Get list of all swatches
    swatches = list_r2_swatches()

    if not swatches:
        print("❌ No swatches found!")
        return

    # Organize by color family
    organized = {family_id: [] for family_id in COLOR_FAMILIES.keys()}
    results = []

    print(f"\n🔍 Analyzing {len(swatches)} swatches...")
    print("=" * 80)

    for i, swatch in enumerate(swatches, 1):
        try:
            # Download and analyze
            image = download_swatch_from_r2(swatch['key'])
            dominant_rgb = get_dominant_color(image)
            family_id, color_name = categorize_color(dominant_rgb)
            hex_color = rgb_to_hex(*dominant_rgb)

            result = {
                'swatch_code': swatch['code'],
                'family_id': family_id,
                'color_name': color_name,
                'hex': hex_color,
                'rgb': dominant_rgb,
            }
            organized[family_id].append(result)
            results.append(result)

            print(f"{i:3d}. {swatch['code']:<20} → {family_id:<15} {color_name:<20} {hex_color}")

        except Exception as e:
            print(f"❌ Error processing {swatch['code']}: {e}")

    print("=" * 80)

    # Print summary by family
    print("\n📊 Summary by Color Family:")
    print("=" * 80)
    for family_id, items in organized.items():
        if items:
            print(f"{COLOR_FAMILIES[family_id]['display_name']:<25} {len(items):>3} swatches")
    print("=" * 80)

    # Save results to JSON
    import json
    output_file = "swatch_categorization.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'organized_by_family': organized,
            'all_results': results,
            'summary': {family_id: len(items) for family_id, items in organized.items() if items}
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_file}")

    return organized, results


if __name__ == "__main__":
    print("🌈 Swatch Color Analyzer & Organizer\n")
    organized, results = analyze_all_swatches()
    print("\n✨ Done!")
