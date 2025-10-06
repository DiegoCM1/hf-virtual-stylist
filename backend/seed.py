# seed.py
import json
import csv
from pathlib import Path
from app.core.database import SessionLocal
from app.admin import models

# --- 1. CONFIGURATION: SET YOUR R2 PUBLIC URL BASE HERE ---
# This should be the path to the folder where you uploaded the fabric images.
R2_BASE_URL = "https://pub-56acd80744c24e2fb1fca9004abce188.r2.dev/fabrics/"
# ---------------------------------------------------------

print("Seeding database...")
with SessionLocal() as db:
    # --- PART 1: SEED FAMILIES AND COLORS FROM JSON (Your original logic) ---
    print("\n--- Processing fabrics.json to add families and colors ---")
    fabrics_path = Path('app/data/fabrics.json')
    if not fabrics_path.exists():
        raise FileNotFoundError(f"{fabrics_path} not found.")

    with open(fabrics_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for family_data in data['families']:
        db_family = db.query(models.FabricFamily).filter(models.FabricFamily.family_id == family_data['family_id']).first()
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

        for color_data in family_data.get('colors', []):
            color_id = color_data['color_id']
            if not db.query(models.Color).filter(models.Color.color_id == color_id).first():
                print(f"    - Adding color: {color_id}")
                hex_value = color_data.get('hex_value') or color_data.get('hex')
                if not hex_value:
                    raise ValueError(f"Color {color_id} is missing 'hex_value' in JSON.")
                
                db.add(models.Color(
                    color_id=color_id,
                    name=color_data['name'],
                    hex_value=hex_value,
                    swatch_url=color_data.get('swatch_url'),
                    fabric_family=db_family,
                ))
    db.commit()

    # --- PART 2: UPDATE SWATCH URLS FROM CSV (New logic) ---
    print("\n--- Processing swatch_mapping.csv to update URLs ---")
    mapping_path = Path('app/data/swatch_mapping.csv')
    if not mapping_path.exists():
        print(f"⚠️  Warning: {mapping_path} not found. Skipping URL updates.")
    else:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                color_id = row['color_id']
                image_filename = row['image_filename']
                
                color_record = db.query(models.Color).filter(models.Color.color_id == color_id).first()
                
                if color_record:
                    full_url = f"{R2_BASE_URL.rstrip('/')}/{image_filename}"
                    if color_record.swatch_url != full_url:
                        color_record.swatch_url = full_url
                        print(f"  Updating URL for {color_id}")
                else:
                    print(f"  ⚠️  Warning: Color ID '{color_id}' from CSV not found in database.")
        db.commit()

print("\n✅ Seeding complete.")