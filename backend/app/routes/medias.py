from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.utils import save_upload_file

router = APIRouter(prefix="/api/medias", tags=["medias"])


@router.post("", response_model=schemas.MediaCreated)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    stored_path = save_upload_file(file)
    media = models.Media(stored_path=stored_path, user_id=user.id)
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"media_id": media.id}
