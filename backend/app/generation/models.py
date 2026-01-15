"""Database models for generation jobs."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSON

from app.core.database import Base


class GenerationJob(Base):
    """Represents a background job for generating suit visualizations."""

    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, nullable=False, index=True)  # UUID for API
    status = Column(String, nullable=False, default="pending", index=True)  # pending, processing, completed, failed

    # Request parameters
    family_id = Column(String, nullable=False)
    color_id = Column(String, nullable=False)
    cuts = Column(JSON, nullable=False)  # ["recto", "cruzado"]
    seed = Column(Integer, nullable=True)
    swatch_url = Column(String, nullable=True)  # URL to fabric swatch for IP-Adapter

    # Results
    result_urls = Column(JSON, nullable=True)  # Array of generated image URLs
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
