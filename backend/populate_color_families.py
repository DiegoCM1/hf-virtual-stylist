"""
Populate database with organized color families.

Reads the categorization from organize_swatches_by_color.py output
and creates fabric families and colors in the database.
"""

import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.admin.models import FabricFamily, Color


# Spanish display names for color families
FAMILY_DISPLAY_NAMES = {
    "azules": "Azules",
    "grises": "Grises",
    "marrones": "Marrones y Beiges",
    "neutros": "Negros y Blancos",
    "verdes": "Verdes",
    "tonos-calidos": "Tonos Cálidos",
    "tonos-frios": "Tonos Fríos",
}


def populate_from_categorization():
    """Populate database from swatch_categorization.json."""

    # Load categorization results
    try:
        with open("swatch_categorization.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ swatch_categorization.json not found!")
        print("   Run: python organize_swatches_by_color.py first")
        return

    organized = data['organized_by_family']

    db: Session = SessionLocal()

    try:
        # Clear existing data (optional - comment out to keep test data)
        print("🗑️  Clearing existing fabric families and colors...")
        db.query(Color).delete()
        db.query(FabricFamily).delete()
        db.commit()

        print("✨ Creating new fabric families and colors...\n")

        total_colors = 0

        # Create families and their colors
        for sort_order, (family_id, colors_list) in enumerate(organized.items(), start=1):
            if not colors_list:
                continue  # Skip empty families

            # Create fabric family
            family = FabricFamily(
                family_id=family_id,
                display_name=FAMILY_DISPLAY_NAMES.get(family_id, family_id.title()),
                status="active"
            )
            db.add(family)
            db.flush()  # Get the family.id

            print(f"📁 {family.display_name} ({len(colors_list)} colors)")

            # Create colors for this family
            for color_data in colors_list:
                # Generate unique color_id
                color_id = f"{family_id[:2]}-{color_data['swatch_code'][:10]}"

                color = Color(
                    fabric_family_id=family.id,
                    color_id=color_id,
                    name=color_data['color_name'],
                    hex_value=color_data['hex'],
                    swatch_code=color_data['swatch_code']
                )
                db.add(color)
                total_colors += 1

                print(f"   └─ {color_data['swatch_code']:<20} {color_data['color_name']:<25} {color_data['hex']}")

            print()

        # Commit all changes
        db.commit()

        print("=" * 80)
        print(f"✅ Successfully created:")
        print(f"   Fabric families: {len([f for f, colors in organized.items() if colors])}")
        print(f"   Colors: {total_colors}")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def preview_organization():
    """Preview the organization without making changes."""
    try:
        with open("swatch_categorization.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ swatch_categorization.json not found!")
        return

    print("📋 Preview of Organization:\n")
    print("=" * 80)

    summary = data['summary']
    for family_id, count in summary.items():
        if count > 0:
            display_name = FAMILY_DISPLAY_NAMES.get(family_id, family_id.title())
            print(f"{display_name:<25} {count:>3} swatches")

    print("=" * 80)
    print(f"Total: {sum(summary.values())} swatches")
    print()


if __name__ == "__main__":
    import sys

    print("🎨 Fabric Family Population Script\n")

    if "--preview" in sys.argv:
        preview_organization()
    else:
        print("⚠️  This will REPLACE all existing fabric families and colors!")
        response = input("   Continue? (yes/no): ")

        if response.lower() == "yes":
            populate_from_categorization()
            print("\n✨ Done!")
        else:
            print("❌ Cancelled")
