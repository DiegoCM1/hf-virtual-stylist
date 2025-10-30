from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from urllib.parse import quote

from app.admin.dependencies import get_db
from app.admin import models
from app.services.catalog import load_catalog  # we reuse this to pull JSON-only extras
from app.core.config import settings

router = APIRouter(tags=["public"])

@router.get("/catalog")
def get_catalog(db: Session = Depends(get_db)):
    # 1) Build a lookup for extras coming from fabrics.json (JSON-only fields)
    #    load_catalog() returns your Pydantic CatalogResponse
    extras_by_family_id: dict[str, dict] = {}
    try:
        json_catalog = load_catalog()
        # json_catalog.families is a list of Pydantic models with lora_id, default_recipe, sort, etc.
        for fam in json_catalog.families:
            extras_by_family_id[fam.family_id] = {
                "lora_id": getattr(fam, "lora_id", None),
                "default_recipe": getattr(fam, "default_recipe", None),
                "sort": getattr(fam, "sort", None),
            }
    except Exception:
        # If JSON file missing or malformed, just proceed without extras
        extras_by_family_id = {}

    # 2) Query only ACTIVE families with their colors
    families = (
        db.query(models.FabricFamily)
          .options(joinedload(models.FabricFamily.colors))
          .filter(models.FabricFamily.status == "active")
          .all()
    )

    # 3) Shape response exactly like your JSON catalog (note: color "hex" from DB's hex_value)
    shaped = []
    for f in families:
        extras = extras_by_family_id.get(f.family_id, {})

        # Build color responses with swatch URLs
        colors_response = []
        for c in f.colors:
            color_dict = {
                "color_id": c.color_id,
                "name": c.name,
                "hex": c.hex_value,      # <-- FE expects "hex"
            }

            # Build swatch_url from swatch_code if available
            if c.swatch_code and settings.r2_public_url:
                # URL encode the path components for spaces and special chars
                swatch_path = f"ZEGNA%202025-26/{quote(c.swatch_code)}.png"
                color_dict["swatch_url"] = f"{settings.r2_public_url}/{swatch_path}"
            elif c.swatch_url:
                # Use explicit swatch_url if set
                color_dict["swatch_url"] = c.swatch_url
            else:
                # No swatch available
                color_dict["swatch_url"] = None

            colors_response.append(color_dict)

        shaped.append({
            "family_id": f.family_id,
            "display_name": f.display_name,
            "lora_id": extras.get("lora_id"),
            "default_recipe": extras.get("default_recipe"),
            "colors": colors_response,
            "status": f.status,              # harmless for FE, but matches your JSON
            "sort": extras.get("sort"),
        })

    # 4) Sort using JSON "sort" if present, else by display_name
    shaped.sort(key=lambda x: (x.get("sort") is None, x.get("sort") or x["display_name"]))

    return {"families": shaped}
