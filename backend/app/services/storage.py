"""Storage adapter helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Protocol


class StorageAdapter(Protocol):
    """Protocol implemented by storage backends."""

    def save_bytes(self, data: bytes, key: str, content_type: str = "image/jpeg") -> str:
        ...


class LocalStorage:
    """Persist files locally under ``./storage`` and expose them via ``/files``."""

    def __init__(self, base_dir: str, base_url: str):
        self.base_dir = Path(base_dir)
        self.base_url = base_url.rstrip("/")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, data: bytes, key: str, content_type: str = "image/jpeg") -> str:
        safe_key = _normalize_key(key)
        dest = self.base_dir / safe_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return f"{self.base_url}/{safe_key.replace(os.sep, '/')}"


def save_bytes(data: bytes, key: str, content_type: str = "image/jpeg") -> str:
    """Save *data* using the configured adapter and return a public URL."""

    storage = _get_storage()
    try:
        return storage.save_bytes(data, key, content_type=content_type)
    except Exception as exc:  # pragma: no cover - surfaced by global handler
        raise RuntimeError("Failed to persist generated file") from exc


def _normalize_key(key: str) -> str:
    # Prevent leading slashes so Path does not treat the key as absolute.
    return key.lstrip("/\\")


@lru_cache(maxsize=1)
def _get_storage() -> StorageAdapter:
    driver = os.getenv("STORAGE_DRIVER", "local").lower() or "local"
    if driver != "local":
        # Future cloud adapters plug in here; fall back to local for now.
        driver = "local"

    if driver == "local":
        return _build_local_storage()

    raise RuntimeError(f"Unsupported storage driver: {driver}")


def _build_local_storage() -> LocalStorage:
    base_dir = os.getenv("LOCAL_STORAGE_DIR", "storage")
    public_base = os.getenv("PUBLIC_BASE_URL")
    if public_base:
        base_url = f"{public_base.rstrip('/')}/files"
    else:
        base_url = "http://localhost:8000/files"
    return LocalStorage(base_dir=base_dir, base_url=base_url)


def _reset_storage_cache() -> None:
    """Testing helper to reset the cached adapter."""

    _get_storage.cache_clear()
