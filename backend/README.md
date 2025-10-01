# Start image creation
## call once and store JSON
curl -s http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"HF-001","color_id":"Navy","cuts":["recto","cruzado"],"quality":"preview"}' > out.json

## extract recto
jq -r '.images[0].url' out.json | sed 's|^data:image/png;base64,||' | base64 -d > recto.png
## extract cruzado
jq -r '.images[1].url' out.json | sed 's|^data:image/png;base64,||' | base64 -d > cruzado.png


<!-- TESTS -->

## Testing in general
pytest -q

### Health
curl -s http://127.0.0.1:8000/healthz

Expect: {"ok":true,...}

### Generate
curl -s -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"lana-normal","color_id":"green-001"}'

Expect: images[0].url and images[1].url HTTP URLs under /files/generated/...

- URLs load (HEAD check)
```
URL1="<<paste images[0].url>>"
URL2="<<paste images[1].url>>"
curl -I "$URL1"
curl -I "$URL2"
```



<!-- Run backend -->
uvicorn app.main:app --reload --port 8000





## POD
### Sync POD - One command
Created a quick deploy script in the pod so syncing is one command:

cat > /workspace/deploy.sh <<'SH'
set -e
cd /workspace/app
export PYTHONUNBUFFERED=1
git fetch origin
git reset --hard origin/main
cd backend
pip install -r requirements.txt -q
export PYTHONPATH=/workspace/app/backend
export HF_HOME=/workspace/.cache/huggingface
export HF_HUB_ENABLE_HF_TRANSFER=1
export WATERMARK_PATH=/workspace/app/backend/tests/assets/watermark-logo.png
python - <<'PY'
import torch, torchvision
print("[sanity] torch", torch.__version__, "torchvision", torchvision.__version__)
from transformers import CLIPImageProcessor; print("[sanity] CLIPImageProcessor OK")
from diffusers import StableDiffusionXLPipeline; print("[sanity] SDXL pipeline import OK")
PY
pkill -f uvicorn || true
uvicorn app.main:app --host 0.0.0.0 --port 8000
SH
chmod +x /workspace/deploy.sh


Whenever you push from your laptop, on the pod just run:

/workspace/deploy.sh


### Testing Pod
curl -s -X POST "https://lnqrev4dnktv7s-8000.proxy.runpod.net/generate" \
  -H "Content-Type: application/json" \
  -d '{"family_id":"lana-normal","color_id":"green-001","cuts":["recto"]}'

---

## Service Blueprint

### Project Layout

```
backend/
├── app/
│   ├── main.py                # FastAPI app factory & CORS/static config
│   ├── routers/               # HTTP routers (catalog, generate, admin)
│   ├── models/                # Pydantic request/response contracts
│   ├── services/              # Catalog lookup, storage, generator, watermark
│   ├── core/                  # Settings, database, logging primitives
│   └── admin/                 # Admin fabric management endpoints
├── tests/                     # pytest suite and fixtures
├── requirements.txt           # Runtime dependencies
└── seed.py                    # Example data seeding script
```

### Runtime Flow

1. **Request:** The frontend submits a `POST /generate` payload shaped like `GenerationRequest` (see below).
2. **Routing:** `app/routers/generate.py` picks the generator implementation (`MockGenerator` by default) and delegates the call.
3. **Generation:**
   - `MockGenerator` creates placeholder JPEGs and watermarks them.
   - `SdxlTurboGenerator` lazily loads `StableDiffusionXLPipeline`, runs inference, applies a watermark, and returns metadata including seeds and inference timing.
4. **Storage:** `LocalStorage.save_bytes` (configurable) writes to `storage/generated/...` and returns a URL served under `/files`.
5. **Response:** The endpoint returns a `GenerationResponse` with IDs, duration, and URLs. Errors propagate through `app/errors.py`, which maps exceptions to JSON responses.

Static assets are mounted through `FastAPIStaticFiles` in `app/main.py`, making every generated file available as soon as it is written.

---

## API Contracts

### `POST /generate`

```jsonc
{
  "family_id": "lana-normal",        // required: fabric collection code
  "color_id": "green-001",           // required: color variant id
  "cuts": ["recto", "cruzado"],      // optional: defaults to both poses
  "quality": "preview",              // optional: influences inference params
  "seed": 123456789                   // optional: deterministic generation
}
```

Response (`201 Created`):

```jsonc
{
  "request_id": "a1b2c3d4e5",
  "status": "completed",
  "duration_ms": 42857,
  "images": [
    {
      "cut": "recto",
      "url": "http://localhost:8000/files/generated/.../recto.jpg",
      "width": 1024,
      "height": 1536,
      "watermark": true,
      "meta": {
        "seed": "123456789",
        "steps": "28",
        "guidance": "5.5",
        "engine": "sdxl-base"
      }
    }
  ],
  "meta": {
    "family_id": "lana-normal",
    "color_id": "green-001",
    "device": "cuda"
  }
}
```

### `GET /catalog/fabrics`

Returns the structured catalog consumed by the UI, sourced from `app/services/catalog.py`. Each fabric family includes a list of colors and metadata describing seasonality, swatch URLs, and availability flags.

### `GET /healthz`

Lightweight heartbeat endpoint that returns `{ "ok": true, "version": "…" }`. Useful for load balancer checks and local validation.

---

## Configuration & Environment Variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `APP_VERSION` | Exposed via `/healthz` for release tracking. | `0.1.0` |
| `WATERMARK_PATH` | Path to the watermark image consumed by `apply_watermark_image`. | `tests/assets/watermark-logo.png` |
| `HF_HOME` | Hugging Face cache location for SDXL weights. | `$HOME/.cache/huggingface` |
| `HF_HUB_ENABLE_HF_TRANSFER` | Enables accelerated downloads when set to `1`. | unset |
| `USE_MOCK` | Toggle between mock generator and SDXL. Set in `routers/generate.py`. | `False` |

> For cloud storage, implement a new `Storage` subclass (e.g., S3) and inject it into `SdxlTurboGenerator` in `routers/generate.py`.

---

## Testing & Quality Gates

- `pytest -q` exercises unit tests under `backend/tests`, including watermarking and API contract validations.
- `curl` commands listed above are ideal for manual smoke testing or scripting.
- To profile SDXL inference, export `HF_HOME` and monitor logs emitted by `SdxlTurboGenerator` (seed, duration, device).

---

## Extending the Backend

1. **Add a new endpoint:** Create a module in `app/routers`, wire it in `app/main.py`, and document the schema under `app/models`.
2. **Swap storage providers:** Implement `Storage.save_bytes` and `Storage.save_file` interfaces (see `app/services/storage.py`). Update the router to use the new provider.
3. **Customize prompts:** Modify `base_prompt` and `prompts` within `SdxlTurboGenerator`. Keep the negative prompt aligned with brand guidelines.
4. **Persist metadata:** Integrate a database by leveraging `app/core/database.py` and `alembic/` migrations to store run history or catalog state.