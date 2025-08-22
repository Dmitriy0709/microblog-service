from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Integer,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    api_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    tweets: Mapped[List[Tweet]] = relationship("Tweet", back_populates="author")
    likes: Mapped[List[Like]] = relationship("Like", back_populates="user")
    followers: Mapped[List[Follow]] = relationship(
        "Follow", back_populates="followee", foreign_keys="Follow.followee_id"
    )
    following: Mapped[List[Follow]] = relationship(
        "Follow", back_populates="follower", foreign_keys="Follow.follower_id"
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped[User] = relationship("User", back_populates="tweets")
    likes: Mapped[List[Like]] = relationship("Like", back_populates="tweet")
    medias: Mapped[List[Media]] = relationship("Media", back_populates="tweet")


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stored_path: Mapped[str] = mapped_column(String(200), nullable=False)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    tweet: Mapped[Tweet] = relationship("Tweet", back_populates="medias")


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    user: Mapped[User] = relationship("User", back_populates="likes")
    tweet: Mapped[Tweet] = relationship("Tweet", back_populates="likes")

    __table_args__ = (UniqueConstraint("user_id", "tweet_id", name="uq_user_tweet"),)


class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    followee_id: Mapped[int] = mapped_column
