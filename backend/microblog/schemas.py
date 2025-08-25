from typing import List
from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TweetBase(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserBase

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
    attachments: List[str] = []
    likes: List[LikeResponse] = []

    class Config:
        orm_mode = True


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] = []


class FeedResponse(BaseModel):
    tweets: List[TweetOut]
