from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


# ==== Media ====
class MediaCreated(BaseModel):
    media_id: int


# ==== Tweets: create ====
class TweetCreate(BaseModel):
    # тесты шлют поле "tweet_data"
    tweet_data: str = Field(..., min_length=1)
    tweet_media_ids: list[int] = []


class TweetCreateOut(BaseModel):
    tweet_id: int


# ==== Tweets: feed ====
class TweetAuthor(BaseModel):
    id: int
    name: str


class TweetLike(BaseModel):
    user_id: int
    name: str


class TweetOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    attachments: list[str]
    author: TweetAuthor
    likes: list[TweetLike] = []


class FeedResponse(BaseModel):
    tweets: list[TweetOut]


# ==== Likes ====
class LikeResponse(BaseModel):
    tweet_id: int
    user_id: int


# ==== Users ====
class UserMeResponse(BaseModel):
    id: int
    name: str
