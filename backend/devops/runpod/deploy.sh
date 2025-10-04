#!/usr/bin/env bash
set -euo pipefail

# --- 0) Ensure Python 3.11 venv on NV (persist across pods) -------------------
if [ ! -d /workspace/py311 ]; then
  echo "[py311] creating venv on NV"
  apt-get update -y
  DEBIAN_FRONTEND=noninteractive apt-get install -y python3.11 python3.11-venv
  python3.11 -m venv /workspace/py311 --system-site-packages
fi
source /workspace/py311/bin/activate
python -V

# --- 1) Sync repo to main -----------------------------------------------------
cd /workspace/app
export PYTHONUNBUFFERED=1
git fetch origin
git reset --hard origin/main

# --- 2) Install deps with py311 ----------------------------------------------
cd backend
python -m pip install --upgrade pip -q
python -m pip install --quiet --only-binary=:all: tokenizers==0.19.1
python -m pip install --quiet -r requirements.txt

# --- 3) Runtime envs ----------------------------------------------------------
export PYTHONPATH=/workspace/app/backend
export HF_HOME=/workspace/.cache/huggingface
export HF_HUB_ENABLE_HF_TRANSFER=1
export WATERMARK_PATH=/workspace/app/backend/tests/assets/watermark-logo.png
mkdir -p /workspace/app/db
export DATABASE_URL=sqlite:////workspace/app/db/app.db
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-change-this-now}"
export JWT_SECRET="${JWT_SECRET:-$(python - <<'PY'
import secrets; print(secrets.token_hex(32))
PY
)}"
export JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}"
# Storage
export STORAGE_BACKEND="local"        # or "r2" when you swap
export CORS_ORIGINS="*"

# --- 4) DB migrations + optional seed ----------------------------------------
set -x  # show commands in this section

# Ensure we're in backend where alembic.ini lives
cd /workspace/app/backend

# Show current SQLite tables BEFORE migration
python - <<'PY'
import sqlite3, os
db = "/workspace/app/db/app.db"
os.makedirs("/workspace/app/db", exist_ok=True)
con = sqlite3.connect(db); cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("[pre-migrate] tables:", [r[0] for r in cur.fetchall()])
con.close()
PY

# --- Force Alembic to use the SAME DB as the app ------------------------------
ALEMBIC_CONFIG="/workspace/app/backend/alembic.ini"

echo "[alembic] sqlalchemy.url before:"
grep -nE '^\s*sqlalchemy\.url' "$ALEMBIC_CONFIG" || true

# Overwrite sqlalchemy.url inside alembic.ini to match $DATABASE_URL
sed -i -E "s|^\s*sqlalchemy\.url\s*=.*$|sqlalchemy.url = ${DATABASE_URL}|" "$ALEMBIC_CONFIG"

echo "[alembic] sqlalchemy.url after:"
grep -nE '^\s*sqlalchemy\.url' "$ALEMBIC_CONFIG" || true

# Ensure metadata is loaded (models imported) so Alembic has tables
PYTHONPATH=/workspace/app/backend python - <<'PY'
from app.core.database import Base
from app.admin import models  # registers FabricFamily, Color, etc.
print("[alembic] metadata tables:", list(Base.metadata.tables.keys()))
PY

# Run Alembic (fail loud), then show status
alembic -c "$ALEMBIC_CONFIG" upgrade head
alembic -c "$ALEMBIC_CONFIG" heads
alembic -c "$ALEMBIC_CONFIG" current

# Show SQLite tables AFTER migration
python - <<'PY'
import sqlite3
db = "/workspace/app/db/app.db"
con = sqlite3.connect(db); cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("[post-migrate] tables:", [r[0] for r in cur.fetchall()])
con.close()
PY

# Optional seed (now it should work)
if [ -f /workspace/app/backend/seed.py ]; then
  echo "[seed] running seed.py"
  PYTHONPATH=/workspace/app/backend python /workspace/app/backend/seed.py
else
  echo "[seed] seed.py not found, skipping"
fi
set +x

# --- 5) Quick sanity ----------------------------------------------------------
python - <<'PY'
import torch
print(f"[sanity] torch {torch.__version__} cuda={torch.cuda.is_available()}")
from diffusers import StableDiffusionXLPipeline
print("[sanity] SDXL pipeline import OK")
PY

# --- 6) Start API -------------------------------------------------------------
pkill -f uvicorn || true
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
