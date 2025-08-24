from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.utils import save_upload_file

router = APIRouter(prefix="/api/medias", tags=["medias"])


@router.post("", response_model=schemas.MediaCreated)
async def upload_media(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Загрузка файла"""
    try:
        file_url = await save_upload_file(file)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to save file")

    media = models.Media(url=file_url, owner_id=current_user.id)
    db.add(media)
    db.commit()
    db.refresh(media)

    return {"media_id": media.id, "url": media.url}
