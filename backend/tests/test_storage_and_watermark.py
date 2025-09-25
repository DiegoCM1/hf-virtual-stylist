import io, requests
from PIL import Image
from app.services.storage import LocalStorage
from app.services.watermark import apply_watermark_image

def test_save_bytes_local_serves_url():
    storage = LocalStorage(base_dir="storage", base_url="http://127.0.0.1:8000/files")
    img = Image.new("RGB", (400, 300), "#888B8D")
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85)
    url = storage.save_bytes(buf.getvalue(), "generated/test/test.jpg")
    assert url.startswith("http://127.0.0.1:8000/files/")
    # requires server running:
    r = requests.get(url, timeout=5)
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("image/")

def test_watermark_changes_bytes():
    img = Image.new("RGB", (400, 300), "#888B8D")
    raw = io.BytesIO(); img.save(raw, format="JPEG", quality=85)
    wm = apply_watermark_image(raw.getvalue(), "tests/assets/logo.webp", scale=0.2)
    assert isinstance(wm, (bytes, bytearray))
    # watermark should change content length
    assert len(wm) != len(raw.getvalue())
