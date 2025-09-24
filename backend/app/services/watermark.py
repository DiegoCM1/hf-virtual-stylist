from PIL import Image
import io

def apply_watermark_image(image_bytes: bytes, watermark_path: str, scale: float = 0.15) -> bytes:
    """
    Apply an image watermark (PNG with transparency) to the bottom-right corner.

    :param image_bytes: The base image in bytes
    :param watermark_path: Path to the watermark PNG file
    :param scale: Fraction of base image width to scale the watermark (0.15 = 15%)
    :return: New image bytes with watermark applied
    """
    # open base image
    with Image.open(io.BytesIO(image_bytes)).convert("RGBA") as base:
        # open watermark
        with Image.open(watermark_path).convert("RGBA") as wm:
            # resize watermark relative to base width
            wm_width = int(base.width * scale)
            wm_height = int(wm.height * wm_width / wm.width)
            wm_resized = wm.resize((wm_width, wm_height), Image.LANCZOS)

            # position bottom-right
            x = base.width - wm_resized.width - 10
            y = base.height - wm_resized.height - 10

            # paste with alpha
            base.alpha_composite(wm_resized, dest=(x, y))

            # save to bytes
            output = io.BytesIO()
            base.convert("RGB").save(output, format="JPEG", quality=95)
            return output.getvalue()
