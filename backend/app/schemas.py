from typing import List
from datetime import datetime
from pydantic import BaseModel


# ===== USERS =====
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


# ===== TWEETS =====
class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] = []


class TweetCreateOut(BaseModel):
    tweet_id: int


class LikeResponse(BaseModel):
    user_id: int
    name: str


class TweetOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserBase
    attachments: List[str]
    likes: List[LikeResponse]


class FeedResponse(BaseModel):
    tweets: List[TweetOut]


# ===== MEDIAS =====
class MediaCreated(BaseModel):
    media_id: int
    url: str
