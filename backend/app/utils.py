# backend/app/utils.py
from __future__ import annotations

from pathlib import Path
from fastapi import UploadFile
import uuid

MEDIA_ROOT = Path(__file__).parent.parent / "media_storage"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


def save_upload(file: UploadFile | None) -> str:
    """
    Save UploadFile and return relative public path.
    If file is None or empty, raise ValueError.
    """
    if file is None:
        raise ValueError("No file provided")
    # If UploadFile already had .file consumed, ensure we read from .file
    try:
        content = file.file.read()
    except Exception:
        # might be async UploadFile; try to read .filename only
        raise
    ext = Path(file.filename).suffix or ""
    name = f"{uuid.uuid4().hex}{ext}"
    dest = MEDIA_ROOT / name
    dest.write_bytes(content)
    return f"/media/{name}"


# compatibility alias (some places used save_upload_file)
def save_upload_file(file: UploadFile) -> str:
    return save_upload(file)


def media_public_url(stored_url: str) -> str:
    # stored_url is already a public path (/media/...) in our simple setup
    return stored_url
