"""Pydantic schemas for fabric and color management."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ColorBase(BaseModel):
    color_id: str
    name: str
    hex_value: str
    swatch_code: Optional[str] = None  # R2 swatch filename
    swatch_url: Optional[str] = None
    status: str = "active"


class ColorCreate(ColorBase):
    pass


class ColorUpdate(BaseModel):
    color_id: Optional[str] = None
    name: Optional[str] = None
    hex_value: Optional[str] = None
    swatch_code: Optional[str] = None
    swatch_url: Optional[str] = None
    status: Optional[str] = None
    fabric_family_id: Optional[int] = None  # For moving colors between families

    model_config = ConfigDict(extra="forbid")


class ColorRead(ColorBase):
    id: int
    fabric_family_id: int
    created_at: datetime
    updated_at: datetime

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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusUpdate(BaseModel):
    """Schema for status toggle endpoints."""
    status: str = Field(..., pattern="^(active|inactive)$")
