from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# ------------------------
# Users
# ------------------------
class UserBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserMeResponse(BaseModel):
    id: int
    name: str
    api_key: str

    class Config:
        orm_mode = True


# ------------------------
# Medias
# ------------------------
class MediaCreate(BaseModel):
    url: str


class MediaCreated(BaseModel):
    id: int
    url: str

    class Config:
        orm_mode = True


# ------------------------
# Tweets
# ------------------------
class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] = []


class TweetCreateOut(BaseModel):
    tweet_id: int


class LikeOut(BaseModel):
    user_id: int
    name: str


class TweetOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserBase
    attachments: List[MediaCreated] = []
    likes: List[LikeOut] = []

    class Config:
        orm_mode = True


class FeedResponse(BaseModel):
    tweets: List[TweetOut]
