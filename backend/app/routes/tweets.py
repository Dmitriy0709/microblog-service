from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


# ------------------------
# Create Tweet
# ------------------------
@router.post("", response_model=schemas.TweetCreateOut)
def create_tweet(
    tweet: schemas.TweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_tweet = models.Tweet(content=tweet.tweet_data, author_id=current_user.id)
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)

    # прикрепляем медиа, если есть
    if tweet.tweet_media_ids:
        medias = db.query(models.Media).filter(models.Media.id.in_(tweet.tweet_media_ids)).all()
        for m in medias:
            db_tweet.attachments.append(m)
        db.commit()

    return {"tweet_id": db_tweet.id}


# ------------------------
# Like Tweet
# ------------------------
@router.post("/{tweet_id}/likes")
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    like = models.Like(user_id=current_user.id, tweet_id=tweet_id)
    db.add(like)
    db.commit()
    return {"message": "Liked"}


# ------------------------
# Feed
# ------------------------
@router.get("", response_model=schemas.FeedResponse)
def get_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # показываем только твиты тех, на кого подписан
    follows = db.query(models.Follow).filter(models.Follow.follower_id == current_user.id).all()
    followee_ids = [f.followee_id for f in follows]

    tweets = []
    if followee_ids:
        tweets = (
            db.query(models.Tweet)
            .filter(models.Tweet.author_id.in_(followee_ids))
            .order_by(models.Tweet.created_at.desc())
            .all()
        )

    return {"tweets": tweets}
