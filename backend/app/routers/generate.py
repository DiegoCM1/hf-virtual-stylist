from fastapi import APIRouter
from app.models.generate import GenerationRequest, GenerationResponse
from app.services.generator import MockGenerator, SdxlTurboGenerator
from app.services.storage import LocalStorage


router = APIRouter()
USE_MOCK = False
storage = LocalStorage()  # or R2/S3 later
generator = MockGenerator(storage) if USE_MOCK else SdxlTurboGenerator(storage)

@router.post("/generate", response_model=GenerationResponse, status_code=201)
def generate(req: GenerationRequest) -> GenerationResponse:
    return generator.generate(req)