# tools/make_pose_maps.py
from controlnet_aux import MidasDetector, CannyDetector
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

# Detectores:
#   - Depth (MiDaS en Annotators; público, sin token)
#   - Canny (bordes finos para botones/costuras)
depth = MidasDetector.from_pretrained("lllyasviel/Annotators")
canny = CannyDetector()


for key, fname in NAMES.items():
    src = SRC_DIR / fname
    if not src.exists():
        print(f"[skip] Falta {src}")
        continue

    im = load_and_fit(src, TARGET)

    # Depth
    depth_img = depth(im).resize(TARGET, Image.BICUBIC)
    depth_img.save(SRC_DIR / f"{key}_depth.png")

    # Canny (umbrales bajos para capturar botones/placket)
    # Rango típico 50–200; ajusta si ves demasiadas/pocas líneas.
    canny_img = canny(im, low_threshold=80, high_threshold=180).resize(TARGET, Image.BICUBIC)
    canny_img.save(SRC_DIR / f"{key}_canny.png")

    print(f"[ok] {key} -> depth:{SRC_DIR / f'{key}_depth.png'}  canny:{SRC_DIR / f'{key}_canny.png'}")

