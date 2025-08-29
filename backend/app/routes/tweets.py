from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any

from ..database import get_db
from ..models import Tweet, Like, User
from ..schemas import TweetOut, TweetCreate, TweetCreated, TweetLike, TweetAuthor, Result, TweetsResponse
from ..deps import get_current_user

router = APIRouter(prefix="/api/tweets", tags=["tweets"])

@router.post("", response_model=TweetCreated)
def create_tweet(
    payload: TweetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TweetCreated:
    tweet = Tweet(content=payload.tweet_data, author_id=current_user.id)
    if tweet.created_at is None:
        from datetime import datetime, timezone
        tweet.created_at = datetime.now(timezone.utc)
    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return TweetCreated(tweet_id=int(tweet.id))

@router.get("", response_model=TweetsResponse)
def get_tweets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> TweetsResponse:
    following_ids = [f.followee_id for f in user.following] + [user.id]  # type: ignore[attr-defined]
    tweets = (
        db.query(Tweet)
        .filter(Tweet.author_id.in_(following_ids))
        .order_by(Tweet.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result: List[TweetOut] = []
    for tw in tweets:
        result.append(
            TweetOut(
                id=int(tw.id),
                content=str(tw.content),
                created_at=tw.created_at,  # type: ignore[arg-type]
                author=TweetAuthor(id=int(tw.author.id), name=str(tw.author.name)),
                likes=[TweetLike(user_id=int(lk.user.id), name=str(lk.user.name)) for lk in tw.likes],
                attachments=[m.url for m in tw.medias]
            )
        )
    return TweetsResponse(tweets=result)

@router.post("/{tweet_id}/likes", response_model=Result)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Result:
    tw = db.query(Tweet).filter(Tweet.id == tweet_id).first()
    if not tw:
        raise HTTPException(status_code=404, detail="Tweet not found")
    existing = db.query(Like).filter(Like.tweet_id == tweet_id, Like.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already liked")
    like = Like(tweet_id=tweet_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    return Result(result=True)

@router.delete("/{tweet_id}/likes", response_model=Result)
def unlike_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Result:
    lk = db.query(Like).filter(Like.tweet_id == tweet_id, Like.user_id == current_user.id).first()
    if not lk:
        raise HTTPException(status_code=404, detail="Like not found")
    db.delete(lk)
    db.commit()
    return Result(result=True)
