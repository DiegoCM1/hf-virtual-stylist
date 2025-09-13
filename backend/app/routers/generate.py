from fastapi import APIRouter
from app.models.generate import GenerationRequest, GenerationResponse
from app.services.generator import MockGenerator, Generator

router = APIRouter()
GEN: Generator = MockGenerator() # swap to SDXL later

@router.post("/generate", response_model=GenerationResponse)
def generate(req: GenerationRequest):
    return GEN.generate(req)