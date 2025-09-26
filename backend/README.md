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
export WATERMARK_PATH=/workspace/app/backend/tests/assets/logo.webp
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