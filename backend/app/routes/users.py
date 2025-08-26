# backend/app/routes/users.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=schemas.UserMeResponse)
def me(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    def short(u: models.User) -> schemas.UserShort:
        return schemas.UserShort(id=u.id, name=u.name)

    followers = [short(rel.follower) for rel in user.followers]
    following = [short(rel.followee) for rel in user.following]
    return schemas.UserProfile(id=user.id, name=user.name, followers=followers, following=following)


@router.post("/{user_id}/follow", response_model=schemas.Result)
def follow(user_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if user_id == user.id:
        return {"result": True}
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    rel = db.query(models.Follow).filter(models.Follow.follower_id == user.id, models.Follow.followee_id == user_id).first()
    if not rel:
        rel = models.Follow(follower_id=user.id, followee_id=user_id)
        db.add(rel)
        db.commit()
    return {"result": True}


@router.delete("/{user_id}/follow", response_model=schemas.Result)
def unfollow(user_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rel = db.query(models.Follow).filter(models.Follow.follower_id == user.id, models.Follow.followee_id == user_id).first()
    if rel:
        db.delete(rel)
        db.commit()
    return {"result": True}
