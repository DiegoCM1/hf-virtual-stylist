#!/usr/bin/env python3
"""
Quick script to update swatch_code field from swatch_mapping.csv
Run this to populate swatch codes without re-seeding entire database.
"""
import csv
from pathlib import Path
from app.core.database import SessionLocal
from app.admin import models

print("Updating swatch codes from CSV...")
with SessionLocal() as db:
    mapping_path = Path('app/data/swatch_mapping.csv')

    if not mapping_path.exists():
        print(f"❌ Error: {mapping_path} not found.")
        exit(1)

    updated_count = 0
    missing_count = 0

    with open(mapping_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            color_id = row['color_id']
            image_filename = row['image_filename']

            # Extract swatch code (filename without extension)
            swatch_code = image_filename.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')

            color_record = db.query(models.Color).filter(models.Color.color_id == color_id).first()

            if color_record:
                if color_record.swatch_code != swatch_code:
                    color_record.swatch_code = swatch_code
                    print(f"  ✓ Updated {color_id} -> {swatch_code}")
                    updated_count += 1
                else:
                    print(f"  - Skipped {color_id} (already up to date)")
            else:
                print(f"  ⚠️  Warning: Color ID '{color_id}' not found in database.")
                missing_count += 1

    db.commit()

    print(f"\n✅ Done!")
    print(f"   Updated: {updated_count}")
    print(f"   Missing: {missing_count}")
