# backend/app/routes/tweets.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..database import get_db
from .. import models, schemas
from ..utils import media_public_url

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.post("", response_model=schemas.TweetCreated)
def create_tweet(payload: schemas.TweetCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # create tweet
    tweet = models.Tweet(content=payload.tweet_data, author_id=user.id)
    # ensure python-level created_at if DB doesn't set server_default
    if tweet.created_at is None:
        from datetime import datetime
        tweet.created_at = datetime.utcnow()

    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    # attach medias if provided
    if payload.tweet_media_ids:
        medias = db.query(models.Media).filter(models.Media.id.in_(payload.tweet_media_ids)).all()
        for m in medias:
            m.tweet_id = tweet.id
            db.add(m)
        db.commit()

    return {"tweet_id": tweet.id}


@router.post("/{tweet_id}/likes", response_model=schemas.Result)
def like_tweet(tweet_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    existing = db.query(models.Like).filter(models.Like.tweet_id == tweet_id, models.Like.user_id == user.id).first()
    if not existing:
        like = models.Like(tweet_id=tweet_id, user_id=user.id)
        db.add(like)
        db.commit()
    return {"result": True}


@router.delete("/{tweet_id}/likes", response_model=schemas.Result)
def unlike_tweet(tweet_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    like = db.query(models.Like).filter(models.Like.tweet_id == tweet_id, models.Like.user_id == user.id).first()
    if like:
        db.delete(like)
        db.commit()
    return {"result": True}


@router.get("", response_model=schemas.TweetsResponse)
def get_feed(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # feed: tweets by users current user follows
    following_ids = [f.followee_id for f in user.following]
    if not following_ids:
        return {"tweets": []}

    tweets_q = db.query(models.Tweet).filter(models.Tweet.author_id.in_(following_ids)).order_by(models.Tweet.created_at.desc()).all()

    out = []
    for t in tweets_q:
        out.append(
            schemas.TweetOut(
                id=t.id,
                content=t.content,
                created_at=t.created_at,
                attachments=[media_public_url(m.url) for m in t.medias],
                author=schemas.TweetAuthor(id=t.author.id, name=t.author.name),
                likes=[schemas.TweetLike(user_id=lk.user.id, name=lk.user.name) for lk in t.likes],
            )
        )
    return {"tweets": out}
