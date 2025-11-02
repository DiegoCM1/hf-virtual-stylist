#!/usr/bin/env python3
"""
Quick Generation Script for Rapid SDXL Parameter Testing

Usage:
    # Single test with preset
    python -m app.scripts.quick_gen --preset=aggressive-depth --fabric=algodon-tech --color=negro-001

    # Compare multiple presets
    python -m app.scripts.quick_gen --compare baseline,aggressive-depth,ultra-fast --fabric=algodon-tech

    # Override specific parameters
    python -m app.scripts.quick_gen --preset=baseline --override guidance=6.0,steps=100

    # Custom seed
    python -m app.scripts.quick_gen --preset=baseline --fabric=algodon-tech --color=negro-001 --seed=42

Speed: ~8-10s first run (model loading), ~2-3s subsequent runs (models cached in RAM)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Defer heavy imports until needed (torch/diffusers dependencies)
# from app.services.generator import SdxlTurboGenerator
# from app.models.generate import GenerationRequest
# from app.services.storage import LocalStorage


# Paths
SCRIPT_DIR = Path(__file__).parent
DEFAULTS_JSON = SCRIPT_DIR / "quick_defaults.json"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"


def load_presets() -> Dict[str, Dict[str, Any]]:
    """Load preset configurations from quick_defaults.json"""
    if not DEFAULTS_JSON.exists():
        print(f"[!] Error: {DEFAULTS_JSON} not found")
        sys.exit(1)

    with open(DEFAULTS_JSON, 'r') as f:
        return json.load(f)


def apply_overrides(preset: Dict[str, Any], override_str: str) -> Dict[str, Any]:
    """
    Apply CLI overrides to preset config

    Example: "guidance=6.0,steps=100" → {"guidance": 6.0, "total_steps": 100}
    """
    preset = preset.copy()

    for override in override_str.split(','):
        if '=' not in override:
            print(f"[!] Warning: Invalid override format '{override}' (expected key=value)")
            continue

        key, value = override.split('=', 1)
        key = key.strip()
        value = value.strip()

        # Map short names to full config keys
        key_mappings = {
            'guidance': 'guidance',
            'steps': 'total_steps',
            'refiner': 'use_refiner',
            'refiner_split': 'refiner_split',
            'depth_weight': 'controlnet_weight',
            'canny_weight': 'controlnet2_weight',
            'ip_adapter': 'ip_adapter_enabled',
            'ip_scale': 'ip_adapter_scale',
        }

        full_key = key_mappings.get(key, key)

        # Type conversion
        if full_key in ['use_refiner', 'controlnet_enabled', 'controlnet2_enabled', 'ip_adapter_enabled']:
            value = value.lower() in ['1', 'true', 'yes']
        elif full_key == 'total_steps':
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string

        preset[full_key] = value
        print(f"   Override: {full_key} = {value}")

    return preset


def apply_preset_to_env(preset: Dict[str, Any]):
    """
    Apply preset config to environment variables that generator reads
    """
    env_mappings = {
        'guidance': 'GUIDANCE',
        'total_steps': 'TOTAL_STEPS',
        'use_refiner': 'USE_REFINER',
        'refiner_split': 'REFINER_SPLIT',
        'controlnet_enabled': 'CONTROLNET_ENABLED',
        'controlnet_weight': 'CONTROLNET_WEIGHT',
        'controlnet_guidance_start': 'CONTROLNET_GUIDANCE_START',
        'controlnet_guidance_end': 'CONTROLNET_GUIDANCE_END',
        'controlnet2_enabled': 'CONTROLNET2_ENABLED',
        'controlnet2_weight': 'CONTROLNET2_WEIGHT',
        'controlnet2_guidance_start': 'CONTROLNET2_GUIDANCE_START',
        'controlnet2_guidance_end': 'CONTROLNET2_GUIDANCE_END',
        'ip_adapter_enabled': 'IP_ADAPTER_ENABLED',
        'ip_adapter_scale': 'IP_ADAPTER_SCALE',
    }

    for preset_key, env_var in env_mappings.items():
        if preset_key in preset:
            value = preset[preset_key]
            # Convert booleans to "1" or "0" for env vars
            if isinstance(value, bool):
                value = "1" if value else "0"
            os.environ[env_var] = str(value)


def generate_with_preset(
    preset_name: str,
    preset_config: Dict[str, Any],
    fabric_id: str,
    color_id: str,
    cuts: List[str],
    seed: int,
    storage,  # LocalStorage - type hint removed to avoid import at module level
) -> Dict[str, Any]:
    """
    Generate images using specified preset configuration

    Returns dict with timing stats and output paths
    """
    # Import heavy dependencies only when generating
    from app.services.generator import SdxlTurboGenerator
    from app.models.generate import GenerationRequest

    print(f"\n{'='*80}")
    print(f"[Preset] {preset_name}")
    print(f"   {preset_config.get('description', 'No description')}")
    print(f"{'='*80}")

    # Apply preset to environment variables
    apply_preset_to_env(preset_config)

    # CRITICAL FIX: Reload generator module to pick up env var changes
    # Generator reads env vars directly via os.getenv() at module load time
    # Reloading the module re-executes those lines with new env values
    import importlib
    import torch
    import gc
    from app.services import generator as gen_module

    # Clear the class-level singletons BEFORE reload
    if hasattr(gen_module, 'SdxlTurboGenerator'):
        gen_module.SdxlTurboGenerator._base = None
        gen_module.SdxlTurboGenerator._refiner = None
        gen_module.SdxlTurboGenerator._device = "cpu"

    # Clear CUDA cache aggressively
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()  # Wait for all GPU operations to finish
        torch.cuda.ipc_collect()  # Clean up inter-process communication
    gc.collect()

    print(f"[DEBUG quick_gen] After clearing cache, env vars are:")
    print(f"  CONTROLNET_WEIGHT={os.environ.get('CONTROLNET_WEIGHT', 'NOT SET')}")
    print(f"  CONTROLNET2_WEIGHT={os.environ.get('CONTROLNET2_WEIGHT', 'NOT SET')}")

    # Reload generator module (re-executes os.getenv() calls with new env values)
    importlib.reload(gen_module)
    from app.services.generator import SdxlTurboGenerator

    # Create generation request
    request = GenerationRequest(
        family_id=fabric_id,
        color_id=color_id,
        cuts=cuts,
        seed=seed
    )

    # Generate
    print(f"\n[*] Starting generation...")
    print(f"   Fabric: {fabric_id}")
    print(f"   Color: {color_id}")
    print(f"   Cuts: {', '.join(cuts)}")
    print(f"   Seed: {seed}")
    print(f"\n   Parameters:")
    print(f"   - Steps: {preset_config.get('total_steps', 80)}")
    print(f"   - Guidance: {preset_config.get('guidance', 4.3)}")
    print(f"   - Refiner: {'Yes' if preset_config.get('use_refiner', True) else 'No'}")
    if preset_config.get('use_refiner', True):
        print(f"   - Refiner split: {preset_config.get('refiner_split', 0.7)}")
    print(f"   - Depth ControlNet: {'Yes' if preset_config.get('controlnet_enabled', True) else 'No'}")
    if preset_config.get('controlnet_enabled', True):
        print(f"     Weight: {preset_config.get('controlnet_weight', 0.9)}")
    print(f"   - Canny ControlNet: {'Yes' if preset_config.get('controlnet2_enabled', False) else 'No'}")
    if preset_config.get('controlnet2_enabled', False):
        print(f"     Weight: {preset_config.get('controlnet2_weight', 0.65)}")
    print(f"   - IP-Adapter: {'Yes' if preset_config.get('ip_adapter_enabled', False) else 'No'}")
    if preset_config.get('ip_adapter_enabled', False):
        print(f"     Scale: {preset_config.get('ip_adapter_scale', 0.7)}")

    start_time = time.time()

    try:
        generator = SdxlTurboGenerator(storage=storage)
        response = generator.generate(request)

        elapsed = time.time() - start_time

        print(f"\n[OK] Generation complete in {elapsed:.2f}s")
        print(f"   Images generated: {len(response.images)}")

        # Print output paths
        for img in response.images:
            print(f"   - {img.cut}: {img.url}")

        return {
            'preset_name': preset_name,
            'elapsed_time': elapsed,
            'images': response.images,
            'config': preset_config
        }

    except Exception as e:
        print(f"\n[!] Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return {
            'preset_name': preset_name,
            'error': str(e),
            'config': preset_config
        }


def main():
    parser = argparse.ArgumentParser(
        description="Quick SDXL generation for rapid parameter testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--preset',
        type=str,
        help='Preset name from quick_defaults.json (e.g., baseline, aggressive-depth)'
    )

    parser.add_argument(
        '--compare',
        type=str,
        help='Comma-separated list of presets to compare (e.g., baseline,ultra-fast,high-cfg)'
    )

    parser.add_argument(
        '--override',
        type=str,
        help='Override preset params (e.g., guidance=6.0,steps=100)'
    )

    parser.add_argument(
        '--fabric',
        type=str,
        default='algodon-tech',
        help='Fabric family ID (default: algodon-tech)'
    )

    parser.add_argument(
        '--color',
        type=str,
        default='negro-001',
        help='Color ID (default: negro-001)'
    )

    parser.add_argument(
        '--cuts',
        type=str,
        default='recto,cruzado',
        help='Comma-separated cut names (default: recto,cruzado)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed (default: random)'
    )

    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='List available presets and exit'
    )

    parser.add_argument(
        '--no-reload',
        action='store_true',
        help='Skip model reload (faster but ignores env var changes - use only when testing different seeds with same config)'
    )

    args = parser.parse_args()

    # Load presets
    presets = load_presets()

    # List presets if requested
    if args.list_presets:
        print("\n[Available Presets]\n")
        for name, config in presets.items():
            desc = config.get('description', 'No description')
            print(f"  {name:20} - {desc}")
        print()
        sys.exit(0)

    # Validate arguments
    if not args.preset and not args.compare:
        print("[!] Error: Must specify either --preset or --compare")
        parser.print_help()
        sys.exit(1)

    # Determine which presets to test
    if args.compare:
        preset_names = [p.strip() for p in args.compare.split(',')]
    else:
        preset_names = [args.preset]

    # Validate preset names
    for name in preset_names:
        if name not in presets:
            print(f"[!] Error: Preset '{name}' not found in {DEFAULTS_JSON}")
            print(f"   Available presets: {', '.join(presets.keys())}")
            sys.exit(1)

    # Prepare
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Import storage only when actually generating
    from app.services.storage import LocalStorage
    storage = LocalStorage(base_dir=str(OUTPUT_DIR), base_url="file://")

    cuts = [c.strip() for c in args.cuts.split(',')]
    seed = args.seed if args.seed is not None else int(time.time())

    # Run generation for each preset
    results = []

    total_start = time.time()

    for preset_name in preset_names:
        preset_config = presets[preset_name].copy()

        # Apply overrides if specified
        if args.override:
            preset_config = apply_overrides(preset_config, args.override)

        # Generate
        result = generate_with_preset(
            preset_name=preset_name,
            preset_config=preset_config,
            fabric_id=args.fabric,
            color_id=args.color,
            cuts=cuts,
            seed=seed,
            storage=storage
        )

        results.append(result)

    total_elapsed = time.time() - total_start

    # Print summary
    print(f"\n{'='*80}")
    print(f"[Summary]")
    print(f"{'='*80}")
    print(f"Total time: {total_elapsed:.2f}s")
    print(f"Presets tested: {len(results)}")
    print()

    for result in results:
        if 'error' in result:
            print(f"[FAIL] {result['preset_name']}: ERROR - {result['error']}")
        else:
            print(f"[OK] {result['preset_name']}: {result['elapsed_time']:.2f}s - {len(result.get('images', []))} images")

    print()
    print(f"Output directory: {OUTPUT_DIR}")
    print()


if __name__ == '__main__':
    main()
