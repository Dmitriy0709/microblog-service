from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, utils
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.post("", response_model=schemas.TweetCreateOut)
def create_tweet(
    tweet: schemas.TweetCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_tweet = models.Tweet(content=tweet.tweet_data, author_id=user.id)
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)

    # Медиафайлы, если есть
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
    user: models.User = Depends(get_current_user),
):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    existing_like = (
        db.query(models.Like)
        .filter(models.Like.tweet_id == tweet_id, models.Like.user_id == user.id)
        .first()
    )
    if existing_like:
        return {"status": "already liked"}

    like = models.Like(tweet_id=tweet_id, user_id=user.id)
    db.add(like)
    db.commit()
    return {"status": "liked"}


@router.get("", response_model=schemas.FeedResponse)
def get_feed(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Получаем твиты только от тех, на кого подписан текущий пользователь
    followees = db.query(models.Follow.followee_id).filter(
        models.Follow.follower_id == user.id
    )
    tweets = (
        db.query(models.Tweet)
        .filter(models.Tweet.author_id.in_(followees))
        .order_by(models.Tweet.created_at.desc())
        .all()
    )

    return {
        "tweets": [
            schemas.TweetOut(
                id=t.id,
                content=t.content,
                created_at=t.created_at,
                attachments=[utils.media_public_url(m.stored_path) for m in t.medias],
                author=schemas.TweetAuthor(id=t.author.id, name=t.author.name),
                likes=[
                    schemas.TweetLike(user_id=l.user_id, name=l.user.name)
                    for l in t.likes
                ],
            )
            for t in tweets
        ]
    }
