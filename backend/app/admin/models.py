"""Database models for the admin application."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class FabricFamily(Base):
    """Represents a fabric family grouping available within the catalog."""

    __tablename__ = "fabric_families"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")

    colors = relationship(
        "Color",
        back_populates="fabric_family",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Color(Base):
    """Represents a color option associated with a fabric family."""

    __tablename__ = "colors"

    id = Column(Integer, primary_key=True, index=True)
    fabric_family_id = Column(
        Integer, ForeignKey("fabric_families.id", ondelete="CASCADE"), nullable=False, index=True
    )
    color_id = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    hex_value = Column(String, nullable=False)
    swatch_url = Column(String, nullable=True)

    fabric_family = relationship("FabricFamily", back_populates="colors")
