from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..utils import save_upload

router = APIRouter(prefix="/api/medias", tags=["media"])

@router.post("", response_model=schemas.MediaCreated)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    saved = save_upload(content, file.filename)
    media = models.Media(original_name=file.filename, stored_path=str(saved))
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"result": True, "media_id": media.id}
