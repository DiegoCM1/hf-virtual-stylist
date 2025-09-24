# app/services/storage.py
from __future__ import annotations
from typing import Protocol
from pathlib import Path
import os

class Storage(Protocol):
    def save_bytes(self, data: bytes, key: str, content_type: str = "image/jpeg") -> str: ...
    def url_for(self, key: str) -> str: ...

class LocalStorage:
    """
    Saves files under ./storage and serves them via FastAPI static mount (/files).
    base_url must match your StaticFiles mount (http://localhost:8000/files by default).
    """
    def __init__(self, base_dir: str = "storage", base_url: str = "http://localhost:8000/files"):
        self.base_dir = Path(base_dir)
        self.base_url = base_url

    def save_bytes(self, data: bytes, key: str, content_type: str = "image/jpeg") -> str:
        key = key.lstrip("/\\")
        dest = self.base_dir / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return f"{self.base_url}/{key.replace(os.sep, '/')}"

    def url_for(self, key: str) -> str:
        key = key.lstrip("/\\")
        return f"{self.base_url}/{key.replace(os.sep, '/')}"
