from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict

Cut = Literal["recto", "cruzado"]

class GenerationRequest(BaseModel):
    family_id: str
    color_id: str
    cuts: List[Cut] = Field(default_factory=lambda: ["recto", "cruzado"])
    seed: Optional[int] = None
    quality: Literal["preview", "final"] = "final"


class ImageResult(BaseModel):
    cut: Cut
    url: str
    width: int
    height: int
    watermark: bool = True
    meta: Dict[str, str] = Field(default_factory=dict)


class GenerationResponse(BaseModel):
    request_id: str
    status: Literal["completed","pending","failed"]
    images: List[ImageResult] = Field(default_factory=list)
    duration_ms: Optional[int] = None
    meta: Dict[str, str] = Field(default_factory=dict)