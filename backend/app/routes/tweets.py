from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app import schemas, models
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.post("", response_model=schemas.TweetCreateOut)
def create_tweet(
    tweet: schemas.TweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_tweet = models.Tweet(content=tweet.tweet_data, author=current_user)
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)
    return {"tweet_id": db_tweet.id}


@router.post("/{tweet_id}/likes", response_model=schemas.LikeResponse)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tweet = db.get(models.Tweet, tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    like = models.Like(user=current_user, tweet=tweet)
    db.add(like)
    db.commit()
    db.refresh(like)

    return schemas.LikeResponse(user_id=current_user.id, name=current_user.name)


@router.get("", response_model=schemas.FeedResponse)
def get_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    stmt = select(models.Tweet).where(models.Tweet.author_id != current_user.id)
    tweets = db.scalars(stmt).all()

    return schemas.FeedResponse(
        tweets=[
            schemas.TweetOut(
                id=t.id,
                content=t.content,
                created_at=t.created_at,
                author=schemas.UserBase(id=t.author.id, name=t.author.name),
                attachments=[m.url for m in t.medias],
                likes=[
                    schemas.LikeResponse(user_id=l.user.id, name=l.user.name)
                    for l in t.likes
                ],
            )
            for t in tweets
        ]
    )
