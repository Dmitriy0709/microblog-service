from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {"id": current_user.id, "name": current_user.name}
