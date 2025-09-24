from fastapi import APIRouter
from app.models.generate import GenerationRequest, GenerationResponse
from app.services.generator import MockGenerator, SdxlTurboGenerator


router = APIRouter()
USE_MOCK = False
generator = MockGenerator() if USE_MOCK else SdxlTurboGenerator()

@router.post("/generate", response_model=GenerationResponse, status_code=201)
def generate(req: GenerationRequest) -> GenerationResponse:
    return generator.generate(req)