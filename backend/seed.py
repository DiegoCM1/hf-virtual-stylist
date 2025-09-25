# seed.py
import json
from app.core.database import SessionLocal
from app.admin import models

print("Seeding database...")

with SessionLocal() as db:
    # Make sure Alembic has created tables first: alembic upgrade head
    with open('app/data/fabrics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for family_data in data['families']:
        # upsert family
        db_family = (
            db.query(models.FabricFamily)
            .filter(models.FabricFamily.family_id == family_data['family_id'])
            .first()
        )
        if not db_family:
            print(f"  Adding family: {family_data['display_name']}")
            db_family = models.FabricFamily(
                family_id=family_data['family_id'],
                display_name=family_data['display_name'],
                status=family_data.get('status', 'active'),
            )
            db.add(db_family)
            db.commit()
            db.refresh(db_family)

        # colors
        for color_data in family_data.get('colors', []):
            # required by your model
            color_id = color_data['color_id']
            name = color_data['name']

            # your model requires hex_value (NOT NULL)
            # adjust the key if your JSON uses another name (e.g., "hex" or "hex_value")
            hex_value = (
                color_data.get('hex_value')
                or color_data.get('hex')
            )
            if not hex_value:
                # choose: (a) fail fast, or (b) default
                raise ValueError(
                    f"Color {color_id} is missing 'hex_value' in JSON and the DB column is NOT NULL."
                )
                # Or, if you prefer a fallback:
                # hex_value = "#000000"

            swatch_url = color_data.get('swatch_url')  # nullable in your model

            exists = (
                db.query(models.Color)
                .filter(models.Color.color_id == color_id)
                .first()
            )
            if exists:
                continue

            print(f"    - Adding color: {color_id}")
            db_color = models.Color(
                color_id=color_id,
                name=name,
                hex_value=hex_value,
                swatch_url=swatch_url,
                # Use the relationship name, not the FK keyword:
                fabric_family=db_family,
                # Alternative if you prefer FK directly:
                # fabric_family_id=db_family.id,
            )
            db.add(db_color)

    db.commit()

print("Seeding complete.")
