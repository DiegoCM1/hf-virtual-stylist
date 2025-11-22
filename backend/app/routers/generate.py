# app/routers/generate.py
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.generate import GenerationRequest, GenerationResponse
from app.admin.generations.models import GenerationJob  # Updated import
from app.admin.dependencies import get_db

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse, status_code=201)
def generate(req: GenerationRequest, db: Session = Depends(get_db)) -> GenerationResponse:
    """Create a background job for image generation and return immediately."""

    # Generate a unique job ID
    job_id = str(uuid.uuid4())

    # Create the job record with status="pending"
    job = GenerationJob(
        job_id=job_id,
        status="pending",
        family_id=req.family_id,
        color_id=req.color_id,
        cuts=req.cuts,
        seed=req.seed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Return immediately with pending status
    return GenerationResponse(
        request_id=job_id,
        status="pending",
        images=[],
        meta={"message": "Job created. Poll /jobs/{job_id} for status."}
    )


@router.get("/jobs/{job_id}", response_model=GenerationResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)) -> GenerationResponse:
    """Get the status and results of a generation job."""

    job = db.query(GenerationJob).filter(GenerationJob.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Build response based on job status
    response = GenerationResponse(
        request_id=job.job_id,
        status=job.status,  # "pending", "processing", "completed", "failed"
        images=[],
        meta={}
    )

    if job.status == "completed" and job.result_urls:
        # Convert result_urls to ImageResult objects
        from app.models.generate import ImageResult
        for i, url in enumerate(job.result_urls):
            cut = job.cuts[i] if i < len(job.cuts) else "recto"
            response.images.append(
                ImageResult(
                    cut=cut,
                    url=url,
                    width=1024,  # Default SDXL output size
                    height=1024,
                    watermark=True
                )
            )
    elif job.status == "failed" and job.error_message:
        response.meta["error"] = job.error_message

    # Add timing info
    if job.completed_at and job.started_at:
        duration_ms = int((job.completed_at - job.started_at).total_seconds() * 1000)
        response.duration_ms = duration_ms

    return response