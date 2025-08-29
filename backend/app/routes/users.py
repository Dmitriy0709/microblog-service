from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..deps import get_current_user
from ..database import get_db
from ..models import User, Follow
from ..schemas import UserProfile, UserShort, Result

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
def get_user_profile(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
) -> UserProfile:
    """Возвращает профиль текущего пользователя."""
    # Получаем актуальные данные из БД
    fresh_user = db.query(User).filter(User.id == user.id).first()
    if not fresh_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Получаем подписчиков
    followers_follows = db.query(Follow).filter(Follow.followee_id == fresh_user.id).all()
    followers = [UserShort(id=f.follower_id, name=f.follower.name) for f in followers_follows]

    # Получаем подписки
    following_follows = db.query(Follow).filter(Follow.follower_id == fresh_user.id).all()
    following = [UserShort(id=f.followee_id, name=f.followee.name) for f in following_follows]

    return UserProfile(
        id=fresh_user.id,
        name=fresh_user.name,
        followers=followers,
        following=following
    )


@router.get("/{user_id}", response_model=UserProfile)
def get_user_by_id(
        user_id: int,
        db: Session = Depends(get_db)
) -> UserProfile:
    """Возвращает профиль пользователя по ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Получаем подписчиков
    followers_follows = db.query(Follow).filter(Follow.followee_id == user.id).all()
    followers = [UserShort(id=f.follower_id, name=f.follower.name) for f in followers_follows]

    # Получаем подписки
    following_follows = db.query(Follow).filter(Follow.follower_id == user.id).all()
    following = [UserShort(id=f.followee_id, name=f.followee.name) for f in following_follows]

    return UserProfile(
        id=user.id,
        name=user.name,
        followers=followers,
        following=following
    )


@router.post("/{user_id}/follow", response_model=Result)
def follow_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Result:
    """Подписаться на пользователя."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя подписаться на самого себя")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем, не подписан ли уже
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followee_id == user_id
    ).first()

    if existing_follow:
        raise HTTPException(status_code=400, detail="Уже подписан")

    follow = Follow(follower_id=current_user.id, followee_id=user_id)
    db.add(follow)
    db.commit()

    return Result(result=True)


@router.delete("/{user_id}/follow", response_model=Result)
def unfollow_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Result:
    """Отписаться от пользователя."""
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followee_id == user_id
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    db.delete(follow)
    db.commit()

    return Result(result=True)
