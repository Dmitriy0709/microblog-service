from __future__ import annotations

import hashlib
import os
from pathlib import Path


def hash_password(password: str) -> str:
    """Хеширует пароль используя SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет пароль против хеша."""
    return hash_password(password) == hashed_password


def generate_api_key() -> str:
    """Генерирует случайный API ключ."""
    return hashlib.sha256(os.urandom(32)).hexdigest()


def get_media_path() -> Path:
    """Возвращает путь к директории для медиа файлов."""
    media_dir = os.getenv("MEDIA_DIR", "media")
    media_path = Path(media_dir)
    media_path.mkdir(exist_ok=True)
    return media_path


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """Сохраняет загруженный файл и возвращает его путь."""
    media_path = get_media_path()
    file_path = media_path / filename

    with open(file_path, "wb") as f:
        f.write(file_content)

    return str(file_path)


def media_public_url(media_path: str) -> str:
    """Возвращает публичный URL для медиа файла."""
    return f"/static/media/{os.path.basename(media_path)}"
