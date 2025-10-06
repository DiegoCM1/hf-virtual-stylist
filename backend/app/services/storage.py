# app/services/storage.py
from __future__ import annotations
from typing import Protocol
from pathlib import Path
import os
import io
import boto3
from urllib.parse import urljoin

from app.core.config import settings # Make sure this import is here

# --- STORAGE INTERFACE (Your original protocol) ---
class Storage(Protocol):
    def save_bytes(self, data: bytes, key: str, content_type: str = "image/jpeg") -> str: ...
    def url_for(self, key: str) -> str: ...

# --- LOCAL STORAGE (Your original implementation) ---
class LocalStorage:
    """
    Saves files under ./storage and serves them via FastAPI static mount (/files).
    base_url must match your StaticFiles mount (http://localhost:8000/files by default).
    """
    def __init__(self, base_dir: str = "storage", base_url: str = "http://localhost:8000/files"):
        self.base_dir = Path(base_dir)
        self.base_url = base_url.rstrip('/')

    def save_bytes(self, data: bytes, key: str, content_type: str = "image/jpeg") -> str:
        key = key.lstrip("/\\")
        dest = self.base_dir / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return self.url_for(key)

    def url_for(self, key: str) -> str:
        key = key.lstrip("/\\")
        # Ensure os-independent path for URL
        url_path = '/'.join(Path(key).parts)
        return f"{self.base_url}/{url_path}"

# --- R2 STORAGE (New implementation) ---
class R2Storage:
    """Saves files to a Cloudflare R2 bucket."""
    def __init__(self):
        endpoint_url = f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
        
        self.client = boto3.client(
            service_name='s3',
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name='auto',
        )
        self.bucket_name = settings.r2_bucket_name
        self.public_url = settings.r2_public_url.rstrip('/')

    def save_bytes(self, data: bytes, key: str, content_type: str = "image/jpeg") -> str:
        """Uploads bytes to the R2 bucket and returns the public URL."""
        key = key.lstrip("/\\")
        file_like_object = io.BytesIO(data)
        self.client.upload_fileobj(
            Fileobj=file_like_object,
            Bucket=self.bucket_name,
            Key=key,
            ExtraArgs={'ContentType': content_type} 
        )
        return self.url_for(key)

    def url_for(self, key: str) -> str:
        """Constructs the public URL for a given key."""
        key = key.lstrip("/\\")
        return f"{self.public_url}/{key}"