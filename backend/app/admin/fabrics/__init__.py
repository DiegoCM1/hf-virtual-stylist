"""Fabrics and colors management submodule."""

from app.admin.fabrics.fabrics_router import router as fabrics_router
from app.admin.fabrics.colors_router import router as colors_router

__all__ = ["fabrics_router", "colors_router"]
