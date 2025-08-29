from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Tweet, User
from ..schemas import TweetOut, TweetCreate, Result, TweetLike, TweetAuthor
from ..deps import get_current_user

router = APIRouter(prefix="/api/tweets", tags=["tweets"])

@router.post("", response_model=Result)
def create_tweet(
    payload: TweetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Result:
    tweet = Tweet(content=payload.tweet_data, author_id=current_user.id)
    if tweet.created_at is None:
        from datetime import datetime, timezone
        tweet.created_at = datetime.now(timezone.utc)
    db.add(tweet)
    db.commit()
    return Result(result=True)

@router.get("", response_model=List[TweetOut])
def get_tweets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[TweetOut]:
    following_ids = [f.followee_id for f in user.following] + [user.id]
    tweets = (
        db.query(Tweet)
        .filter(Tweet.author_id.in_(following_ids))
        .order_by(Tweet.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result: List[TweetOut] = []
    for tweet in tweets:
        result.append(
            TweetOut(
                id=int(tweet.id),
                content=str(tweet.content),
                created_at=tweet.created_at, # type: ignore[arg-type]
                author=TweetAuthor(id=int(tweet.author.id), name=str(tweet.author.name)),
                likes=[
                    TweetLike(user_id=int(lk.user.id), name=str(lk.user.name))
                    for lk in tweet.likes
                ],
                attachments=[m.url for m in tweet.medias]
            )
        )
    return result
