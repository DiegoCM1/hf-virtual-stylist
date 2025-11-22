from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.generation import router as generation_router  # Updated: using new generation module
from app.catalog import router as catalog_router  # Updated: using new catalog module
from app.errors import add_error_handlers
import os
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.admin.fabrics import fabrics_router, colors_router  # Updated imports
from app.admin.generations import router as admin_generations_router  # Updated import




app = FastAPI(title="HF Virtual Stylist")

# make sure the folder exists before mounting
Path("storage").mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory="storage", html=False), name="files")

# Errors handler
add_error_handlers(app)


# Allowed origins
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://hf-virtual-stylist.vercel.app",
]

# Allow Vercel preview deployments
allow_origin_regex = r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fabrics_router)  # Updated
app.include_router(colors_router)  # Updated
app.include_router(admin_generations_router)

@app.get("/healthz")
def healthz():
    return {"ok": True, "version": os.getenv("APP_VERSION", "0.1.0")}

app.include_router(catalog_router, prefix="")  # Updated: using new catalog module
app.include_router(generation_router, prefix="")  # Updated: using new generation module
