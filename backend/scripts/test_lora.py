#!/usr/bin/env python3
"""
LoRA Testing Script - Isolated testing for LoRA models with SDXL

This script tests LoRA files (.safetensors) in isolation, without ControlNet,
IP-Adapter, or other components. This helps evaluate the LoRA's effect
before integrating it into the full pipeline.

Usage:
    # Basic test with default scales
    python test_lora.py /workspace/loras/my-lora.safetensors

    # Custom scales
    python test_lora.py /workspace/loras/my-lora.safetensors --scales 0.5,0.8,1.0

    # Custom prompt
    python test_lora.py /workspace/loras/my-lora.safetensors --prompt "navy blue suit"

    # Multiple LoRAs comparison
    python test_lora.py /workspace/loras/lora1.safetensors /workspace/loras/lora2.safetensors

Output:
    Results saved to /workspace/lora_tests/ with naming:
    - {lora_name}_scale_{scale}.png
    - baseline_no_lora.png (for comparison)
"""

import argparse
import os
import sys
import time
from pathlib import Path

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image


# =============================================================================
# CONFIGURATION - Adjust these for your testing needs
# =============================================================================

# Default output directory (on RunPod network volume for persistence)
DEFAULT_OUTPUT_DIR = "/workspace/lora_tests"

# Default prompt - similar to production but simplified for isolated testing
DEFAULT_PROMPT = (
    "studio photo of a men's tailored suit on a mannequin, "
    "ultra-realistic, white seamless background, soft even lighting, "
    "sharp tailoring, crisp lapels, detailed fabric texture"
)

DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, text, watermark, logo, deformed, "
    "bad anatomy, ugly, duplicate, poorly drawn"
)

# Default LoRA scales to test (0.0 = no effect, 1.0 = full effect)
DEFAULT_SCALES = [0.0, 0.5, 0.7, 0.85, 1.0]

# Generation parameters (kept simple for testing)
DEFAULT_STEPS = 30          # Fewer steps for faster iteration
DEFAULT_GUIDANCE = 7.0      # Standard CFG scale
DEFAULT_WIDTH = 1024        # SDXL native resolution
DEFAULT_HEIGHT = 1024
DEFAULT_SEED = 42           # Fixed seed for reproducible comparisons


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_pipeline(device: str = "cuda") -> StableDiffusionXLPipeline:
    """
    Load the base SDXL pipeline without any additions.

    We use the base model only (no refiner) to isolate the LoRA's effect.
    The refiner can be tested separately once we know the LoRA works.
    """
    print("[pipeline] Loading SDXL base model...")
    print("           This may take a minute on first run (downloading weights)")

    dtype = torch.float16 if device == "cuda" else torch.float32

    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=dtype,
        use_safetensors=True,
    ).to(device)

    # Use DPM-Solver for faster inference (same as production)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe.scheduler.config,
        use_karras_sigmas=True
    )

    # Memory optimizations
    pipe.enable_attention_slicing()
    if device == "cuda":
        try:
            pipe.enable_xformers_memory_efficient_attention()
            print("[pipeline] xformers enabled")
        except Exception:
            print("[pipeline] xformers not available, using default attention")

    print("[pipeline] SDXL base loaded successfully")
    return pipe


def load_lora(pipe: StableDiffusionXLPipeline, lora_path: str) -> str:
    """
    Load a LoRA file into the pipeline.

    Returns the adapter name (used for setting scale later).
    """
    lora_path = Path(lora_path)

    if not lora_path.exists():
        raise FileNotFoundError(f"LoRA file not found: {lora_path}")

    # Use filename (without extension) as adapter name
    adapter_name = lora_path.stem

    print(f"[lora] Loading: {lora_path.name}")

    pipe.load_lora_weights(
        str(lora_path.parent),           # Directory containing the LoRA
        weight_name=lora_path.name,      # Filename of the LoRA
        adapter_name=adapter_name        # Name to reference this LoRA
    )

    print(f"[lora] Loaded as adapter: '{adapter_name}'")
    return adapter_name


def generate_image(
    pipe: StableDiffusionXLPipeline,
    prompt: str,
    negative_prompt: str,
    seed: int,
    steps: int = DEFAULT_STEPS,
    guidance: float = DEFAULT_GUIDANCE,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> Image.Image:
    """
    Generate a single image with the current pipeline configuration.

    The LoRA scale should be set BEFORE calling this function.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    generator = torch.Generator(device=device).manual_seed(seed)

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance,
        width=width,
        height=height,
        generator=generator,
    )

    return result.images[0]


def test_lora_scales(
    pipe: StableDiffusionXLPipeline,
    adapter_name: str,
    scales: list[float],
    output_dir: Path,
    prompt: str,
    negative_prompt: str,
    seed: int,
    steps: int,
    guidance: float,
) -> list[dict]:
    """
    Test a LoRA at different scales and save results.

    This is the core testing function. It:
    1. Generates a baseline image (scale=0, no LoRA effect)
    2. Generates images at each specified scale
    3. Saves all images for visual comparison

    Returns a list of results with paths and timing info.
    """
    results = []

    for scale in scales:
        print(f"\n[test] Generating with scale={scale:.2f}...")

        # Set the LoRA scale
        # Scale of 0.0 effectively disables the LoRA (baseline)
        # Scale of 1.0 applies full LoRA effect
        pipe.set_adapters([adapter_name], adapter_weights=[scale])

        # Generate
        start_time = time.time()
        image = generate_image(
            pipe=pipe,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            steps=steps,
            guidance=guidance,
        )
        elapsed = time.time() - start_time

        # Save with descriptive filename
        if scale == 0.0:
            filename = f"{adapter_name}_baseline_no_effect.png"
        else:
            filename = f"{adapter_name}_scale_{scale:.2f}.png"

        output_path = output_dir / filename
        image.save(output_path)

        print(f"[test] Saved: {output_path.name} ({elapsed:.1f}s)")

        results.append({
            "scale": scale,
            "path": str(output_path),
            "time": elapsed,
        })

    return results


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Test LoRA models in isolation with SDXL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Positional: LoRA file(s) to test
    parser.add_argument(
        "lora_files",
        nargs="+",
        help="Path(s) to .safetensors LoRA file(s)"
    )

    # Optional: customize testing parameters
    parser.add_argument(
        "--scales",
        type=str,
        default=",".join(map(str, DEFAULT_SCALES)),
        help=f"Comma-separated LoRA scales to test (default: {','.join(map(str, DEFAULT_SCALES))})"
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default=DEFAULT_PROMPT,
        help="Generation prompt (default: suit on mannequin)"
    )

    parser.add_argument(
        "--negative",
        type=str,
        default=DEFAULT_NEGATIVE_PROMPT,
        help="Negative prompt"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed for reproducibility (default: {DEFAULT_SEED})"
    )

    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help=f"Inference steps (default: {DEFAULT_STEPS})"
    )

    parser.add_argument(
        "--guidance",
        type=float,
        default=DEFAULT_GUIDANCE,
        help=f"CFG guidance scale (default: {DEFAULT_GUIDANCE})"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )

    args = parser.parse_args()

    # Parse scales
    scales = [float(s.strip()) for s in args.scales.split(",")]

    # Setup output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Print configuration
    print("=" * 60)
    print("  LoRA Testing Script")
    print("=" * 60)
    print(f"  LoRA files:  {len(args.lora_files)} file(s)")
    print(f"  Scales:      {scales}")
    print(f"  Seed:        {args.seed}")
    print(f"  Steps:       {args.steps}")
    print(f"  Guidance:    {args.guidance}")
    print(f"  Output:      {output_dir}")
    print("=" * 60)

    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"\n[cuda] GPU: {torch.cuda.get_device_name(0)}")
        print(f"[cuda] VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("\n[warning] CUDA not available, using CPU (will be slow)")

    # Load pipeline (once, reused for all LoRAs)
    pipe = load_pipeline()

    # Test each LoRA file
    all_results = {}

    for lora_path in args.lora_files:
        print(f"\n{'=' * 60}")
        print(f"  Testing: {Path(lora_path).name}")
        print("=" * 60)

        try:
            # Load the LoRA
            adapter_name = load_lora(pipe, lora_path)

            # Test at different scales
            results = test_lora_scales(
                pipe=pipe,
                adapter_name=adapter_name,
                scales=scales,
                output_dir=output_dir,
                prompt=args.prompt,
                negative_prompt=args.negative,
                seed=args.seed,
                steps=args.steps,
                guidance=args.guidance,
            )

            all_results[adapter_name] = results

            # Unload this LoRA before testing the next one
            pipe.unload_lora_weights()
            print(f"[lora] Unloaded: {adapter_name}")

        except Exception as e:
            print(f"[error] Failed to test {lora_path}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Print summary
    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print("=" * 60)

    for adapter_name, results in all_results.items():
        print(f"\n  {adapter_name}:")
        for r in results:
            print(f"    scale={r['scale']:.2f} → {Path(r['path']).name} ({r['time']:.1f}s)")

    print(f"\n  Output directory: {output_dir}")
    print(f"\n  Tip: Compare scale=0.00 (baseline) with higher scales to see LoRA effect")
    print("=" * 60)


if __name__ == "__main__":
    main()
