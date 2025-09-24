from pathlib import Path

from app.services.watermark import apply_watermark_image


ASSETS_DIR = Path(__file__).parent / "assets"


def test_apply_watermark_image(tmp_path):
    input_path = ASSETS_DIR / "test_input.jpg"
    watermark_path = ASSETS_DIR / "logo.webp"

    image_bytes = input_path.read_bytes()
    watermarked = apply_watermark_image(image_bytes, str(watermark_path))

    output_path = tmp_path / "watermarked.jpg"
    output_path.write_bytes(watermarked)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
