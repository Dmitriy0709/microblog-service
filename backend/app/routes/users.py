from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


# ------------------------
# Текущий пользователь
# ------------------------
@router.get("/me", response_model=schemas.UserMeResponse)
def get_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return current_user


# ------------------------
# Follow
# ------------------------
@router.post("/{user_id}/follow")
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_id == current_user.id:
        return {"message": "You cannot follow yourself"}

    follow = models.Follow(follower_id=current_user.id, followee_id=user_id)
    db.add(follow)
    db.commit()
    return {"message": f"Now following user {user_id}"}


# ------------------------
# Unfollow
# ------------------------
@router.delete("/{user_id}/follow")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.followee_id == user_id,
    ).delete()
    db.commit()
    return {"message": f"Unfollowed user {user_id}"}
