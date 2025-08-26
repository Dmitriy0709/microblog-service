from datetime import datetime
import secrets

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # теперь API key генерируется автоматически
    api_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        default=lambda: secrets.token_hex(16),
    )

    tweets: Mapped[list["Tweet"]] = relationship(back_populates="author")
    likes: Mapped[list["Like"]] = relationship(back_populates="user")
    followers: Mapped[list["Follow"]] = relationship(
        back_populates="followed",
        foreign_keys="Follow.followed_id",
    )
    following: Mapped[list["Follow"]] = relationship(
        back_populates="follower",
        foreign_keys="Follow.follower_id",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # created_at теперь с дефолтом
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    author: Mapped["User"] = relationship(back_populates="tweets")
    likes: Mapped[list["Like"]] = relationship(back_populates="tweet")
    medias: Mapped[list["Media"]] = relationship(back_populates="tweet")


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), nullable=False)

    tweet: Mapped["Tweet"] = relationship(back_populates="medias")


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="likes")
    tweet: Mapped["Tweet"] = relationship(back_populates="likes")


class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    follower: Mapped["User"] = relationship(
        back_populates="following", foreign_keys=[follower_id]
    )
    followed: Mapped["User"] = relationship(
        back_populates="followers", foreign_keys=[followed_id]
    )
