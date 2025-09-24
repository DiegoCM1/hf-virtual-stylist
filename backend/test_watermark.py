from pathlib import Path
from app.services.watermark import apply_watermark_image

input_path = Path("test_input.jpg")
output_path = Path("test_output.jpg")

with open(input_path, "rb") as f:
    image_bytes = f.read()

watermarked = apply_watermark_image(image_bytes, "logo-transparent.webp")

with open(output_path, "wb") as f:
    f.write(watermarked)

print(f"✅ Watermarked image with PNG logo saved to {output_path}")
