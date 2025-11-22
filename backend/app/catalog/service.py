import json
from pathlib import Path
from app.catalog.schemas import CatalogResponse, Family, Color

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "fabrics.json"

def load_catalog() -> CatalogResponse:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    families = []
    for fam in raw.get("families", []):
        colors = [Color(**c) for c in fam.get("colors", [])]
        families.append(Family(
            family_id=fam["family_id"],
            display_name=fam["display_name"],
            status=fam.get("status","active"),
            sort=fam.get("sort",0),
            colors=colors
        ))
    return CatalogResponse(families=families)
