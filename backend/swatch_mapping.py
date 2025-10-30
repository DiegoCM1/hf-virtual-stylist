"""
Script to populate swatch_code field for all colors in the database.

Instructions:
1. Fill in the SWATCH_MAPPING dictionary below with your color_id → swatch_code mappings
2. Run this script: python swatch_mapping.py
3. The script will update all colors with their corresponding swatch codes
"""

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.admin.models import Color

# Map color_id to swatch_code (R2 filename without extension)
# Example: "lc-navy-001" → "095T-0121"
SWATCH_MAPPING = {
    # Lana-Cachemir
    "lc-navy-001": "095T-0121",  # TODO: Replace with actual swatch code
    "lc-charcoal-002": "095T-0132",  # TODO: Replace with actual swatch code
    "lc-camel-003": "",  # TODO: Add swatch code
    "lc-heather-004": "",  # TODO: Add swatch code
    "lc-burgundy-005": "",  # TODO: Add swatch code

    # Lana-Normal
    "ln-forest-001": "",  # TODO: Add swatch code
    "ln-olive-002": "",  # TODO: Add swatch code
    "ln-rust-003": "",  # TODO: Add swatch code
    "ln-beige-004": "",  # TODO: Add swatch code
    "ln-brown-005": "",  # TODO: Add swatch code

    # Lino Premium
    "lp-sand-001": "",  # TODO: Add swatch code
    "lp-ivory-002": "",  # TODO: Add swatch code
    "lp-sky-003": "",  # TODO: Add swatch code
    "lp-sage-004": "",  # TODO: Add swatch code
    "lp-terracotta-005": "",  # TODO: Add swatch code

    # Algodón Tech
    "at-black-001": "095T-B22D",  # TODO: Replace with actual swatch code
    "at-white-002": "",  # TODO: Add swatch code
    "at-techgrey-003": "",  # TODO: Add swatch code
    "at-navy-004": "",  # TODO: Add swatch code
    "at-khaki-005": "",  # TODO: Add swatch code

    # Seda Lux
    "sl-emerald-001": "",  # TODO: Add swatch code
    "sl-ruby-002": "",  # TODO: Add swatch code
    "sl-sapphire-003": "",  # TODO: Add swatch code
    "sl-gold-004": "",  # TODO: Add swatch code
    "sl-plum-005": "",  # TODO: Add swatch code
}


def update_swatch_codes():
    """Update swatch_code for all colors based on the mapping."""
    db: Session = SessionLocal()
    try:
        updated_count = 0
        skipped_count = 0

        for color_id, swatch_code in SWATCH_MAPPING.items():
            if not swatch_code:  # Skip empty mappings
                print(f"⚠️  Skipping {color_id} - no swatch code provided")
                skipped_count += 1
                continue

            # Find color by color_id
            color = db.query(Color).filter(Color.color_id == color_id).first()

            if color:
                color.swatch_code = swatch_code
                print(f"✅ Updated {color_id} → {swatch_code}")
                updated_count += 1
            else:
                print(f"❌ Color not found: {color_id}")

        # Commit all changes
        db.commit()

        print(f"\n📊 Summary:")
        print(f"   Updated: {updated_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Total:   {len(SWATCH_MAPPING)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🎨 Updating swatch codes for colors...\n")
    update_swatch_codes()
    print("\n✨ Done!")
