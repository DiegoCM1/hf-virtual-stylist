from __future__ import annotations
import io, os, time, uuid, random
from typing import List
from PIL import Image, ImageDraw, ImageFont

from app.models.generate import GenerationRequest, GenerationResponse, ImageResult
from app.services.storage import save_bytes
from app.services.watermark import apply_watermark_image

# Config
WATERMARK_PATH = os.getenv("WATERMARK_PATH", "tests/assets/logo.webp")


class Generator:
    def generate(self, req: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError
    
# --- Helpers ---------------------------------------------------------------

def _placeholder_bytes(text: str, width=1024, height=1536) -> bytes:
    img = Image.new("RGB", (width, height), (24, 24, 24))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), text, font=font) 
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((width - tw) // 2, (height - th) // 2), text, fill=(230, 230, 230), font=font)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()



# --- Mock generator (now returns saved, watermarked URLs) ------------------

class MockGenerator(Generator):
    def generate(self, req: GenerationRequest) -> GenerationResponse:
        t0 = time.time()
        run_id = uuid.uuid4().hex[:10]
        images: List[ImageResult] = []

        cuts = (req.cuts or ["recto", "cruzado"])[:2]
        for cut in cuts:
            raw = _placeholder_bytes(f"{req.family_id}:{req.color_id}:{cut}")
            wm = apply_watermark_image(raw, WATERMARK_PATH, scale=0.12)  # watermark first
            key = f"generated/{req.family_id}/{req.color_id}/{run_id}/{cut}.jpg"
            url = save_bytes(wm, key)  # then save → URL
            images.append(ImageResult(cut=cut, url=url, width=1024, height=1536, watermark=True))

        return GenerationResponse(
            request_id=run_id,
            status="completed",
            images=images,
            duration_ms=int((time.time() - t0) * 1000),
            meta={"family_id": req.family_id, "color_id": req.color_id, "engine": "mock"},
        )



import base64, io, time, uuid
from typing import List
from PIL import Image
import torch
from diffusers import StableDiffusionXLPipeline

from app.models.generate import GenerationRequest, GenerationResponse, ImageResult


class SdxlTurboGenerator(Generator):
    _pipe = None  # lazy singleton

    def __init__(self, watermark_path: str = "logo.webp"):
        self.watermark_path = watermark_path

    @classmethod
    def _get_pipe(cls):
        if cls._pipe is None:
            cls._pipe = StableDiffusionXLPipeline.from_pretrained(
                r"D:\models\sdxl-turbo",
                dtype=torch.float32,  # <- use dtype (not string)
                low_cpu_mem_usage=True,
            )
            cls._pipe.to("cpu")
            try:
                cls._pipe.enable_attention_slicing()
            except Exception:
                pass
        return cls._pipe

    @staticmethod
    def _to_data_url(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(
            "utf-8"
        )

    def generate(self, req: GenerationRequest) -> GenerationResponse:
        t0 = time.time()
        pipe = self._get_pipe()

        cuts = (req.cuts or ["recto", "cruzado"])[:2]
        # CPU-friendly defaults for Turbo (keep your values)
        width, height = 640, 640
        steps, guidance = 4, 0.0

        base_prompt = (
            "man wearing an elegant bespoke suit, photorealistic, "
            "neutral studio lighting, high detail, clean background"
        )
        prompts = {
            "recto": base_prompt + ", front view shoulders to knees",
            "cruzado": base_prompt + ", three-quarter view slightly angled",
        }
        seed_map = {"recto": 12345, "cruzado": 67890}

        run_id = str(uuid.uuid4())[:8]
        images: List[ImageResult] = []

        for cut in cuts:
            seed = req.seed or seed_map.get(cut, 1234)
            g = torch.Generator(device="cpu").manual_seed(seed)

            # 1) Generate PIL image (unchanged)
            img: Image.Image = pipe(
                prompt=prompts.get(cut, base_prompt),
                num_inference_steps=steps,
                guidance_scale=guidance,
                width=width,
                height=height,
                generator=g,
            ).images[0]

            # 2) PIL -> bytes (JPEG). Keep PNG if you prefer, but JPEG is fine.
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            raw_bytes = buf.getvalue()

            # 3) Watermark bytes
            wm_bytes = apply_watermark_image(raw_bytes, self.watermark_path, scale=0.12)

            # 4) Save -> URL
            key = f"generated/{req.family_id}/{req.color_id}/{run_id}/{cut}.jpg"
            url = save_bytes(wm_bytes, key)

            images.append(
                ImageResult(
                    cut=cut,
                    url=url,                 # <-- now a public URL, not data URL
                    width=width,
                    height=height,
                    watermark=True,
                    meta={
                        "seed": str(seed),
                        "steps": str(steps),
                        "guidance": str(guidance),
                        "engine": "sdxl-turbo",
                    },
                )
            )

        return GenerationResponse(
            request_id=run_id,
            status="completed",
            images=images,
            duration_ms=int((time.time() - t0) * 1000),
            meta={
                "family_id": req.family_id,
                "color_id": req.color_id,
                "device": "cpu",
            },
        )
