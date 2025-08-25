from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.post("", response_model=schemas.TweetCreateOut)
def create_tweet(
    tweet: schemas.TweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Создать новый твит"""
    db_tweet = models.Tweet(
        content=tweet.tweet_data,
        author_id=current_user.id,
    )
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)

    if tweet.tweet_media_ids:
        medias = (
            db.query(models.Media)
            .filter(models.Media.id.in_(tweet.tweet_media_ids))
            .all()
        )
        db_tweet.medias.extend(medias)
        db.commit()

    return {"tweet_id": db_tweet.id}


@router.post("/{tweet_id}/likes", response_model=schemas.LikeResponse)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Поставить лайк на твит"""
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    like = (
        db.query(models.Like)
        .filter(models.Like.tweet_id == tweet_id, models.Like.user_id == current_user.id)
        .first()
    )
    if like:
        return {"user_id": current_user.id, "name": current_user.name}

    like = models.Like(user_id=current_user.id, tweet_id=tweet_id)
    db.add(like)
    db.commit()
    return {"user_id": current_user.id, "name": current_user.name}


@router.get("", response_model=schemas.FeedResponse)
def get_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Получить ленту текущего пользователя"""
    followees = (
        db.query(models.Follow.followee_id)
        .filter(models.Follow.follower_id == current_user.id)
        .all()
    )
    followee_ids = [f[0] for f in followees]

    if not followee_ids:
        return {"tweets": []}

    tweets = (
        db.query(models.Tweet)
        .filter(models.Tweet.author_id.in_(followee_ids))
        .order_by(models.Tweet.created_at.desc())
        .all()
    )

    feed: List[schemas.TweetOut] = []
    for t in tweets:
        feed.append(
            schemas.TweetOut(
                id=t.id,
                content=t.content,
                created_at=t.created_at,
                author={"id": t.author.id, "name": t.author.name},
                attachments=[m.url for m in t.medias],
                likes=[{"user_id": like.user.id, "name": like.user.name} for like in t.likes],
            )
        )

    return {"tweets": feed}
