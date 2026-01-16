"""Generator configuration loaded from environment variables."""
import os
from pathlib import Path

# Core generation settings
GUIDANCE = float(os.getenv("GUIDANCE", "4.3"))
MAX_CUTS = int(os.getenv("MAX_CUTS", "2"))
USE_REFINER = os.getenv("USE_REFINER", "1") == "1"
TOTAL_STEPS = int(os.getenv("TOTAL_STEPS", "80"))
REFINER_SPLIT = float(os.getenv("REFINER_SPLIT", "0.70"))

# Primary ControlNet (DEPTH)
# CRITICAL: Read directly from os.getenv() instead of importing from config.py
# This allows quick_gen.py overrides to work correctly after module reload
CONTROLNET_ENABLED = os.getenv("CONTROLNET_ENABLED", "0") == "1"
CONTROLNET_MODEL = os.getenv("CONTROLNET_MODEL", "")
CONTROLNET_WEIGHT = float(os.getenv("CONTROLNET_WEIGHT", "0.9"))
CONTROLNET_GUIDANCE_START = float(os.getenv("CONTROLNET_GUIDANCE_START", "0.0"))
CONTROLNET_GUIDANCE_END = float(os.getenv("CONTROLNET_GUIDANCE_END", "0.5"))
CONTROL_IMAGE_RECTO = os.getenv("CONTROL_IMAGE_RECTO", "")
CONTROL_IMAGE_CRUZADO = os.getenv("CONTROL_IMAGE_CRUZADO", "")

# Second ControlNet (CANNY)
CONTROLNET2_ENABLED = os.getenv("CONTROLNET2_ENABLED", "0") == "1"
CONTROLNET2_MODEL = os.getenv("CONTROLNET2_MODEL", "")
CONTROLNET2_WEIGHT = float(os.getenv("CONTROLNET2_WEIGHT", "0.65"))
CONTROLNET2_GUIDANCE_START = float(os.getenv("CONTROLNET2_GUIDANCE_START", "0.05"))
CONTROLNET2_GUIDANCE_END = float(os.getenv("CONTROLNET2_GUIDANCE_END", "0.88"))
CONTROL_IMAGE_RECTO_CANNY = os.getenv("CONTROL_IMAGE_RECTO_CANNY", "")
CONTROL_IMAGE_CRUZADO_CANNY = os.getenv("CONTROL_IMAGE_CRUZADO_CANNY", "")

# IP-Adapter (image prompt)
IP_ADAPTER_ENABLED = os.getenv("IP_ADAPTER_ENABLED", "0") == "1"
IP_ADAPTER_REPO = os.getenv("IP_ADAPTER_REPO", "h94/IP-Adapter")
IP_ADAPTER_SUBFOLDER = os.getenv("IP_ADAPTER_SUBFOLDER", "sdxl_models")
IP_ADAPTER_WEIGHT = os.getenv("IP_ADAPTER_WEIGHT", "ip-adapter_sdxl.bin")
IP_ADAPTER_SCALE = float(os.getenv("IP_ADAPTER_SCALE", "0.70"))
IP_ADAPTER_IMAGE = os.getenv("IP_ADAPTER_IMAGE", "")  # leave empty to skip

# DEBUG: Log values read from env vars at module load/reload time
print(f"[DEBUG generator_config.py MODULE LOAD] Configuration loaded from environment:")
print(f"  GUIDANCE = {GUIDANCE}")
print(f"  TOTAL_STEPS = {TOTAL_STEPS}")
print(f"  USE_REFINER = {USE_REFINER}")
print(f"  REFINER_SPLIT = {REFINER_SPLIT}")
print(f"  CONTROLNET_ENABLED = {CONTROLNET_ENABLED}")
print(f"  CONTROLNET_WEIGHT = {CONTROLNET_WEIGHT}")
print(f"  CONTROLNET_GUIDANCE_START = {CONTROLNET_GUIDANCE_START}")
print(f"  CONTROLNET_GUIDANCE_END = {CONTROLNET_GUIDANCE_END}")
print(f"  CONTROLNET2_ENABLED = {CONTROLNET2_ENABLED}")
print(f"  CONTROLNET2_WEIGHT = {CONTROLNET2_WEIGHT}")
print(f"  CONTROLNET2_GUIDANCE_START = {CONTROLNET2_GUIDANCE_START}")
print(f"  CONTROLNET2_GUIDANCE_END = {CONTROLNET2_GUIDANCE_END}")
print(f"  IP_ADAPTER_ENABLED = {IP_ADAPTER_ENABLED}")
print(f"  IP_ADAPTER_SCALE = {IP_ADAPTER_SCALE}")


def resolve_watermark_path() -> str:
    """Resolve watermark image path from environment or defaults."""
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


WATERMARK_PATH = resolve_watermark_path()
