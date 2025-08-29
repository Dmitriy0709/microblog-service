from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..deps import get_current_user
from ..database import get_db
from ..models import User, Follow
from ..schemas import UserProfile, UserShort

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserProfile)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserProfile:
    fresh_user = db.query(User).filter(User.id == current_user.id).first()
    if not fresh_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    followers_follows = db.query(Follow).filter(Follow.followee_id == fresh_user.id).all()
    followers: List[UserShort] = [
        UserShort(id=int(f.follower_id), name=str(f.follower.name))
        for f in followers_follows
    ]

    following_follows = db.query(Follow).filter(Follow.follower_id == fresh_user.id).all()
    following: List[UserShort] = [
        UserShort(id=int(f.followee_id), name=str(f.followee.name))
        for f in following_follows
    ]

    return UserProfile(
        id=int(fresh_user.id),
        name=str(fresh_user.name),
        followers=followers,
        following=following
    )

@router.get("/{user_id}", response_model=UserProfile)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
) -> UserProfile:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    followers_follows = db.query(Follow).filter(Follow.followee_id == user.id).all()
    followers: List[UserShort] = [
        UserShort(id=int(f.follower_id), name=str(f.follower.name))
        for f in followers_follows
    ]

    following_follows = db.query(Follow).filter(Follow.follower_id == user.id).all()
    following: List[UserShort] = [
        UserShort(id=int(f.followee_id), name=str(f.followee.name))
        for f in following_follows
    ]

    return UserProfile(
        id=int(user.id),
        name=str(user.name),
        followers=followers,
        following=following
    )
