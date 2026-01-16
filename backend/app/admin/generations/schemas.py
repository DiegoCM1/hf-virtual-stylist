"""Pydantic schemas for generation job management."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class GenerationJobRead(BaseModel):
    id: int
    job_id: str
    status: str
    family_id: str
    color_id: str
    cuts: List[str]
    seed: Optional[int] = None
    result_urls: Optional[List[str]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
