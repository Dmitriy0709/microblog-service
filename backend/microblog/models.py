from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    tweets: Mapped[list["Tweet"]] = relationship("Tweet", back_populates="author")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user")
    following: Mapped[list["Follow"]] = relationship(
        "Follow", foreign_keys="[Follow.follower_id]", back_populates="follower"
    )
    followers: Mapped[list["Follow"]] = relationship(
        "Follow", foreign_keys="[Follow.following_id]", back_populates="following"
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship("User", back_populates="tweets")

    likes: Mapped[list["Like"]] = relationship("Like", back_populates="tweet")
    medias: Mapped[list["Media"]] = relationship("Media", back_populates="tweet")


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    tweet: Mapped["Tweet"] = relationship("Tweet", back_populates="medias")


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    user: Mapped["User"] = relationship("User", back_populates="likes")
    tweet: Mapped["Tweet"] = relationship("Tweet", back_populates="likes")


class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following: Mapped["User"] = relationship("User", foreign_keys=[following_id], back_populates="followers")
