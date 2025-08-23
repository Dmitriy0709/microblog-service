from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.utils import media_public_url

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


@router.post("/{tweet_id}/likes", response_model=schemas.LikeResponse)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not db_tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    existing = (
        db.query(models.Like)
        .filter(models.Like.tweet_id == tweet_id, models.Like.user_id == user.id)
        .first()
    )
    if existing:
        return {"tweet_id": tweet_id, "user_id": user.id}

    like = models.Like(tweet_id=tweet_id, user_id=user.id)
    db.add(like)
    db.commit()
    return {"tweet_id": tweet_id, "user_id": user.id}


@router.get("", response_model=schemas.FeedResponse)
def get_feed(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # показываем ленту только по тем, на кого подписан текущий пользователь
    followees = [
        f.followee_id
        for f in db.query(models.Follow).filter_by(follower_id=user.id).all()
    ]

    if not followees:
        return {"tweets": []}

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
                attachments=[media_public_url(m.stored_path) for m in t.medias],
                author=schemas.TweetAuthor(id=t.author.id, name=t.author.name),
                likes=[
                    schemas.TweetLike(user_id=l.user_id, name=l.user.name)
                    for l in t.likes
                ],
            )
            for t in tweets
        ]
    }
