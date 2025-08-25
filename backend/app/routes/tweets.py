from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.post("", response_model=schemas.TweetOut)
def create_tweet(
    tweet: schemas.TweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_tweet = models.Tweet(content=tweet.tweet_data, author_id=current_user.id)
    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)
    return schemas.TweetOut(
        id=new_tweet.id,
        content=new_tweet.content,
        created_at=new_tweet.created_at,
        author=current_user,
        attachments=[],
        likes=[],
    )


@router.post("/{tweet_id}/likes", response_model=schemas.LikeResponse)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    like = models.Like(user_id=current_user.id, tweet_id=tweet.id)
    db.add(like)
    db.commit()
    db.refresh(like)

    return schemas.LikeResponse(user_id=current_user.id, name=current_user.name)


@router.get("", response_model=schemas.FeedResponse)
def get_feed(db: Session = Depends(get_db)):
    tweets = db.query(models.Tweet).order_by(models.Tweet.created_at.desc()).all()
    return schemas.FeedResponse(
        tweets=[
            schemas.TweetOut(
                id=t.id,
                content=t.content,
                created_at=t.created_at,
                author=t.author,
                attachments=[m for m in t.medias],
                likes=[schemas.LikeResponse(user_id=l.user.id, name=l.user.name) for l in t.likes],
            )
            for t in tweets
        ]
    )
