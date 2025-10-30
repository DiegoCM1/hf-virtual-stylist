# app/admin/colors_router.py
"""Admin endpoints for individual color management."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.admin import models, schemas
from app.admin.dependencies import get_db

router = APIRouter(prefix="/admin/colors", tags=["admin:colors"])


@router.get("", response_model=list[schemas.ColorRead])
def list_colors(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Search by color_id, name, or swatch_code"),
    family_id: str | None = Query(None, description="Filter by family_id"),
    status_filter: str | None = Query(None, regex="^(active|inactive)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List all colors across families with search and filter."""
    query = db.query(models.Color)

    if status_filter:
        query = query.filter(models.Color.status == status_filter)

    if family_id:
        # Join with fabric_families to filter by family_id
        query = query.join(models.FabricFamily).filter(
            models.FabricFamily.family_id == family_id
        )

    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.Color.color_id.ilike(like)) |
            (models.Color.name.ilike(like)) |
            (models.Color.swatch_code.ilike(like))
        )

    items = (
        query.order_by(models.Color.name.asc())
             .offset(offset).limit(limit).all()
    )
    return items


@router.get("/{color_id}", response_model=schemas.ColorRead)
def get_color(color_id: int, db: Session = Depends(get_db)):
    """Get a single color by ID."""
    color = db.query(models.Color).get(color_id)
    if not color:
        raise HTTPException(404, "Color not found")
    return color


@router.patch("/{color_id}", response_model=schemas.ColorRead)
def update_color(
    color_id: int,
    payload: schemas.ColorUpdate,
    db: Session = Depends(get_db)
):
    """Update color details including moving to a different family."""
    color = db.query(models.Color).get(color_id)
    if not color:
        raise HTTPException(404, "Color not found")

    # Update fields if provided
    if payload.color_id is not None:
        color.color_id = payload.color_id
    if payload.name is not None:
        color.name = payload.name
    if payload.hex_value is not None:
        color.hex_value = payload.hex_value
    if payload.swatch_code is not None:
        color.swatch_code = payload.swatch_code
    if payload.swatch_url is not None:
        color.swatch_url = payload.swatch_url
    if payload.status is not None:
        color.status = payload.status

    # Move to different family if requested
    if payload.fabric_family_id is not None:
        # Verify target family exists
        target_family = db.query(models.FabricFamily).get(payload.fabric_family_id)
        if not target_family:
            raise HTTPException(404, "Target fabric family not found")
        color.fabric_family_id = payload.fabric_family_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Duplicate color_id")

    db.refresh(color)
    return color


@router.patch("/{color_id}/status", response_model=schemas.ColorRead)
def set_color_status(
    color_id: int,
    status_data: schemas.StatusUpdate,
    db: Session = Depends(get_db)
):
    """Toggle color status between active/inactive."""
    color = db.query(models.Color).get(color_id)
    if not color:
        raise HTTPException(404, "Color not found")

    color.status = status_data.status
    db.commit()
    db.refresh(color)
    return color


@router.post("/{color_id}/move", response_model=schemas.ColorRead)
def move_color_to_family(
    color_id: int,
    move_data: dict,
    db: Session = Depends(get_db)
):
    """Move a color to a different fabric family."""
    color = db.query(models.Color).get(color_id)
    if not color:
        raise HTTPException(404, "Color not found")

    target_family_id = move_data.get("fabric_family_id")
    if not target_family_id:
        raise HTTPException(400, "fabric_family_id is required")

    # Verify target family exists
    target_family = db.query(models.FabricFamily).get(target_family_id)
    if not target_family:
        raise HTTPException(404, "Target fabric family not found")

    color.fabric_family_id = target_family_id
    db.commit()
    db.refresh(color)
    return color


@router.delete("/{color_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_color(color_id: int, db: Session = Depends(get_db)):
    """Delete a color."""
    color = db.query(models.Color).get(color_id)
    if not color:
        raise HTTPException(404, "Color not found")

    db.delete(color)
    db.commit()
    return None
