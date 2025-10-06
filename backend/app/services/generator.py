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
from app.core.config import (
    PUBLIC_BASE_URL,
    CONTROLNET_ENABLED, CONTROLNET_MODEL,
    CONTROLNET_WEIGHT, CONTROLNET_GUIDANCE_START, CONTROLNET_GUIDANCE_END,
    CONTROL_IMAGE_RECTO, CONTROL_IMAGE_CRUZADO
)
import base64, io, time, uuid
from typing import List
import torch
from diffusers import (
    StableDiffusionXLPipeline,
    StableDiffusionXLImg2ImgPipeline,
    DPMSolverMultistepScheduler,
    StableDiffusionXLControlNetPipeline,
    ControlNetModel,
)

from app.models.generate import GenerationRequest, GenerationResponse, ImageResult
from pathlib import Path




# Config / Env toggles for refiner
USE_REFINER = os.getenv("USE_REFINER", "1") == "1"
TOTAL_STEPS = int(os.getenv("TOTAL_STEPS", "60"))
REFINER_SPLIT = float(os.getenv("REFINER_SPLIT", "0.70"))

# --- SECOND CONTROLNET (CANNY) via env (kept local to this module) ----------
CONTROLNET2_ENABLED = os.getenv("CONTROLNET2_ENABLED", "0") == "1"
CONTROLNET2_MODEL = os.getenv("CONTROLNET2_MODEL", "")
CONTROLNET2_WEIGHT = float(os.getenv("CONTROLNET2_WEIGHT", "0.7"))
CONTROLNET2_GUIDANCE_START = float(os.getenv("CONTROLNET2_GUIDANCE_START", "0.00"))
CONTROLNET2_GUIDANCE_END = float(os.getenv("CONTROLNET2_GUIDANCE_END", "0.90"))
CONTROL_IMAGE_RECTO_CANNY = os.getenv("CONTROL_IMAGE_RECTO_CANNY", "")
CONTROL_IMAGE_CRUZADO_CANNY = os.getenv("CONTROL_IMAGE_CRUZADO_CANNY", "")

# Watermark path not correct
def _resolve_wm_path() -> str:
    # 1) env override (deploy.sh can set this)
    p = os.getenv("WATERMARK_PATH")
    if p and Path(p).exists():
        return p
    # 2) repo default: backend/tests/assets/watermark-logo.png
    repo_default = Path(__file__).resolve().parents[2] / "tests" / "assets" / "watermark-logo.png"
    if repo_default.exists():
        return str(repo_default)
    # 3) last-ditch (if someone drops a copy next to this module)
    sibling = Path(__file__).resolve().parent / "watermark-logo.png"
    if sibling.exists():
        return str(sibling)
    raise FileNotFoundError("Watermark not found. Set WATERMARK_PATH or keep tests/assets/watermark-logo.png")

WATERMARK_PATH = _resolve_wm_path()



class Generator:
    def generate(self, req: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError
    
# --- Helpers ---------------------------------------------------------------
def _placeholder_bytes(text: str, width=1344, height=2016) -> bytes:
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





class SdxlTurboGenerator(Generator):
    _base = None     # lazy singletons
    _refiner = None
    _device = "cpu"

    def __init__(self, storage: Storage, watermark_path: str | None = None):
        self.storage = storage
        self.watermark_path = watermark_path or WATERMARK_PATH

    @classmethod
    def _get_pipes(cls):
        if cls._base is not None:
            return cls._base, cls._refiner

        t0 = time.time()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        print("[sdxl] init: base on", device)
        cls._base = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=dtype,
            use_safetensors=True,
        ).to(device)
        try:
            if device == "cuda":
                cls._base.enable_xformers_memory_efficient_attention()
        except Exception:
            pass
        # --- Scheduler: DPM-Solver (Karras) + VAE memory helpers
        cls._base.scheduler = DPMSolverMultistepScheduler.from_config(
            cls._base.scheduler.config, use_karras_sigmas=True
        )
        cls._base.enable_vae_tiling()
        cls._base.enable_vae_slicing()

        # --- Optional ControlNet(s) ----------------------------------------------
        if CONTROLNET_ENABLED and CONTROLNET_MODEL:
            print(f"[controlnet] loading {CONTROLNET_MODEL}")
            cn_modules = []
            cn_depth = ControlNetModel.from_pretrained(
                CONTROLNET_MODEL,
                torch_dtype=dtype,
                use_safetensors=True,
            ).to(device)
            cn_modules.append(cn_depth)

            # Second CN (Canny), if enabled
            if CONTROLNET2_ENABLED and CONTROLNET2_MODEL:
                print(f"[controlnet-2] loading {CONTROLNET2_MODEL}")
                cn_canny = ControlNetModel.from_pretrained(
                    CONTROLNET2_MODEL,
                    torch_dtype=dtype,
                    use_safetensors=True,
                ).to(device)
                cn_modules.append(cn_canny)

            # For broad diffusers compatibility:
            # - if 1 CN → pass the single ControlNetModel
            # - if 2 CNs → pass a list; SDXL ControlNet pipeline accepts List[ControlNetModel]
            controlnet = cn_modules[0] if len(cn_modules) == 1 else cn_modules

            cls._base = StableDiffusionXLControlNetPipeline(
                vae=cls._base.vae,
                text_encoder=cls._base.text_encoder,
                text_encoder_2=cls._base.text_encoder_2,
                tokenizer=cls._base.tokenizer,
                tokenizer_2=cls._base.tokenizer_2,
                unet=cls._base.unet,
                controlnet=controlnet,
                scheduler=cls._base.scheduler,
                feature_extractor=cls._base.feature_extractor,
            ).to(device)
            try:
                if device == "cuda":
                    cls._base.enable_xformers_memory_efficient_attention()
            except Exception:
                pass
            cls._base.enable_vae_tiling()
            cls._base.enable_vae_slicing()
            print("[controlnet] enabled")

        if USE_REFINER:
            print("[sdxl] init: refiner on", device)
            cls._refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-refiner-1.0",
                torch_dtype=dtype,
                use_safetensors=True,
            ).to(device)
            try:
                if device == "cuda":
                    cls._refiner.enable_xformers_memory_efficient_attention()
            except Exception:
                pass
            # --- Scheduler + VAE helpers for refiner as well
            cls._refiner.scheduler = DPMSolverMultistepScheduler.from_config(
                cls._refiner.scheduler.config, use_karras_sigmas=True
            )
            cls._refiner.enable_vae_tiling()
            cls._refiner.enable_vae_slicing()

        print(f"[sdxl] init: done in {time.time()-t0:.2f}s")
        cls._device = device
        return cls._base, cls._refiner

    @staticmethod
    def _to_data_url(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(
            "utf-8"
        )
    
    
    def _control_images_for_cut(self, cut: str, size: tuple[int,int]):
        """
        Returns (images, scales, starts, ends) for enabled controlnets, resized to size.
        Each list can have length 0, 1, or 2 depending on what is enabled/available.
        """
        images, scales, starts, ends = [], [], [], []

        # Depth (primary)
        if CONTROLNET_ENABLED:
            dpath = CONTROL_IMAGE_RECTO if cut == "recto" else CONTROL_IMAGE_CRUZADO
            if dpath and os.path.exists(dpath):
                img = Image.open(dpath).convert("RGB").resize(size, Image.BICUBIC)
                images.append(img)
                scales.append(CONTROLNET_WEIGHT)
                starts.append(CONTROLNET_GUIDANCE_START)
                ends.append(CONTROLNET_GUIDANCE_END)

        # Canny (secondary)
        if CONTROLNET2_ENABLED:
            cpath = CONTROL_IMAGE_RECTO_CANNY if cut == "recto" else CONTROL_IMAGE_CRUZADO_CANNY
            if cpath and os.path.exists(cpath):
                img = Image.open(cpath).convert("RGB").resize(size, Image.BICUBIC)
                images.append(img)
                scales.append(CONTROLNET2_WEIGHT)
                starts.append(CONTROLNET2_GUIDANCE_START)
                ends.append(CONTROLNET2_GUIDANCE_END)

        return images, scales, starts, ends

    def generate(self, req: GenerationRequest) -> GenerationResponse:
        t0 = time.time()
        base, refiner = self._get_pipes()
        device = self._device

        cuts = (req.cuts or ["recto", "cruzado"])[:2]
        # Forzar 1 imagen por request para evitar 524 y simplificar FE
        cuts = (req.cuts or ["recto"])[:1]

        # Calidad (SDXL Base en GPU)
        width, height = 1344, 2016  # vertical, the bigger it is, the more details the image will have
        steps, guidance = TOTAL_STEPS, 4.3 # Guidance will tell the model how strictly to follow the prompt, usually 4.5 - 6 is best

        # Common product-photo prompt (neutral, high detail, e-comm style)
        base_prompt = (
            "studio catalog photo of a men's tailored suit on a manneque, ultra-realistic, high detail, "
            "clear background, even lighting, 85mm look, "
            "clean tailoring, correct grain, even drape, crisp lapels, sharp stitching, "
            "true fabric texture, no stretch, "
        )

        neg_prompt = (
            "blurry, low quality, text, watermark, logo, jpeg artifacts, "
            "texture stretching, melted cloth, rubbery fabric, wavy weave, "
            "misaligned buttons, off-center buttons, missing buttons, warped edges, "
            "asymmetry, twisted torso, duplicated patterns, heavy denoise"
        )

        # Minimal pose hints (ControlNet handles geometry)  garment specifics
        CUT_TEMPLATES = {
            "recto": {
                "pos": "single-breasted 2-button, notch lapels, patch pockets, buttons centered on placket, symmetric front",
                "neg": "double-breasted, peak lapels"
            },
            "cruzado": {
                "pos": "double-breasted 6x2, peak lapels, clean overlap, button rows symetric",
                "neg": "single-breasted, notch lapels"
            },
        }

        def build_prompts(base_pos: str, base_neg: str, cut: str):
            d = CUT_TEMPLATES.get(cut, {"pos": "", "neg": ""})
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
            if refiner:
                # Optional ControlNet kwargs (apply only on base stage)
                imgs, scales, starts, ends = self._control_images_for_cut(cut, (width, height))
                extra = {}
                if imgs:
                    # Support 1 or 2 controlnets transparently
                    payload = imgs if len(imgs) > 1 else imgs[0]
                    w = scales if len(scales) > 1 else scales[0]
                    s = starts if len(starts) > 1 else starts[0]
                    e = ends if len(ends) > 1 else ends[0]
                    extra = dict(
                        image=payload,
                        controlnet_conditioning_scale=w,
                        control_guidance_start=s,
                        control_guidance_end=e,
                    )

                # Base → latent (0 → split)
                base_out = base(
                    prompt=pos,
                    negative_prompt=neg,
                    num_inference_steps=steps,
                    denoising_end=REFINER_SPLIT,
                    guidance_scale=guidance,
                    width=width,
                    height=height,
                    generator=g,
                    num_images_per_prompt=1,
                    output_type="latent",
                    **extra,
                )
                latents = base_out.images  # latent tensor

                # Refiner → image (split → 1.0)
                refiner_steps = max(5, int(round(steps * (1.0 - REFINER_SPLIT))))
                img: Image.Image = refiner(
                    prompt=pos,
                    negative_prompt=neg,
                    num_inference_steps=refiner_steps,
                    denoising_start=REFINER_SPLIT,
                    guidance_scale=guidance,
                    image=latents,
                    generator=g,
                ).images[0]
            else:
                # Optional ControlNet kwargs (no refiner path)
                imgs, scales, starts, ends = self._control_images_for_cut(cut, (width, height))
                extra = {}
                if imgs:
                    payload = imgs if len(imgs) > 1 else imgs[0]
                    w = scales if len(scales) > 1 else scales[0]
                    s = starts if len(starts) > 1 else starts[0]
                    e = ends if len(ends) > 1 else ends[0]
                    extra = dict(
                        image=payload,
                        controlnet_conditioning_scale=w,
                        control_guidance_start=s,
                        control_guidance_end=e,
                    )
                img: Image.Image = base(
                    prompt=pos,
                    negative_prompt=neg,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    width=width,
                    height=height,
                    generator=g,
                    num_images_per_prompt=1,
                    **extra,
                ).images[0]
            print(f"[sdxl] {cut}: infer done in {time.time()-t1:.2f}s (seed={seed})")

            # bytes -> watermark -> storage URL
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            raw_bytes = buf.getvalue()

            wm_bytes = apply_watermark_image(raw_bytes, self.watermark_path, scale=0.30)
            key = f"generated/{req.family_id}/{req.color_id}/{run_id}/{cut}.jpg"
            saved_url  = self.storage.save_bytes(wm_bytes, key)

            # --- Force public domain if env is set ---
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
                        "engine": "sdxl-refiner" if refiner else "sdxl-base",
                        "refiner_split": str(REFINER_SPLIT),
                        "refiner_steps": str(refiner_steps) if refiner else "0",                    
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

