from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..deps import get_current_user, get_db
from .. import models, schemas
from ..utils import media_public_url

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.post("", response_model=schemas.TweetCreated)
def create_tweet(
    payload: schemas.TweetCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    tweet = models.Tweet(content=payload.tweet_data, author_id=user.id)
    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    if payload.tweet_media_ids:
        for mid in payload.tweet_media_ids:
            media = db.query(models.Media).filter(models.Media.id == mid).first()
            if media:
                media.tweet_id = tweet.id
        db.commit()

    return {"result": True, "tweet_id": tweet.id}


@router.delete("/{tweet_id}", response_model=schemas.Result)
def delete_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    if tweet.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete others' tweets",
        )
    db.delete(tweet)
    db.commit()
    return {"result": True}


@router.post("/{tweet_id}/likes", response_model=schemas.Result)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    already = (
        db.query(models.Like)
        .filter(models.Like.user_id == user.id, models.Like.tweet_id == tweet_id)
        .first()
    )
    if already:
        return {"result": True}

    like = models.Like(user_id=user.id, tweet_id=tweet_id)
    db.add(like)
    db.commit()
    return {"result": True}


@router.delete("/{tweet_id}/likes", response_model=schemas.Result)
def unlike_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    like = (
        db.query(models.Like)
        .filter(models.Like.user_id == user.id, models.Like.tweet_id == tweet_id)
        .first()
    )
    if like:
        db.delete(like)
        db.commit()
    return {"result": True}


@router.get("", response_model=schemas.TweetsResponse)
def get_feed(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    following_ids = [f.followee_id for f in user.following]

    tweets = (
        db.query(models.Tweet)
        .filter(models.Tweet.author_id.in_(following_ids + [user.id]))
        .outerjoin(models.Like)
        .group_by(models.Tweet.id)
        .order_by(func.count(models.Like.id).desc())
        .all()
    )

    tweets_out = [
        schemas.TweetOut(
            id=t.id,
            content=t.content,
            created_at=t.created_at.isoformat(),  # 👈 добавлено
            attachments=[media_public_url(m.stored_path) for m in t.medias],
            author=schemas.TweetAuthor(id=t.author.id, name=t.author.name),
            likes=[
                schemas.TweetLike(user_id=like.user_id, name=like.user.name)
                for like in t.likes
            ],
        )
        for t in tweets
    ]

    return {"result": True, "tweets": tweets_out}
