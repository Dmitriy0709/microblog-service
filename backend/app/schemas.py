from pydantic import BaseModel
from datetime import datetime
from typing import List


# -------- USERS --------
class UserBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserMeResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# -------- TWEETS --------
class TweetAuthor(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TweetLike(BaseModel):
    user_id: int
    name: str

    class Config:
        orm_mode = True


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] = []


class TweetCreateOut(BaseModel):
    tweet_id: int


class TweetOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    attachments: List[str]
    author: TweetAuthor
    likes: List[TweetLike]

    class Config:
        orm_mode = True


class FeedResponse(BaseModel):
    tweets: List[TweetOut]


# -------- MEDIAS --------
class MediaCreated(BaseModel):
    media_id: int
