from __future__ import annotations
import io, os, time, uuid, random
from dataclasses import dataclass
from typing import List
from PIL import Image, ImageDraw, ImageFont

from app.models.generate import GenerationRequest, GenerationResponse, ImageResult
from app.services.storage import Storage, LocalStorage
from app.services.watermark import apply_watermark_image
import secrets
from urllib.parse import urljoin, urlparse
import hashlib
from app.core.config import PUBLIC_BASE_URL
import base64, io, time, uuid
from typing import List
from PIL import Image
import torch
from diffusers import StableDiffusionXLPipeline

from app.models.generate import GenerationRequest, GenerationResponse, ImageResult



# Config
WATERMARK_PATH = os.getenv("WATERMARK_PATH", "tests/assets/watermark-logo.png")


neg_prompt = ""


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

@dataclass
class MockGenerator(Generator):
    storage: Storage

    def generate(self, req: GenerationRequest) -> GenerationResponse:
        t0 = time.time()
        run_id = uuid.uuid4().hex[:10]
        images: List[ImageResult] = []

        cuts = (req.cuts or ["recto", "cruzado"])[:2]
        for cut in cuts:
            raw = _placeholder_bytes(f"{req.family_id}:{req.color_id}:{cut}")
            wm = apply_watermark_image(raw, WATERMARK_PATH, scale=0.12)  # watermark first
            key = f"generated/{req.family_id}/{req.color_id}/{run_id}/{cut}.jpg"
            url = self.storage.save_bytes(wm, key)  # then save → URL
            images.append(
                ImageResult(
                    cut=cut,
                    url=url,
                    width=1024,
                    height=1536,
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





class SdxlTurboGenerator(Generator):
    _pipe = None  # lazy singleton

    def __init__(self, storage: Storage, watermark_path: str = "watermark-logo.png"):
        self.storage = storage
        self.watermark_path = watermark_path

    @classmethod
    def _get_pipe(cls):
        if cls._pipe is not None:
            return cls._pipe

        import time, torch
        from diffusers import StableDiffusionXLPipeline

        t0 = time.time()
        print("[sdxl] init: base on cuda")
        cls._pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            dtype=torch.float16,          # fp16 en GPU (evita warning)
            use_safetensors=True,
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        cls._pipe.to(device)
        try:
            if device == "cuda":
                cls._pipe.enable_xformers_memory_efficient_attention()
        except Exception:
            pass
        print(f"[sdxl] init: done in {time.time()-t0:.2f}s on {device}")
        cls._device = device  # opcional: recordar el device
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
        device = "cuda" if torch.cuda.is_available() else "cpu"

        cuts = (req.cuts or ["recto", "cruzado"])[:2]
        # Forzar 1 imagen por request para evitar 524 y simplificar FE
        cuts = (req.cuts or ["recto"])[:1]

        # Calidad (SDXL Base en GPU)
        width, height = 1024, 1536  # vertical "recto"
        steps, guidance = 28, 5.5 #28 is the optimal one
        base_prompt = (
            "front view of a luxury men's suit on a mannequin, photorealistic, "
            "neutral studio lighting, sharp fabric texture, clean background"
        )

        neg_prompt = "blurry, low quality, text, watermark, logo, extra limbs, malformed"

        CUT_DELTAS = {
            "recto":   {"pos": "shoulders to knees, centered", 
                        "neg": ""},
            "cruzado": {"pos": "three-quarter view, slightly angled, diagonal feel",
                        "neg": "flat, straight-on, perfectly horizontal weave"}
        }

        def build_prompts(base_pos: str, base_neg: str, cut: str):
            d = CUT_DELTAS.get(cut, {"pos": "", "neg": ""})
            pos = f"{base_pos}, {d['pos']}".strip(", ")
            neg = base_neg + (", " + d["neg"] if d["neg"] else "")
            return pos, neg

        run_id = uuid.uuid4().hex[:10]
        images: List[ImageResult] = []

        base_seed = req.seed if req.seed is not None else secrets.randbits(32)

        for cut in cuts:
            # derive a per-cut seed from base_seed (stable & distinct)
            derived = hashlib.sha256(f"{base_seed}:{cut}".encode()).digest()
            seed = int.from_bytes(derived[:4], "little")
            g = torch.Generator(device=device).manual_seed(seed)

            print(f"[sdxl] {cut}: infer start")
            t1 = time.time()
            pos, neg = build_prompts(base_prompt, neg_prompt, cut)
            img: Image.Image = pipe(
                prompt=pos,
                negative_prompt=neg,
                num_inference_steps=steps,
                guidance_scale=guidance,
                width=width,
                height=height,
                generator=g,
                num_images_per_prompt=1,
            ).images[0]
            print(f"[sdxl] {cut}: infer done in {time.time()-t1:.2f}s (seed={seed})")

            # bytes -> watermark -> storage URL
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            raw_bytes = buf.getvalue()

            wm_bytes = apply_watermark_image(raw_bytes, self.watermark_path, scale=0.12)
            key = f"generated/{req.family_id}/{req.color_id}/{run_id}/{cut}.jpg"
            saved_url  = self.storage.save_bytes(wm_bytes, key)

            # --- NEW: force public domain if env is set ---
            if PUBLIC_BASE_URL:
                parsed = urlparse(saved_url)
                # if storage returned absolute (e.g., http://localhost:8000/...),
                # strip domain and keep only the path; if it was already relative, keep it
                path = parsed.path if parsed.scheme else saved_url
                public_url = urljoin(PUBLIC_BASE_URL.rstrip('/') + '/', path.lstrip('/'))
            else:
                public_url = saved_url
            # ---------------------------------------------

            images.append(
                ImageResult(
                    cut=cut,
                    url=public_url,
                    width=width,
                    height=height,
                    watermark=True,
                    meta={
                        "seed": str(seed),
                        "steps": str(steps),
                        "guidance": str(guidance),
                        "engine": "sdxl-base",
                    },
                )
            )

        return GenerationResponse(
            request_id=run_id,
            status="completed",
            images=images,
            duration_ms=int((time.time() - t0) * 1000),
            meta={"family_id": req.family_id, "color_id": req.color_id, "device": device},
        )

