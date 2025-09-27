from fastapi import APIRouter, Request
from app.models.generate import GenerationRequest, GenerationResponse
from app.services.generator import MockGenerator, SdxlTurboGenerator
from app.services.storage import LocalStorage
from urllib.parse import urljoin, urlparse
from app.core.config import PUBLIC_BASE_URL


router = APIRouter()
USE_MOCK = False
storage = LocalStorage()  # or R2/S3 later
generator = MockGenerator(storage) if USE_MOCK else SdxlTurboGenerator(storage)

@router.post("/generate", response_model=GenerationResponse, status_code=201)
def generate(req: GenerationRequest, request: Request) -> GenerationResponse:
    resp = generator.generate(req)

    # Fallback: if PUBLIC_BASE_URL is not defined, rewrite using the caller's base_url
    if not PUBLIC_BASE_URL:
        base = str(request.base_url).rstrip("/") + "/"
        for img in resp.images:
            parsed = urlparse(img.url)
            # if storage returned absolute (e.g., localhost) keep the path only; if relative, use as-is
            path = parsed.path if parsed.scheme else img.url
            img.url = urljoin(base, path.lstrip("/"))

    return resp