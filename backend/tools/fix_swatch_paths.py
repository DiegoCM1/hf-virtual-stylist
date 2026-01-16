"""
Quick fix script to update swatch URLs to correct R2 path.

Current (wrong):  https://pub-.../fabrics/095T-0121.png
Correct (right):  https://pub-.../ZEGNA%202025-26/095T-0121.png
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.admin.models import Color
from app.core.config import settings
from urllib.parse import quote

def fix_swatch_urls():
    """Update all swatch URLs to use correct R2 path."""
    db: Session = SessionLocal()
    try:
        colors = db.query(Color).all()
        updated_count = 0

        for color in colors:
            if color.swatch_url and "/fabrics/" in color.swatch_url:
                # Extract the filename from old URL
                # Example: https://pub-.../fabrics/095T-0121.png → 095T-0121.png
                filename = color.swatch_url.split("/fabrics/")[-1]

                # Build new URL with correct path
                swatch_path = f"ZEGNA%202025-26/{filename}"
                new_url = f"{settings.r2_public_url}/{swatch_path}"

                print(f"✅ {color.color_id}: {color.swatch_url}")
                print(f"   → {new_url}\n")

                color.swatch_url = new_url
                updated_count += 1

        # Commit all changes
        db.commit()

        print(f"\n📊 Summary:")
        print(f"   Total colors: {len(colors)}")
        print(f"   Updated: {updated_count}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 Fixing swatch URL paths...\n")
    fix_swatch_urls()
    print("\n✨ Done!")
