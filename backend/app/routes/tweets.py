from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, deps
from app.database import get_db

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.post("", response_model=schemas.TweetCreateOut)
def create_tweet(
    tweet: schemas.TweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Создание нового твита.
    """
    db_tweet = models.Tweet(
        content=tweet.tweet_data,
        author_id=current_user.id,
    )
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)

    # вложения (медиа)
    if tweet.tweet_media_ids:
        medias = (
            db.query(models.Media)
            .filter(models.Media.id.in_(tweet.tweet_media_ids))
            .all()
        )
        for m in medias:
            m.tweet_id = db_tweet.id
        db.commit()

    return {"tweet_id": db_tweet.id}


@router.post("/{tweet_id}/likes")
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Лайкнуть твит.
    """
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    # проверка, что лайка ещё нет
    existing_like = (
        db.query(models.Like)
        .filter(models.Like.tweet_id == tweet_id, models.Like.user_id == current_user.id)
        .first()
    )
    if not existing_like:
        like = models.Like(user_id=current_user.id, tweet_id=tweet_id)
        db.add(like)
        db.commit()

    return {"status": "ok"}


@router.get("", response_model=schemas.FeedResponse)
def get_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Лента текущего пользователя: твиты только от тех, на кого он подписан.
    """
    followees = (
        db.query(models.Follow.followee_id)
        .filter(models.Follow.follower_id == current_user.id)
        .subquery()
    )

    tweets = (
        db.query(models.Tweet)
        .filter(models.Tweet.author_id.in_(followees))
        .order_by(models.Tweet.created_at.desc())
        .all()
    )

    return {"tweets": tweets}
