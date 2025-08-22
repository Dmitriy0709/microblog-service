from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=schemas.UserMeResponse)
def me(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    def u_short(u: models.User) -> schemas.UserShort:
        return schemas.UserShort(id=u.id, name=u.name)

    followers = [u_short(f.follower) for f in user.followers]
    following = [u_short(f.followee) for f in user.following]

    return {
        "result": True,
        "user": schemas.UserProfile(id=user.id, name=user.name, followers=followers, following=following),
    }

@router.get("/{user_id}", response_model=schemas.UserMeResponse)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    def u_short(u: models.User) -> schemas.UserShort:
        return schemas.UserShort(id=u.id, name=u.name)

    followers = [u_short(f.follower) for f in user.followers]
    following = [u_short(f.followee) for f in user.following]

    return {
        "result": True,
        "user": schemas.UserProfile(id=user.id, name=user.name, followers=followers, following=following),
    }

@router.post("/{user_id}/follow", response_model=schemas.Result)
def follow(user_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if user_id == user.id:
        return {"result": True}
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    exists = (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == user.id, models.Follow.followee_id == user_id)
        .first()
    )
    if not exists:
        db.add(models.Follow(follower_id=user.id, followee_id=user_id))
        db.commit()
    return {"result": True}

@router.delete("/{user_id}/follow", response_model=schemas.Result)
def unfollow(user_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rel = (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == user.id, models.Follow.followee_id == user_id)
        .first()
    )
    if rel:
        db.delete(rel)
        db.commit()
    return {"result": True}
