from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, UniqueConstraint, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    api_key: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    # Аннотация отношений через typing.List + игнор для mypy
    tweets: List["Tweet"]  # type: ignore
    tweets = relationship(
        "Tweet",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    likes: List["Like"]  # type: ignore
    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    following: List["Follow"]  # type: ignore
    following = relationship(
        "Follow",
        back_populates="follower",
        foreign_keys="Follow.follower_id",
        cascade="all, delete-orphan",
    )
    followers: List["Follow"]  # type: ignore
    followers = relationship(
        "Follow",
        back_populates="followee",
        foreign_keys="Follow.followee_id",
        cascade="all, delete-orphan",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        default=datetime.utcnow,
    )

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: User = relationship("User", back_populates="tweets")

    likes: List["Like"]  # type: ignore
    likes = relationship(
        "Like",
        back_populates="tweet",
        cascade="all, delete-orphan",
    )
    medias: List["Media"]  # type: ignore
    medias = relationship(
        "Media",
        back_populates="tweet",
        cascade="all, delete-orphan",
    )


class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    followee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    follower: User = relationship(
        "User",
        back_populates="following",
        foreign_keys=[follower_id],
    )
    followee: User = relationship(
        "User",
        back_populates="followers",
        foreign_keys=[followee_id],
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_follower_followee"),
    )


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    tweet: Tweet = relationship("Tweet", back_populates="likes")
    user: User = relationship("User", back_populates="likes")

    __table_args__ = (
        UniqueConstraint("tweet_id", "user_id", name="uq_tweet_user_like"),
    )


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    tweet_id: Optional[int] = mapped_column(ForeignKey("tweets.id"), nullable=True)

    tweet: Optional[Tweet] = relationship("Tweet", back_populates="medias")
