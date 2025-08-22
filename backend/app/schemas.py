from __future__ import annotations

from datetime import datetime
from typing import List
from pydantic import BaseModel


# ---------- Users ----------

class UserCreate(BaseModel):
    name: str


class UserOut(BaseModel):
    id: int
    name: str


# ---------- Medias ----------

class MediaUploadIn(BaseModel):
    filename: str


class MediaCreated(BaseModel):
    media_id: int
    url: str  # может быть upload_url или готовый путь


# ---------- Tweets ----------

class TweetCreateIn(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int]


class TweetCreateOut(BaseModel):
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
    attachments: List[str]
    author: TweetAuthor
    likes: List[TweetLike]


class TweetFeed(BaseModel):
    tweets: List[TweetOut]


# ---------- Generic ----------

class OK(BaseModel):
    ok: bool
