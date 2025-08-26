# backend/app/deps.py
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from . import models

API_KEY_HEADER = "X-API-Key"


def get_current_user(api_key: str = Header(..., alias=API_KEY_HEADER), db: Session = Depends(get_db)) -> models.User:
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
    user = db.query(models.User).filter(models.User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid api key")
    return user
