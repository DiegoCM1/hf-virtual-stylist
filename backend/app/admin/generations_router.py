# app/admin/generations_router.py
"""Admin endpoints for viewing and managing generated images."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.admin import models, schemas
from app.admin.dependencies import get_db

router = APIRouter(prefix="/admin/generations", tags=["admin:generations"])


@router.get("", response_model=list[schemas.GenerationJobRead])
def list_generations(
    db: Session = Depends(get_db),
    family_id: str | None = Query(None, description="Filter by family_id"),
    color_id: str | None = Query(None, description="Filter by color_id"),
    status_filter: str | None = Query(None, regex="^(pending|processing|completed|failed)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List all generation jobs with optional filters."""
    query = db.query(models.GenerationJob)

    if status_filter:
        query = query.filter(models.GenerationJob.status == status_filter)

    if family_id:
        query = query.filter(models.GenerationJob.family_id == family_id)

    if color_id:
        query = query.filter(models.GenerationJob.color_id == color_id)

    items = (
        query.order_by(desc(models.GenerationJob.created_at))
             .offset(offset).limit(limit).all()
    )
    return items


@router.get("/by-fabric/{family_id}/{color_id}", response_model=list[schemas.GenerationJobRead])
def get_generations_by_fabric(
    family_id: str,
    color_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    """Get all generated images for a specific fabric color."""
    jobs = (
        db.query(models.GenerationJob)
        .filter(
            models.GenerationJob.family_id == family_id,
            models.GenerationJob.color_id == color_id,
            models.GenerationJob.status == "completed"
        )
        .order_by(desc(models.GenerationJob.created_at))
        .limit(limit)
        .all()
    )
    return jobs


@router.get("/stats")
def get_generation_stats(db: Session = Depends(get_db)):
    """Get analytics on generation usage."""
    # Total count
    total = db.query(func.count(models.GenerationJob.id)).scalar()

    # Count by status
    by_status = (
        db.query(
            models.GenerationJob.status,
            func.count(models.GenerationJob.id).label("count")
        )
        .group_by(models.GenerationJob.status)
        .all()
    )

    # Count by family
    by_family = (
        db.query(
            models.GenerationJob.family_id,
            func.count(models.GenerationJob.id).label("count")
        )
        .group_by(models.GenerationJob.family_id)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    # Recent activity (last 24 hours)
    from datetime import datetime, timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_count = (
        db.query(func.count(models.GenerationJob.id))
        .filter(models.GenerationJob.created_at >= yesterday)
        .scalar()
    )

    return {
        "total_generations": total,
        "by_status": {row.status: row.count for row in by_status},
        "by_family": [{"family_id": row.family_id, "count": row.count} for row in by_family],
        "last_24_hours": recent_count,
    }


@router.get("/{job_id}", response_model=schemas.GenerationJobRead)
def get_generation(job_id: str, db: Session = Depends(get_db)):
    """Get a single generation job by job_id (UUID)."""
    job = db.query(models.GenerationJob).filter(models.GenerationJob.job_id == job_id).first()
    if not job:
        raise HTTPException(404, "Generation job not found")
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generation(job_id: str, db: Session = Depends(get_db)):
    """Delete a generation job and its metadata (images remain in storage)."""
    job = db.query(models.GenerationJob).filter(models.GenerationJob.job_id == job_id).first()
    if not job:
        raise HTTPException(404, "Generation job not found")

    # Note: This deletes the database record only.
    # Generated images in R2/local storage are NOT deleted.
    # You may want to add storage cleanup logic here if needed.

    db.delete(job)
    db.commit()
    return None
