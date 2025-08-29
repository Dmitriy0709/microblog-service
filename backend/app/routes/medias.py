from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Media, User
from ..schemas import MediaCreated
from ..deps import get_current_user
from ..utils import save_uploaded_file

router = APIRouter(prefix="/api/medias", tags=["medias"])

@router.post("", response_model=MediaCreated)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MediaCreated:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")
    content = await file.read()
    path = save_uploaded_file(content, file.filename)
    media = Media(url=path)
    db.add(media)
    db.commit()
    db.refresh(media)
    return MediaCreated(id=int(media.id), url=str(media.url))

@router.get("/{media_id}", response_model=MediaCreated)
def get_media(media_id: int, db: Session = Depends(get_db)) -> FileResponse:
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(media.url)

@router.get("", response_model=List[MediaCreated])
def list_media(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[MediaCreated]:
    medias = db.query(Media).offset(skip).limit(limit).all()
    return [MediaCreated(id=int(m.id), url=str(m.url)) for m in medias]
