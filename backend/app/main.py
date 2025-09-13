from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import catalog, generate

app = FastAPI(title="HF Virtual Stylist")

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
    return {"ok": True}

app.include_router(catalog.router, prefix="")
app.include_router(generate.router, prefix="")
