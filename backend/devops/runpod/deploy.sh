#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# HF Virtual Stylist - RunPod GPU Worker
# =============================================================================
# This script runs the worker that processes generation jobs from Railway's DB.
# It does NOT start a web server - Railway handles the API.
# =============================================================================

echo "========================================"
echo "  HF Virtual Stylist - GPU Worker"
echo "========================================"

# --- 0) Ensure Python 3.11 venv (persist across pod restarts) ----------------
if [ ! -d /workspace/py311 ]; then
  echo "[setup] Creating Python 3.11 venv..."
  apt-get update -y
  DEBIAN_FRONTEND=noninteractive apt-get install -y python3.11 python3.11-venv
  python3.11 -m venv /workspace/py311 --system-site-packages
fi
source /workspace/py311/bin/activate
echo "[setup] Python version: $(python -V)"

# --- 1) Sync repo to main ----------------------------------------------------
cd /workspace/app
export PYTHONUNBUFFERED=1
git fetch origin
git reset --hard origin/main
echo "[setup] Synced to origin/main"

# --- 2) Install dependencies -------------------------------------------------
cd backend
python -m pip install --upgrade pip -q
python -m pip install --quiet --only-binary=:all: tokenizers==0.19.1
python -m pip install --quiet -r requirements.txt
echo "[setup] Dependencies installed"

# --- 3) Environment Variables ------------------------------------------------
export PYTHONPATH=/workspace/app/backend
export HF_HOME=/workspace/.cache/huggingface
export HF_HUB_ENABLE_HF_TRANSFER=1

# =============================================================================
# DATABASE - Connect to Railway's PostgreSQL (NOT local SQLite)
# =============================================================================
# Set this in RunPod's environment variables or secrets:
#   DATABASE_URL=postgresql://user:pass@host:5432/dbname
if [ -z "${DATABASE_URL:-}" ]; then
  echo "[ERROR] DATABASE_URL not set. Configure it in RunPod environment variables."
  echo "        Get the connection string from Railway dashboard."
  exit 1
fi
echo "[config] DATABASE_URL is set (connecting to Railway PostgreSQL)"

# =============================================================================
# STORAGE - Cloudflare R2
# =============================================================================
export STORAGE_BACKEND="r2"
# Required R2 env vars (set in RunPod):
#   R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL
if [ -z "${R2_ACCESS_KEY_ID:-}" ]; then
  echo "[WARNING] R2 credentials not set. Storage may fail."
fi

# =============================================================================
# SDXL Generation Settings
# =============================================================================
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Quality settings
export GUIDANCE="${GUIDANCE:-4.3}"
export TOTAL_STEPS="${TOTAL_STEPS:-80}"
export USE_REFINER="${USE_REFINER:-1}"
export REFINER_SPLIT="${REFINER_SPLIT:-0.70}"

# ControlNet #1 (Depth)
export CONTROLNET_ENABLED="${CONTROLNET_ENABLED:-1}"
export CONTROLNET_MODEL="${CONTROLNET_MODEL:-diffusers/controlnet-depth-sdxl-1.0}"
export CONTROLNET_WEIGHT="${CONTROLNET_WEIGHT:-0.90}"
export CONTROLNET_GUIDANCE_START="${CONTROLNET_GUIDANCE_START:-0.0}"
export CONTROLNET_GUIDANCE_END="${CONTROLNET_GUIDANCE_END:-0.50}"

# ControlNet #2 (Canny)
export CONTROLNET2_ENABLED="${CONTROLNET2_ENABLED:-1}"
export CONTROLNET2_MODEL="${CONTROLNET2_MODEL:-diffusers/controlnet-canny-sdxl-1.0}"
export CONTROLNET2_WEIGHT="${CONTROLNET2_WEIGHT:-0.65}"
export CONTROLNET2_GUIDANCE_START="${CONTROLNET2_GUIDANCE_START:-0.05}"
export CONTROLNET2_GUIDANCE_END="${CONTROLNET2_GUIDANCE_END:-0.88}"

# Control images (pose references)
export CONTROL_IMAGE_RECTO="${CONTROL_IMAGE_RECTO:-/workspace/app/backend/assets/control/recto_depth.png}"
export CONTROL_IMAGE_CRUZADO="${CONTROL_IMAGE_CRUZADO:-/workspace/app/backend/assets/control/cruzado_depth.png}"
export CONTROL_IMAGE_RECTO_CANNY="${CONTROL_IMAGE_RECTO_CANNY:-/workspace/app/backend/assets/control/recto_canny.png}"
export CONTROL_IMAGE_CRUZADO_CANNY="${CONTROL_IMAGE_CRUZADO_CANNY:-/workspace/app/backend/assets/control/cruzado_canny.png}"

# IP-Adapter (fabric texture transfer) - ENABLED for swatch support
export IP_ADAPTER_ENABLED="${IP_ADAPTER_ENABLED:-1}"
export IP_ADAPTER_REPO="${IP_ADAPTER_REPO:-h94/IP-Adapter}"
export IP_ADAPTER_SUBFOLDER="${IP_ADAPTER_SUBFOLDER:-sdxl_models}"
export IP_ADAPTER_WEIGHT="${IP_ADAPTER_WEIGHT:-ip-adapter_sdxl.bin}"
export IP_ADAPTER_SCALE="${IP_ADAPTER_SCALE:-0.70}"

# Watermark
export WATERMARK_PATH="${WATERMARK_PATH:-/workspace/app/backend/assets/watermark.png}"

# =============================================================================
# Sanity Checks
# =============================================================================
echo "[sanity] Checking CUDA and SDXL..."
python - <<'PY'
import torch
print(f"  torch {torch.__version__}")
print(f"  CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
from diffusers import StableDiffusionXLPipeline
print("  SDXL pipeline import: OK")
PY

echo "[sanity] Testing database connection..."
python - <<'PY'
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.environ["DATABASE_URL"])
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("  PostgreSQL connection: OK")
PY

# =============================================================================
# Start Worker (NOT uvicorn - Railway handles the API)
# =============================================================================
echo "========================================"
echo "  Starting GPU Worker..."
echo "  Polling for jobs from Railway DB"
echo "========================================"

cd /workspace/app/backend
exec python worker.py
