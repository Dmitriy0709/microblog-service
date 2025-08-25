from datetime import datetime
from typing import List
from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] = []


class MediaOut(BaseModel):
    id: int
    url: str

    class Config:
        orm_mode = True


class LikeResponse(BaseModel):
    user_id: int
    name: str


class TweetOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserBase
    attachments: List[MediaOut] = []
    likes: List[LikeResponse] = []

    class Config:
        orm_mode = True


class FeedResponse(BaseModel):
    tweets: List[TweetOut]
