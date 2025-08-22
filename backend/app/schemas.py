from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


# ---------- Базовые ----------

class Result(BaseModel):
    result: bool = True


# ---------- Media ----------

class MediaCreated(BaseModel):
    media_id: int
    url: str


# ---------- Tweets ----------

class TweetCreate(BaseModel):
    tweet_data: str = Field(..., min_length=1, max_length=280)
    tweet_media_ids: List[int] = []


class TweetAuthor(BaseModel):
    id: int
    name: str


class TweetLike(BaseModel):
    user_id: int
    name: str


class TweetOut(BaseModel):
    id: int
    content: str
    created_at: str
    author: TweetAuthor
    likes: List[TweetLike]
    attachments: List[str]


class TweetCreated(BaseModel):
    tweet_id: int


class TweetsResponse(BaseModel):
    result: bool = True
    tweets: List[TweetOut]


# ---------- Users ----------

class UserShort(BaseModel):
    id: int
    name: str


class UserProfile(BaseModel):
    id: int
    name: str
    followers: List[UserShort]
    following: List[UserShort]


class UserMeResponse(BaseModel):
    result: bool = True
    user: UserProfile
