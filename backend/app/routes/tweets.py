# app/routes/tweets.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.schemas as schemas
import app.models as models
from app.database import get_db
from app.deps import get_current_user
from app.utils import media_public_url

router = APIRouter()


@router.post("/tweets", response_model=schemas.TweetCreateOut)
def create_tweet(
    tweet: schemas.TweetCreateIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    new_tweet = models.Tweet(
        content=tweet.tweet_data,
        user_id=user.id,
    )
    db.add(new_tweet)
    db.flush()

    # прикрепляем медиа, если есть
    if tweet.tweet_media_ids:
        medias = (
            db.query(models.Media)
            .filter(models.Media.id.in_(tweet.tweet_media_ids))
            .all()
        )
        for m in medias:
            m.tweet_id = new_tweet.id

    db.commit()
    db.refresh(new_tweet)
    return {"tweet_id": new_tweet.id}


@router.post("/tweets/{tweet_id}/likes", response_model=schemas.OK)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    tweet = db.query(models.Tweet).filter_by(id=tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    # проверим, что лайк не дублируется
    exists = (
        db.query(models.Like)
        .filter_by(tweet_id=tweet_id, user_id=user.id)
        .first()
    )
    if exists:
        return {"ok": True}

    like = models.Like(tweet_id=tweet_id, user_id=user.id)
    db.add(like)
    db.commit()
    return {"ok": True}


@router.get("/tweets", response_model=schemas.TweetFeed)
def get_feed(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # на кого подписан текущий пользователь
    followees = (
        db.query(models.Follow.followee_id)
        .filter(models.Follow.follower_id == user.id)
        .subquery()
    )

    # только твиты followees, не свои
    tweets = (
        db.query(models.Tweet)
        .filter(models.Tweet.user_id.in_(followees))
        .order_by(models.Tweet.created_at.desc())
        .all()
    )

    return {
        "tweets": [
            schemas.TweetOut(
                id=t.id,
                content=t.content,
                created_at=t.created_at,
                attachments=[media_public_url(m.stored_path) for m in t.medias],
                author=schemas.TweetAuthor(id=t.author.id, name=t.author.name),
                likes=[
                    schemas.TweetLike(user_id=like.user.id, name=like.user.name)
                    for like in t.likes
                ],
            )
            for t in tweets
        ]
    }
