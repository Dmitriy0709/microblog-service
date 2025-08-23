from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas, utils
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/medias", tags=["medias"])


@router.post("", response_model=schemas.MediaCreated)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    stored_path = utils.save_upload_file(file)
    media = models.Media(stored_path=stored_path, author_id=user.id)
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"media_id": media.id}
