from __future__ import annotations

import secrets
from pathlib import Path
from typing import Final

from fastapi import UploadFile

# Директория для хранения загруженных файлов
UPLOAD_DIR: Final[Path] = Path("uploads")


def save_upload_file(file: UploadFile) -> str:
    """
    Сохраняет загруженный файл на диск и возвращает относительный путь,
    который пишем в БД в Media.stored_path.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Безопасное имя: случайный префикс + исходное расширение
    suffix = Path(file.filename or "").suffix
    safe_name = f"{secrets.token_hex(16)}{suffix}"
    stored_path = UPLOAD_DIR / safe_name

    with stored_path.open("wb") as out:
        # У UploadFile.file — файловый-like объект
        out.write(file.file.read())

    # Храним относительный путь (строкой)
    return str(stored_path)


def media_public_url(stored_path: str) -> str:
    """
    Преобразует путь, сохранённый в БД, в публичный URL для клиента.
    Здесь делаем простой вариант вида /media/<filename>.
    """
    name = Path(stored_path).name
    return f"/media/{name}"
