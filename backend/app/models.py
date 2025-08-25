from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    api_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    tweets: Mapped[List["Tweet"]] = relationship(back_populates="author")
    likes: Mapped[List["Like"]] = relationship(back_populates="user")
    followers: Mapped[List["Follow"]] = relationship(
        foreign_keys="Follow.followee_id", back_populates="followee"
    )
    following: Mapped[List["Follow"]] = relationship(
        foreign_keys="Follow.follower_id", back_populates="follower"
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="tweets")

    likes: Mapped[List["Like"]] = relationship(back_populates="tweet")
    medias: Mapped[List["Media"]] = relationship(back_populates="tweet")


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String, nullable=False)

    tweet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tweets.id"))
    tweet: Mapped[Optional["Tweet"]] = relationship(back_populates="medias")


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    user: Mapped["User"] = relationship(back_populates="likes")
    tweet: Mapped["Tweet"] = relationship(back_populates="likes")


class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    followee_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    follower: Mapped["User"] = relationship(
        foreign_keys=[follower_id], back_populates="following"
    )
    followee: Mapped["User"] = relationship(
        foreign_keys=[followee_id], back_populates="followers"
    )
