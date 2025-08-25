from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.utils import save_upload_file

router = APIRouter(prefix="/api/medias", tags=["medias"])


@router.post("")
def upload_media(file: UploadFile, db: Session = Depends(get_db)):
    file_path = f"uploads/{file.filename}"
    save_upload_file(file, file_path)
    media = models.Media(url=file_path)
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"id": media.id, "url": media.url}
