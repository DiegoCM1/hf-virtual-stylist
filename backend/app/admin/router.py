# app/admin/router.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.admin import models, schemas
from app.admin.dependencies import get_db

router = APIRouter(prefix="/admin/fabrics", tags=["admin:fabrics"])

@router.get("", response_model=list[schemas.FabricRead])
def list_fabrics(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="search by family_id or display_name"),
    status_filter: str | None = Query(None, regex="^(active|inactive)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(models.FabricFamily).options(
        joinedload(models.FabricFamily.colors)
    )
    if status_filter:
        query = query.filter(models.FabricFamily.status == status_filter)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.FabricFamily.family_id.ilike(like)) |
            (models.FabricFamily.display_name.ilike(like))
        )
    items = (
        query.order_by(models.FabricFamily.display_name.asc())
             .offset(offset).limit(limit).all()
    )
    return items

@router.post("", response_model=schemas.FabricRead, status_code=status.HTTP_201_CREATED)
def create_fabric(payload: schemas.FabricCreate, db: Session = Depends(get_db)):
    fam = models.FabricFamily(
        family_id=payload.family_id,
        display_name=payload.display_name,
        status=payload.status,
    )
    db.add(fam)

    for c in payload.colors or []:
        db.add(models.Color(
            color_id=c.color_id,
            name=c.name,
            hex_value=c.hex_value,
            swatch_url=c.swatch_url,
            fabric_family=fam,
        ))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "family_id or color_id already exists")
    db.refresh(fam)
    # eager load colors for response
    fam = db.query(models.FabricFamily).options(joinedload(models.FabricFamily.colors)).get(fam.id)
    return fam

@router.patch("/{fabric_id}", response_model=schemas.FabricRead)
def update_fabric(fabric_id: int, payload: schemas.FabricUpdate, db: Session = Depends(get_db)):
    fam = db.query(models.FabricFamily).options(joinedload(models.FabricFamily.colors)).get(fabric_id)
    if not fam:
        raise HTTPException(404, "Fabric not found")

    if payload.family_id is not None:
        fam.family_id = payload.family_id
    if payload.display_name is not None:
        fam.display_name = payload.display_name
    if payload.status is not None:
        fam.status = payload.status

    # (Optional) naive replace-all colors if provided
    if payload.colors is not None:
        # delete existing
        for c in list(fam.colors):
            db.delete(c)
        # add new
        for c in payload.colors:
            db.add(models.Color(
                color_id=c.color_id,
                name=c.name,
                hex_value=c.hex_value,
                swatch_url=c.swatch_url,
                fabric_family=fam,
            ))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Duplicate family_id or color_id")
    db.refresh(fam)
    return fam

@router.post("/{fabric_id}/deactivate", response_model=schemas.FabricRead)
def deactivate_fabric(fabric_id: int, db: Session = Depends(get_db)):
    fam = db.query(models.FabricFamily).get(fabric_id)
    if not fam:
        raise HTTPException(404, "Fabric not found")
    fam.status = "inactive"
    db.commit()
    db.refresh(fam)
    return fam
