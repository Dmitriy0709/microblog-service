# backend/app/schemas.py
from __future__ import annotations

from typing import List
from datetime import datetime
from pydantic import BaseModel


class Result(BaseModel):
    result: bool = True


class UserShort(BaseModel):
    id: int
    name: str


class UserProfile(BaseModel):
    id: int
    name: str
    followers: List[UserShort] = []
    following: List[UserShort] = []


# backward-compatible alias expected by some routes/tests
UserMeResponse = UserProfile


class MediaCreated(BaseModel):
    id: int
    url: str


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] = []


# aliases expected earlier
TweetCreateIn = TweetCreate
TweetCreateOut = "TweetCreated"  # placeholder string to avoid circular; not used in validation


class TweetCreated(BaseModel):
    tweet_id: int


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
    attachments: List[str] = []
    author: TweetAuthor
    likes: List[TweetLike] = []


class TweetsResponse(BaseModel):
    tweets: List[TweetOut] = []


# Like response alias
LikeResponse = Result
