# app/routers/generate.py
from fastapi import APIRouter, Request
from urllib.parse import urljoin, urlparse

from app.models.generate import GenerationRequest, GenerationResponse
from app.services.generator import MockGenerator, SdxlTurboGenerator
from app.services.storage import LocalStorage, R2Storage, Storage
from app.core.config import settings

router = APIRouter()

# --- Initialize Storage Backend based on settings ---
storage: Storage
if settings.storage_backend == "r2":
    storage = R2Storage()
    print("✅ [Storage] Using Cloudflare R2 backend.")
else:
    storage = LocalStorage()
    print("✅ [Storage] Using LocalStorage backend.")

# --- Initialize the Generator ---
USE_MOCK = False 
generator = MockGenerator(storage) if USE_MOCK else SdxlTurboGenerator(storage)


@router.post("/generate", response_model=GenerationResponse, status_code=201)
def generate(req: GenerationRequest, request: Request) -> GenerationResponse:
    resp = generator.generate(req)

    # The R2Storage class returns a full public URL, so we only need to 
    # rewrite URLs if we're using LocalStorage and PUBLIC_BASE_URL isn't set.
    if isinstance(storage, LocalStorage) and not settings.public_base_url:
        base = str(request.base_url).rstrip("/") + "/"
        for img in resp.images:
            # This logic correctly handles the relative paths from LocalStorage
            parsed = urlparse(img.url)
            path = parsed.path if parsed.scheme else img.url
            img.url = urljoin(base, path.lstrip("/"))

    return resp