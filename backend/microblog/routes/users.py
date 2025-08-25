from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from microblog import models, schemas
from microblog.database import SessionLocal

router = APIRouter(prefix="/api/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[schemas.UserBase])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
