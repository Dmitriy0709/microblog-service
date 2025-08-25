from typing import List
from datetime import datetime
from pydantic import BaseModel


# ---------------------------
# Users
# ---------------------------
class UserBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserMeResponse(UserBase):
    api_key: str


# ---------------------------
# Tweets
# ---------------------------
class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] = []


class TweetCreateOut(BaseModel):
    tweet_id: int


class LikeResponse(BaseModel):
    user_id: int
    name: str

    class Config:
        orm_mode = True


class TweetOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserBase
    attachments: List[str]
    likes: List[LikeResponse]

    class Config:
        orm_mode = True


class FeedResponse(BaseModel):
    tweets: List[TweetOut]


# ---------------------------
# Medias
# ---------------------------
class MediaCreated(BaseModel):
    media_id: int
    url: str
