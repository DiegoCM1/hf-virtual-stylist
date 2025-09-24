from fastapi import APIRouter
from app.models.catalog import CatalogResponse
from app.services.catalog import load_catalog

router = APIRouter(tags=["public"])

@router.get("/catalog", response_model=CatalogResponse)
def get_catalog():
    return load_catalog()