from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# ---------- Users ----------

class UserBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserMeResponse(UserBase):
    api_key: str


# ---------- Medias ----------

class MediaCreated(BaseModel):
    id: int
    url: str

    class Config:
        orm_mode = True


# ---------- Tweets ----------

class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int]


class TweetCreateOut(BaseModel):
    tweet_id: int


class TweetLike(BaseModel):
    user_id: int
    name: str


class TweetAuthor(BaseModel):
    id: int
    name: str


class TweetResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    attachments: List[str]
    author: TweetAuthor
    likes: List[TweetLike]

    class Config:
        orm_mode = True


class FeedResponse(BaseModel):
    tweets: List[TweetResponse]
