from __future__ import annotations

from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

def get_current_user(x_api_key: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    user = db.query(User).filter(User.api_key == x_api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user
