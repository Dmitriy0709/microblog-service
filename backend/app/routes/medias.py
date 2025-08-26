# backend/app/routes/medias.py
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..database import get_db
from .. import models, schemas
from ..utils import save_upload_file

router = APIRouter(prefix="/api/medias", tags=["media"])


@router.post("", response_model=schemas.MediaCreated)
async def upload_media(file: UploadFile = File(...), db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # read content into UploadFile-like object for our save function
    content = await file.read()
    from io import BytesIO
    uf = UploadFile(filename=file.filename, file=BytesIO(content), content_type=file.content_type)
    url = save_upload_file(uf)
    media = models.Media(url=url, tweet_id=None)
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"id": media.id, "url": media.url}
