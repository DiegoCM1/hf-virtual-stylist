"""
Inpainting generator for selective suit fabric replacement.

This generator uses SDXL Inpainting + IP-Adapter Plus to replace only the suit
fabric in a reference photo while keeping face, hands, shirt, and background intact.

Usage:
    - Set GENERATOR_MODE=inpaint in environment
    - Provide reference images and masks in assets/inpaint/
    - Worker will use this generator instead of full generation
"""
from __future__ import annotations

import gc
import hashlib
import io
import os
import secrets
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import urllib.request

import torch
from PIL import Image
from diffusers import (
    StableDiffusionXLInpaintPipeline,
    DPMSolverMultistepScheduler,
)

from app.generation.schemas import GenerationRequest, GenerationResponse, ImageResult
from app.generation.storage import Storage
from app.generation.watermark import apply_watermark_image
from app.generation.generator_config import WATERMARK_PATH
from app.generation.generator_mock import Generator
from app.core.config import PUBLIC_BASE_URL


# =============================================================================
# CONFIGURATION (from environment variables)
# =============================================================================

# Inpainting-specific settings
INPAINT_MODEL = os.getenv("INPAINT_MODEL", "diffusers/stable-diffusion-xl-1.0-inpainting-0.1")
INPAINT_STRENGTH = float(os.getenv("INPAINT_STRENGTH", "0.85"))
INPAINT_GUIDANCE = float(os.getenv("INPAINT_GUIDANCE", "7.5"))
INPAINT_STEPS = int(os.getenv("INPAINT_STEPS", "50"))

# IP-Adapter Plus configuration (inpainting uses separate vars to not conflict with full mode)
IP_ADAPTER_ENABLED = os.getenv("IP_ADAPTER_ENABLED", "1") == "1"
IP_ADAPTER_REPO = os.getenv("IP_ADAPTER_REPO", "h94/IP-Adapter")
IP_ADAPTER_SUBFOLDER = os.getenv("IP_ADAPTER_SUBFOLDER", "sdxl_models")
# Using IP-Adapter Plus by default for better detail preservation
# Falls back to IP_ADAPTER_WEIGHT if INPAINT_IP_ADAPTER_WEIGHT not set
IP_ADAPTER_WEIGHT = os.getenv(
    "INPAINT_IP_ADAPTER_WEIGHT",
    os.getenv("IP_ADAPTER_WEIGHT", "ip-adapter-plus_sdxl_vit-h.safetensors")
)
IP_ADAPTER_SCALE = float(os.getenv(
    "INPAINT_IP_ADAPTER_SCALE",
    os.getenv("IP_ADAPTER_SCALE", "0.7")
))

# Asset paths (reference images and masks)
ASSETS_DIR = Path(os.getenv("INPAINT_ASSETS_DIR", "/workspace/app/backend/assets/inpaint"))
REFERENCE_RECTO = os.getenv("INPAINT_REF_RECTO", str(ASSETS_DIR / "recto_reference.jpg"))
REFERENCE_CRUZADO = os.getenv("INPAINT_REF_CRUZADO", str(ASSETS_DIR / "cruzado_reference.jpg"))
MASK_RECTO = os.getenv("INPAINT_MASK_RECTO", str(ASSETS_DIR / "recto_mask.png"))
MASK_CRUZADO = os.getenv("INPAINT_MASK_CRUZADO", str(ASSETS_DIR / "cruzado_mask.png"))


def _log_config():
    """Log configuration at module load for debugging."""
    print(f"[inpaint-config] INPAINT_MODEL = {INPAINT_MODEL}")
    print(f"[inpaint-config] INPAINT_STRENGTH = {INPAINT_STRENGTH}")
    print(f"[inpaint-config] INPAINT_GUIDANCE = {INPAINT_GUIDANCE}")
    print(f"[inpaint-config] INPAINT_STEPS = {INPAINT_STEPS}")
    print(f"[inpaint-config] IP_ADAPTER_ENABLED = {IP_ADAPTER_ENABLED}")
    print(f"[inpaint-config] IP_ADAPTER_WEIGHT = {IP_ADAPTER_WEIGHT}")
    print(f"[inpaint-config] IP_ADAPTER_SCALE = {IP_ADAPTER_SCALE}")
    print(f"[inpaint-config] ASSETS_DIR = {ASSETS_DIR}")


_log_config()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _load_image_from_path(path: str) -> Optional[Image.Image]:
    """Load an image from a local path."""
    try:
        if not path or not os.path.exists(path):
            print(f"[inpaint] Image not found: {path}")
            return None
        return Image.open(path).convert("RGB")
    except Exception as e:
        print(f"[inpaint] Failed to load image {path}: {e}")
        return None


def _load_mask_from_path(path: str) -> Optional[Image.Image]:
    """Load a mask image (grayscale/binary)."""
    try:
        if not path or not os.path.exists(path):
            print(f"[inpaint] Mask not found: {path}")
            return None
        # Masks should be loaded as grayscale, then converted to RGB for pipeline
        mask = Image.open(path).convert("L")
        return mask
    except Exception as e:
        print(f"[inpaint] Failed to load mask {path}: {e}")
        return None


def _download_image_from_url(url: str, timeout: int = 15) -> Optional[Image.Image]:
    """Download an image from a URL."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            # Might be a local path
            return _load_image_from_path(url)

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (HFVirtualStylist/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return Image.open(io.BytesIO(response.read())).convert("RGB")
    except Exception as e:
        print(f"[inpaint] Failed to download image from {url}: {e}")
        return None


def _resize_to_match(
    image: Image.Image,
    target_size: Tuple[int, int],
    resample: int = Image.BICUBIC
) -> Image.Image:
    """Resize image to match target size."""
    if image.size != target_size:
        return image.resize(target_size, resample)
    return image


# =============================================================================
# INPAINTING GENERATOR
# =============================================================================

class InpaintGenerator(Generator):
    """
    Production inpainting generator using SDXL Inpaint + IP-Adapter Plus.

    This generator:
    1. Loads a reference photo (model wearing suit)
    2. Loads a binary mask (white = suit area to regenerate)
    3. Uses IP-Adapter to transfer texture from swatch image
    4. Regenerates ONLY the masked area with the new fabric texture

    Result: Same photo with different suit fabric, everything else unchanged.
    """

    _pipe = None  # Lazy singleton
    _device = "cpu"
    _references: Dict[str, Image.Image] = {}
    _masks: Dict[str, Image.Image] = {}
    _assets_loaded = False

    def __init__(self, storage: Storage, watermark_path: Optional[str] = None):
        self.storage = storage
        self.watermark_path = watermark_path or WATERMARK_PATH

    @classmethod
    def _load_assets(cls) -> bool:
        """
        Load reference images and masks into memory.
        Returns True if all assets loaded successfully.
        """
        if cls._assets_loaded:
            return True

        print("[inpaint] Loading reference images and masks...")

        # Load references
        recto_ref = _load_image_from_path(REFERENCE_RECTO)
        cruzado_ref = _load_image_from_path(REFERENCE_CRUZADO)

        if recto_ref is None and cruzado_ref is None:
            print("[inpaint] ERROR: No reference images found!")
            print(f"  Checked: {REFERENCE_RECTO}")
            print(f"  Checked: {REFERENCE_CRUZADO}")
            return False

        # Load masks
        recto_mask = _load_mask_from_path(MASK_RECTO)
        cruzado_mask = _load_mask_from_path(MASK_CRUZADO)

        if recto_mask is None and cruzado_mask is None:
            print("[inpaint] ERROR: No masks found!")
            print(f"  Checked: {MASK_RECTO}")
            print(f"  Checked: {MASK_CRUZADO}")
            return False

        # Store loaded assets
        if recto_ref:
            cls._references["recto"] = recto_ref
            print(f"[inpaint] Loaded recto reference: {recto_ref.size}")
        if cruzado_ref:
            cls._references["cruzado"] = cruzado_ref
            print(f"[inpaint] Loaded cruzado reference: {cruzado_ref.size}")
        if recto_mask:
            cls._masks["recto"] = recto_mask
            print(f"[inpaint] Loaded recto mask: {recto_mask.size}")
        if cruzado_mask:
            cls._masks["cruzado"] = cruzado_mask
            print(f"[inpaint] Loaded cruzado mask: {cruzado_mask.size}")

        cls._assets_loaded = True
        return True

    @classmethod
    def _get_pipeline(cls):
        """
        Lazy-load the inpainting pipeline (singleton).
        """
        if cls._pipe is not None:
            return cls._pipe

        t0 = time.time()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        print(f"[inpaint] Initializing SDXL Inpaint pipeline on {device}...")
        print(f"[inpaint] Loading model: {INPAINT_MODEL}")

        # Load SDXL Inpainting pipeline (must use inpainting-specific model)
        cls._pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
            INPAINT_MODEL,
            torch_dtype=dtype,
            use_safetensors=True,
        ).to(device)

        # Configure scheduler (DPM-Solver with Karras sigmas for quality)
        cls._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            cls._pipe.scheduler.config,
            use_karras_sigmas=True
        )

        # Memory optimizations
        cls._pipe.enable_attention_slicing()
        cls._pipe.enable_vae_tiling()
        cls._pipe.enable_vae_slicing()

        # Try to enable xformers for better performance
        try:
            if device == "cuda":
                cls._pipe.enable_xformers_memory_efficient_attention()
                print("[inpaint] xformers enabled")
        except Exception:
            print("[inpaint] xformers not available, using default attention")

        # Load IP-Adapter Plus
        if IP_ADAPTER_ENABLED:
            print(f"[inpaint] Loading IP-Adapter: {IP_ADAPTER_WEIGHT}")
            try:
                cls._pipe.load_ip_adapter(
                    IP_ADAPTER_REPO,
                    subfolder=IP_ADAPTER_SUBFOLDER,
                    weight_name=IP_ADAPTER_WEIGHT,
                )
                cls._pipe.set_ip_adapter_scale(IP_ADAPTER_SCALE)
                print(f"[inpaint] IP-Adapter loaded, scale={IP_ADAPTER_SCALE}")
            except Exception as e:
                print(f"[inpaint] WARNING: Failed to load IP-Adapter Plus, trying base version: {e}")
                try:
                    # Fallback to base IP-Adapter
                    cls._pipe.load_ip_adapter(
                        IP_ADAPTER_REPO,
                        subfolder=IP_ADAPTER_SUBFOLDER,
                        weight_name="ip-adapter_sdxl.bin",
                    )
                    cls._pipe.set_ip_adapter_scale(IP_ADAPTER_SCALE)
                    print("[inpaint] Fallback: IP-Adapter base loaded")
                except Exception as e2:
                    print(f"[inpaint] ERROR: Could not load any IP-Adapter: {e2}")

        cls._device = device
        print(f"[inpaint] Pipeline ready in {time.time() - t0:.2f}s")

        return cls._pipe

    def _get_assets_for_cut(
        self,
        cut: str,
        target_size: Tuple[int, int]
    ) -> Tuple[Optional[Image.Image], Optional[Image.Image]]:
        """
        Get reference image and mask for a specific cut, resized to target.
        Returns (reference, mask) tuple.
        """
        reference = self._references.get(cut)
        mask = self._masks.get(cut)

        if reference is None:
            print(f"[inpaint] WARNING: No reference for cut '{cut}'")
            # Try to use the other cut as fallback
            fallback_cut = "cruzado" if cut == "recto" else "recto"
            reference = self._references.get(fallback_cut)
            mask = self._masks.get(fallback_cut)
            if reference:
                print(f"[inpaint] Using fallback reference from '{fallback_cut}'")

        if reference is None or mask is None:
            return None, None

        # Resize to target dimensions
        reference_resized = _resize_to_match(reference, target_size)
        mask_resized = _resize_to_match(mask, target_size, resample=Image.NEAREST)

        return reference_resized, mask_resized

    def generate(self, req: GenerationRequest) -> GenerationResponse:
        """
        Generate images using inpainting.

        Process:
        1. Load reference image and mask for each cut
        2. Download swatch image for IP-Adapter
        3. Run inpainting to replace suit fabric
        4. Apply watermark and upload to storage
        """
        print(f"\n{'='*70}")
        print(f"[inpaint] Starting generation")
        print(f"{'='*70}")
        print(f"  Request: family_id={req.family_id}, color_id={req.color_id}")
        print(f"  Cuts: {req.cuts}")
        print(f"  Swatch URL: {req.swatch_url}")
        print(f"  INPAINT_STRENGTH: {INPAINT_STRENGTH}")
        print(f"  INPAINT_GUIDANCE: {INPAINT_GUIDANCE}")
        print(f"  INPAINT_STEPS: {INPAINT_STEPS}")
        print(f"{'='*70}\n")

        t0 = time.time()

        # Load assets if not already loaded
        if not self._load_assets():
            raise RuntimeError(
                "Failed to load inpainting assets. "
                "Ensure reference images and masks exist in assets/inpaint/"
            )

        # Get pipeline
        pipe = self._get_pipeline()
        device = self._device

        # Determine cuts to generate
        cuts = (req.cuts or ["recto", "cruzado"])[:2]

        # Output dimensions (match reference images or use default)
        # Using vertical format suitable for suit display
        width, height = 1024, 1536

        # Download swatch image for IP-Adapter
        swatch_image = None
        if req.swatch_url:
            print(f"[inpaint] Downloading swatch from: {req.swatch_url}")
            swatch_image = _download_image_from_url(req.swatch_url)
            if swatch_image:
                print(f"[inpaint] Swatch loaded: {swatch_image.size}")
            else:
                print("[inpaint] WARNING: Failed to load swatch, proceeding without IP-Adapter image")

        # Prompts for inpainting
        prompt = (
            "high quality suit fabric texture, tailored menswear, "
            "detailed weave pattern, professional studio lighting, "
            "crisp lapels, clean stitching"
        )
        negative_prompt = (
            "blurry, low quality, distorted, watermark, text, "
            "wrinkled, dirty, stained, torn fabric"
        )

        # Prepare IP-Adapter kwargs
        ip_kwargs = {}
        if IP_ADAPTER_ENABLED and swatch_image is not None:
            ip_kwargs["ip_adapter_image"] = swatch_image
        elif IP_ADAPTER_ENABLED:
            # IP-Adapter is enabled but no swatch - use blank with scale 0
            print("[inpaint] No swatch provided, using neutral IP-Adapter input")
            blank = Image.new("RGB", (512, 512), (200, 200, 200))
            ip_kwargs["ip_adapter_image"] = blank
            pipe.set_ip_adapter_scale(0.0)

        # Generate for each cut
        run_id = uuid.uuid4().hex[:10]
        base_seed = req.seed if req.seed is not None else secrets.randbits(32)
        images: List[ImageResult] = []

        for cut in cuts:
            print(f"\n[inpaint] Processing cut: {cut}")

            # Get reference and mask
            reference, mask = self._get_assets_for_cut(cut, (width, height))

            if reference is None or mask is None:
                print(f"[inpaint] ERROR: Missing assets for cut '{cut}', skipping")
                continue

            # Derive per-cut seed for reproducibility
            derived = hashlib.sha256(f"{base_seed}:{cut}".encode()).digest()
            seed = int.from_bytes(derived[:4], "little")
            generator = torch.Generator(device=device).manual_seed(seed)

            print(f"[inpaint] Generating with seed={seed}")
            t1 = time.time()

            # Reset IP-Adapter scale if we have a swatch
            if IP_ADAPTER_ENABLED and swatch_image is not None:
                pipe.set_ip_adapter_scale(IP_ADAPTER_SCALE)

            try:
                # Run inpainting
                result = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=reference,
                    mask_image=mask,
                    strength=INPAINT_STRENGTH,
                    guidance_scale=INPAINT_GUIDANCE,
                    num_inference_steps=INPAINT_STEPS,
                    width=width,
                    height=height,
                    generator=generator,
                    **ip_kwargs,
                ).images[0]

                print(f"[inpaint] Generation done in {time.time() - t1:.2f}s")

            except Exception as e:
                print(f"[inpaint] ERROR during generation: {e}")
                raise

            # Post-process: watermark and upload
            buf = io.BytesIO()
            result.save(buf, format="JPEG", quality=95)
            raw_bytes = buf.getvalue()

            wm_bytes = apply_watermark_image(raw_bytes, self.watermark_path, scale=0.30)
            key = f"generated/{req.family_id}/{req.color_id}/{run_id}/{cut}.jpg"
            saved_url = self.storage.save_bytes(wm_bytes, key)

            # Apply public URL if configured
            if PUBLIC_BASE_URL:
                parsed = urlparse(saved_url)
                path = parsed.path if parsed.scheme else saved_url
                public_url = urljoin(PUBLIC_BASE_URL.rstrip('/') + '/', path.lstrip('/'))
            else:
                public_url = saved_url

            images.append(
                ImageResult(
                    cut=cut,
                    url=public_url,
                    width=width,
                    height=height,
                    watermark=True,
                    meta={
                        "seed": str(seed),
                        "steps": str(INPAINT_STEPS),
                        "guidance": str(INPAINT_GUIDANCE),
                        "strength": str(INPAINT_STRENGTH),
                        "engine": "sdxl-inpaint",
                        "ip_adapter_scale": str(IP_ADAPTER_SCALE) if swatch_image else "0",
                    },
                )
            )

            # Clear CUDA cache between cuts
            if device == "cuda":
                gc.collect()
                torch.cuda.empty_cache()

        total_time = time.time() - t0
        print(f"\n[inpaint] All cuts completed in {total_time:.2f}s")

        return GenerationResponse(
            request_id=run_id,
            status="completed",
            images=images,
            duration_ms=int(total_time * 1000),
            meta={
                "family_id": req.family_id,
                "color_id": req.color_id,
                "device": device,
                "engine": "inpaint",
            },
        )
