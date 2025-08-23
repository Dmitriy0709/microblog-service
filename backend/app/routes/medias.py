from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/medias", tags=["medias"])


# ------------------------
# Upload Media
# ------------------------
@router.post("", response_model=schemas.MediaCreated)
def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # имитация сохранения файла — просто сохраняем имя
    media = models.Media(url=file.filename, uploader_id=current_user.id)
    db.add(media)
    db.commit()
    db.refresh(media)
    return media
