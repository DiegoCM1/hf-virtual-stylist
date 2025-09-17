import time, uuid, random
from app.models.generate import GenerationRequest, GenerationResponse, ImageResult


class Generator:
    def generate(self, req: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError


# Let us demo end to end, able to switch to SDXL later without changing routes.
class MockGenerator(Generator):
    def generate(self, req: GenerationRequest) -> GenerationResponse:
        t0 = time.time()
        rid = str(uuid.uuid4())[:8]
        imgs = []
        for c in req.cuts[:2]:
            # placeholder size ~1024x1536 for portrait-like
            url = f"https://picsum.photos/seed/{c}-{random.randint(1,9999)}/1024/1536"
            imgs.append(
                ImageResult(
                    cut=c,
                    url=url,
                    width=1024,
                    height=1536,
                    watermark=True,
                    meta={"mock": "true"},
                )
            )
        return GenerationResponse(
            request_id=rid,
            status="completed",
            images=imgs,
            duration_ms=int((time.time() - t0) * 1000),
            meta={"family_id": req.family_id, "color_id": req.color_id},
        )

    # Keeping mock as fallback...


import base64, io, time, uuid
from typing import List
from PIL import Image
import torch
from diffusers import StableDiffusionXLPipeline

from app.models.generate import GenerationRequest, GenerationResponse, ImageResult


class SdxlTurboGenerator(Generator):
    _pipe = None  # lazy singleton

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
        # CPU-friendly defaults for Turbo
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

        images: List[ImageResult] = []
        for cut in cuts:
            seed = req.seed or seed_map.get(cut, 1234)
            g = torch.Generator(device="cpu").manual_seed(seed)
            img = pipe(
                prompt=prompts.get(cut, base_prompt),
                num_inference_steps=steps,
                guidance_scale=guidance,
                width=width,
                height=height,
                generator=g,
            ).images[0]

            images.append(
                ImageResult(
                    cut=cut,
                    url=self._to_data_url(img),
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
            request_id=str(uuid.uuid4())[:8],
            status="completed",
            images=images,
            duration_ms=int((time.time() - t0) * 1000),
            meta={
                "family_id": req.family_id,
                "color_id": req.color_id,
                "device": "cpu",
            },
        )
