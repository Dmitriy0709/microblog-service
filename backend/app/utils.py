from __future__ import annotations
from pathlib import Path
from fastapi import UploadFile

MEDIA_ROOT = Path(__file__).parent / "media_storage"
MEDIA_ROOT.mkdir(exist_ok=True)


def save_upload(file: UploadFile, user_id: str | int | None) -> str:
    """Сохраняет загруженный файл и возвращает путь."""
    suffix = Path(file.filename).suffix if file.filename else ""
    if user_id is not None:
        filename = f"{user_id}_{file.filename}"
    else:
        filename = file.filename or "upload" + suffix

    stored_path = MEDIA_ROOT / filename
    with stored_path.open("wb") as f:
        f.write(file.file.read())
    return str(stored_path)


def media_public_url(path: str) -> str:
    """Формирует публичный URL для сохранённого файла."""
    return f"/media/{Path(path).name}"
