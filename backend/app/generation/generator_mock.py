"""Mock generator for testing without GPU."""
import io
import time
import uuid
from dataclasses import dataclass
from typing import List
from PIL import Image, ImageDraw, ImageFont

from app.generation.schemas import GenerationRequest, GenerationResponse, ImageResult
from app.generation.storage import Storage
from app.generation.watermark import apply_watermark_image
from app.generation.generator_config import WATERMARK_PATH


class Generator:
    """Base generator interface."""
    def generate(self, req: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError


def _placeholder_bytes(text: str, width=1344, height=2016) -> bytes:
    """Generate a placeholder image with text."""
    img = Image.new("RGB", (width, height), (24, 24, 24))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((width - tw) // 2, (height - th) // 2), text, fill=(230, 230, 230), font=font)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


@dataclass
class MockGenerator(Generator):
    """Mock generator that returns placeholder images (fast, no GPU required)."""
    storage: Storage

    def generate(self, req: GenerationRequest) -> GenerationResponse:
        t0 = time.time()
        run_id = uuid.uuid4().hex[:10]
        images: List[ImageResult] = []

        cuts = (req.cuts or ["recto", "cruzado"])[:2]
        for cut in cuts:
            raw = _placeholder_bytes(f"{req.family_id}:{req.color_id}:{cut}")
            wm = apply_watermark_image(raw, WATERMARK_PATH, scale=0.30)  # watermark first
            key = f"generated/{req.family_id}/{req.color_id}/{run_id}/{cut}.jpg"
            url = self.storage.save_bytes(wm, key)  # then save → URL
            images.append(
                ImageResult(
                    cut=cut,
                    url=url,
                    width=1344,
                    height=2016,
                    watermark=True,
                )
            )

        return GenerationResponse(
            request_id=run_id,
            status="completed",
            images=images,
            duration_ms=int((time.time() - t0) * 1000),
            meta={"family_id": req.family_id, "color_id": req.color_id, "engine": "mock"},
        )
