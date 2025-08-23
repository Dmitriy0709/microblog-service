from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=schemas.UserMeResponse)
def get_me(user: models.User = Depends(get_current_user)):
    return schemas.UserMeResponse(id=user.id, name=user.name)


@router.post("/{user_id}/follow")
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    me: models.User = Depends(get_current_user),
):
    if me.id == user_id:
        return {"status": "cannot follow yourself"}

    exists = (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == me.id, models.Follow.followee_id == user_id)
        .first()
    )
    if exists:
        return {"status": "already following"}

    follow = models.Follow(follower_id=me.id, followee_id=user_id)
    db.add(follow)
    db.commit()
    return {"status": "followed"}
