from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


@router.post("", response_model=schemas.TweetCreateOut)
def create_tweet(
    tweet: schemas.TweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.TweetCreateOut:
    """
    Создать твит (с возможными медиа).
    """
    new_tweet = models.Tweet(content=tweet.tweet_data, author_id=current_user.id)
    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)

    return schemas.TweetCreateOut(tweet_id=new_tweet.id)


@router.post("/{tweet_id}/likes")
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Лайкнуть твит.
    """
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    like = models.Like(user_id=current_user.id, tweet_id=tweet.id)
    db.add(like)
    db.commit()
    return {"status": "liked"}


@router.get("", response_model=schemas.TweetsResponse)
def get_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.TweetsResponse:
    """
    Лента: показываем твиты только от тех, кого пользователь фоловит.
    """
    followee_ids = [f.followee_id for f in current_user.following]
    tweets = (
        db.query(models.Tweet)
        .filter(models.Tweet.author_id.in_(followee_ids))
        .order_by(models.Tweet.created_at.desc())
        .all()
    )

    return schemas.TweetsResponse(
        tweets=[
            schemas.TweetOut(
                id=t.id,
                content=t.content,
                created_at=t.created_at,
                author=schemas.UserOut(id=t.author.id, name=t.author.name),
                attachments=[],
                likes=[
                    schemas.LikeOut(user_id=l.user_id, name=l.user.name)
                    for l in t.likes
                ],
            )
            for t in tweets
        ]
    )
