from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    api_key = Column(String(200), nullable=False, unique=True)

    tweets: List["Tweet"]  # type: ignore
    tweets = relationship("Tweet", back_populates="author", cascade="all, delete-orphan")

    likes: List["Like"]  # type: ignore
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")

    following: List["Follow"]  # type: ignore
    following = relationship(
        "Follow", back_populates="follower", foreign_keys="Follow.follower_id", cascade="all, delete-orphan"
    )

    followers: List["Follow"]  # type: ignore
    followers = relationship(
        "Follow", back_populates="followee", foreign_keys="Follow.followee_id", cascade="all, delete-orphan"
    )

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
        default=datetime.utcnow,
    )
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author: User  # type: ignore
    author = relationship("User", back_populates="tweets")

    likes: List["Like"]  # type: ignore
    likes = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")

    medias: List["Media"]  # type: ignore
    medias = relationship("Media", back_populates="tweet", cascade="all, delete-orphan")

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followee_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    follower: User  # type: ignore
    follower = relationship("User", back_populates="following", foreign_keys=[follower_id])

    followee: User  # type: ignore
    followee = relationship("User", back_populates="followers", foreign_keys=[followee_id])

    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_follower_followee"),
    )

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tweet: Tweet  # type: ignore
    tweet = relationship("Tweet", back_populates="likes")

    user: User  # type: ignore
    user = relationship("User", back_populates="likes")

    __table_args__ = (
        UniqueConstraint("tweet_id", "user_id", name="uq_tweet_user_like"),
    )

class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=True)

    tweet: Optional[Tweet]  # type: ignore
    tweet = relationship("Tweet", back_populates="medias")
