# tools/make_pose_maps.py
from controlnet_aux import MidasDetector
from PIL import Image, ImageOps
from pathlib import Path

TARGET = (1344, 2016)  # tamaño final de generación

def load_and_fit(path: Path, target: tuple[int, int]) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    # Aplanar alpha sobre blanco (evita bordes raros en los detectores)
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im).convert("RGB")
    # Letterbox: preservar aspecto y rellenar a TARGET
    fitted = ImageOps.contain(im, target, Image.BICUBIC)
    canvas = Image.new("RGB", target, (255, 255, 255))
    canvas.paste(fitted, ((target[0] - fitted.width) // 2, (target[1] - fitted.height) // 2))
    return canvas

BASE = Path(__file__).resolve().parent.parent  # go up one level from /tools
SRC_DIR = BASE / "assets" / "control"
SRC_DIR.mkdir(parents=True, exist_ok=True)

NAMES = {
    "recto": "recto-maniqui.png",
    "cruzado": "cruzado-maniqui.png",
}

# Detector: Depth (MiDaS empaquetado en Annotators; público, sin token)
depth = MidasDetector.from_pretrained("lllyasviel/Annotators")


for key, fname in NAMES.items():
    src = SRC_DIR / fname
    if not src.exists():
        print(f"[skip] Falta {src}")
        continue

    im = load_and_fit(src, TARGET)

    # Depth
    depth_img = depth(im).resize(TARGET, Image.BICUBIC)
    depth_img.save(SRC_DIR / f"{key}_depth.png")

    print(f"[ok] {key} -> {SRC_DIR / f'{key}_depth.png'}")

