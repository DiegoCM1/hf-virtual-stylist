from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Color(BaseModel):
    color_id: str
    name: str
    hex: str
    swatch_url: Optional[str] = None


class Family(BaseModel):
    family_id: str
    display_name: str
    status: Literal["active", "inactive"] = "active"
    sort: int = 0
    colors: List[Color] = Field(default_factory=list)


class CatalogResponse(BaseModel):
    families: List[Family] = Field(default_factory=list)
