from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Media
from ..schemas import MediaCreated
from ..deps import get_current_user
from ..models import User
from ..utils import save_uploaded_file

router = APIRouter(prefix="/api/medias", tags=["medias"])


@router.post("", response_model=MediaCreated)
async def upload_media(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> MediaCreated:
    """Загружает медиа файл."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл должен иметь имя")

    # Читаем содержимое файла
    file_content = await file.read()

    # Сохраняем файл
    file_path = save_uploaded_file(file_content, file.filename)

    # Создаем запись в базе данных
    media = Media(url=file_path)
    db.add(media)
    db.commit()
    db.refresh(media)

    return MediaCreated(
        id=media.id,
        url=media.url
    )


@router.get("/{media_id}")
async def get_media(media_id: int, db: Session = Depends(get_db)) -> FileResponse:
    """Возвращает медиа файл по ID."""
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Медиа не найдено")

    return FileResponse(media.url)


@router.get("", response_model=List[MediaCreated])
async def list_media(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
) -> List[MediaCreated]:
    """Возвращает список всех медиа файлов."""
    medias = db.query(Media).offset(skip).limit(limit).all()
    return [MediaCreated(id=m.id, url=m.url) for m in medias]
