from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    Text,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


# === Базовый класс декларативной модели ===
class Base(DeclarativeBase):
    pass


# === Пользователи ===
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    api_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    tweets: Mapped[List["Tweet"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    likes: Mapped[List["Like"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    following: Mapped[List["Follow"]] = relationship(
        back_populates="follower",
        foreign_keys="Follow.follower_id",
        cascade="all, delete-orphan",
    )
    followers: Mapped[List["Follow"]] = relationship(
        back_populates="followee",
        foreign_keys="Follow.followee_id",
        cascade="all, delete-orphan",
    )


# === Твиты ===
class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    author: Mapped["User"] = relationship(back_populates="tweets")

    likes: Mapped[List["Like"]] = relationship(
        back_populates="tweet", cascade="all, delete-orphan"
    )
    medias: Mapped[List["Media"]] = relationship(
        back_populates="tweet", cascade="all, delete-orphan"
    )


# === Медиа ===
class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    stored_path: Mapped[str] = mapped_column(String, nullable=False)

    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"))
    tweet: Mapped["Tweet"] = relationship(back_populates="medias")


# === Лайки ===
class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="likes")
    tweet: Mapped["Tweet"] = relationship(back_populates="likes")

    __table_args__ = (
        UniqueConstraint("user_id", "tweet_id", name="uq_like_user_tweet"),
    )


# === Подписки ===
class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    followee_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    follower: Mapped["User"] = relationship(
        back_populates="following", foreign_keys=[follower_id]
    )
    followee: Mapped["User"] = relationship(
        back_populates="followers", foreign_keys=[followee_id]
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_follows_pair"),
    )
