from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=schemas.UserMeResponse)
def read_me(current_user: models.User = Depends(get_current_user)) -> schemas.UserMeResponse:
    """
    Возвращает текущего пользователя (по api_key).
    """
    return schemas.UserMeResponse(
        id=current_user.id,
        name=current_user.name,
        api_key=current_user.api_key,
    )


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)) -> schemas.UserOut:
    """
    Получить публичную информацию о пользователе по ID.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserOut(id=user.id, name=user.name)
