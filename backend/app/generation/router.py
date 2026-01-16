# app/generation/router.py
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.generation.schemas import GenerationRequest, GenerationResponse, ImageResult, SwatchUploadResponse
from app.generation.models import GenerationJob
from app.generation.storage import R2Storage, LocalStorage
from app.admin.dependencies import get_db
from app.core.config import settings

router = APIRouter()

# Allowed file types and size limits for swatch uploads
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


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
        swatch_url=req.swatch_url,
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


@router.post("/upload-swatch", response_model=SwatchUploadResponse)
async def upload_swatch(file: UploadFile = File(...)) -> SwatchUploadResponse:
    """
    Upload a custom swatch image for use with IP-Adapter.

    Returns a public URL that can be passed to POST /generate as swatch_url.
    Files are stored in R2 under temp-uploads/ and cleaned up periodically.
    """
    print(f"📤 [upload-swatch] Received file: {file.filename}, content_type={file.content_type}")

    # 1. Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        print(f"❌ [upload-swatch] Invalid type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # 2. Read file and validate size
    contents = await file.read()
    size_bytes = len(contents)
    print(f"📦 [upload-swatch] Size: {size_bytes / 1024:.1f}KB")

    if size_bytes > MAX_FILE_SIZE_BYTES:
        print(f"❌ [upload-swatch] File too large: {size_bytes / 1024 / 1024:.1f}MB")
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {size_bytes / 1024 / 1024:.1f}MB. Maximum: {MAX_FILE_SIZE_MB}MB"
        )

    if size_bytes == 0:
        print("❌ [upload-swatch] Empty file")
        raise HTTPException(status_code=400, detail="Empty file")

    # 3. Generate unique key for R2
    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "jpg"
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        ext = "jpg"

    unique_id = uuid.uuid4().hex[:12]
    key = f"temp-uploads/{unique_id}.{ext}"
    print(f"🔑 [upload-swatch] Generated key: {key}")

    # 4. Upload to storage backend
    if settings.storage_backend == "r2":
        storage = R2Storage()
        print("☁️  [upload-swatch] Using R2 storage")
    else:
        storage = LocalStorage()
        print("💾 [upload-swatch] Using local storage")

    swatch_url = storage.save_bytes(contents, key, file.content_type or "image/jpeg")
    print(f"✅ [upload-swatch] Uploaded successfully: {swatch_url}")

    return SwatchUploadResponse(
        swatch_url=swatch_url,
        filename=file.filename or f"{unique_id}.{ext}",
        size_bytes=size_bytes
    )
