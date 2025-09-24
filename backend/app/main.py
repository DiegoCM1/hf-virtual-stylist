from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import catalog, generate
from app.errors import add_error_handlers
import os

app = FastAPI(title="HF Virtual Stylist")

# Errors handler
add_error_handlers(app)


# CORS: allow your frontend during dev (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"ok": True, "version": os.getenv("APP_VERSION", "0.1.0")}

app.include_router(catalog.router, prefix="")
app.include_router(generate.router, prefix="")
