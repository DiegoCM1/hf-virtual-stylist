# make_pose_maps.py
from controlnet_aux import OpenposeDetector
from PIL import Image
from pathlib import Path

detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")

BASE = Path(__file__).resolve().parent
SRC_DIR = BASE / "assets" / "control"
SRC_DIR.mkdir(parents=True, exist_ok=True)

TARGET = (1344, 2016)  # your generation size

for name in ["recto", "cruzado"]:
    src = SRC_DIR / f"{name}.jpg"
    if not src.exists():
        print(f"Missing {src}, skip.")
        continue
    im = Image.open(src).convert("RGB").resize(TARGET, Image.BICUBIC)

    # include face + hands landmarks
    pose = detector(
        im,
        include_face=True,
        include_hand=True,
    )

    out = SRC_DIR / f"{name}_openpose.png"
    pose = pose.resize(TARGET, Image.NEAREST)
    pose.save(out)
    print(f"[done] {out}")
