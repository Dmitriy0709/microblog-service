from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    api_key: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    tweets: Mapped[List[Tweet]] = relationship(
        "Tweet",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    likes: Mapped[List[Like]] = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    following: Mapped[List[Follow]] = relationship(
        "Follow",
        back_populates="follower",
        foreign_keys="Follow.follower_id",
        cascade="all, delete-orphan",
    )
    followers: Mapped[List[Follow]] = relationship(
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
    author: Mapped[User] = relationship("User", back_populates="tweets")

    likes: Mapped[List[Like]] = relationship(
        "Like",
        back_populates="tweet",
        cascade="all, delete-orphan",
    )
    medias: Mapped[List[Media]] = relationship(
        "Media",
        back_populates="tweet",
        cascade="all, delete-orphan",
    )


class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    followee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    follower: Mapped[User] = relationship(
        "User",
        back_populates="following",
        foreign_keys=[follower_id],
    )
    followee: Mapped[User] = relationship(
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

    tweet: Mapped[Tweet] = relationship("Tweet", back_populates="likes")
    user: Mapped[User] = relationship("User", back_populates="likes")

    __table_args__ = (
        UniqueConstraint("tweet_id", "user_id", name="uq_tweet_user_like"),
    )


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    tweet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tweets.id"), nullable=True)

    tweet: Mapped[Optional[Tweet]] = relationship("Tweet", back_populates="medias")
