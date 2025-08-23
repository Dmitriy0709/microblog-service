from typing import Generator
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models
from fastapi import Depends, Header, HTTPException


# Dependency для БД
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency для текущего пользователя
def get_current_user(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> models.User:
    user = db.query(models.User).filter(models.User.api_key == x_api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user
