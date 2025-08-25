from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from microblog import models, schemas
from microblog.database import SessionLocal

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=schemas.TweetOut)
def create_tweet(tweet: schemas.TweetCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).first()
    if not user:
        user = models.User(name="TestUser")
        db.add(user)
        db.commit()
        db.refresh(user)

    db_tweet = models.Tweet(content=tweet.tweet_data, author_id=user.id)
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)

    return schemas.TweetOut(
        id=db_tweet.id,
        content=db_tweet.content,
        created_at=db_tweet.created_at,
        author=user,
        attachments=[m.url for m in db_tweet.medias],
        likes=[schemas.LikeResponse(user_id=l.user.id, name=l.user.name) for l in db_tweet.likes],
    )


@router.post("/{tweet_id}/likes", response_model=schemas.LikeResponse)
def like_tweet(tweet_id: int, db: Session = Depends(get_db)):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    user = db.query(models.User).first()
    if not user:
        user = models.User(name="TestUser")
        db.add(user)
        db.commit()
        db.refresh(user)

    like = models.Like(user_id=user.id, tweet_id=tweet.id)
    db.add(like)
    db.commit()
    db.refresh(like)

    return schemas.LikeResponse(user_id=user.id, name=user.name)
