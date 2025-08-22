from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# ---------- Users ----------
class UserBase(BaseModel):
    id: int
    name: str


class UserOut(UserBase):
    pass


class UserMeResponse(BaseModel):
    id: int
    name: str
    api_key: str


# ---------- Media ----------
class MediaCreate(BaseModel):
    media_url: str


class MediaCreated(BaseModel):
    id: int
    media_url: str


# ---------- Tweets ----------
class TweetBase(BaseModel):
    content: str


class TweetCreate(TweetBase):
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
    author: UserOut
    attachments: List[MediaCreated] = []
    likes: List[LikeOut] = []


class FeedResponse(BaseModel):
    tweets: List[TweetOut]
