"""Pydantic schemas for admin fabric management."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ColorBase(BaseModel):
    color_id: str
    name: str
    hex_value: str
    swatch_url: Optional[str] = None


class ColorCreate(ColorBase):
    pass


class ColorRead(ColorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class FabricBase(BaseModel):
    family_id: str
    display_name: str
    status: str = "active"


class FabricCreate(FabricBase):
    colors: List[ColorCreate] = Field(default_factory=list)


class FabricUpdate(BaseModel):
    family_id: Optional[str] = None
    display_name: Optional[str] = None
    status: Optional[str] = None
    colors: Optional[List[ColorCreate]] = None

    model_config = ConfigDict(extra="forbid")


class FabricRead(FabricBase):
    id: int
    colors: List[ColorRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
