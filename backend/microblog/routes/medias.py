from fastapi import APIRouter, UploadFile, Depends
from microblog.utils import save_upload_file
from sqlalchemy.orm import Session
from microblog import models
from microblog.database import SessionLocal

router = APIRouter(prefix="/api/medias", tags=["medias"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("")
def upload_media(file: UploadFile, db: Session = Depends(get_db)):
    url = save_upload_file(file)
    media = models.Media(url=url)
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"id": media.id, "url": media.url}
