# backend/app/models.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    api_key = Column(String(200), nullable=False, unique=True)

    tweets = relationship("Tweet", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    following = relationship(
        "Follow",
        back_populates="follower",
        foreign_keys="Follow.follower_id",
        cascade="all, delete-orphan",
    )
    followers = relationship(
        "Follow",
        back_populates="followee",
        foreign_keys="Follow.followee_id",
        cascade="all, delete-orphan",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    # DB server default and python default fallback
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now(), default=datetime.utcnow)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="tweets")

    likes = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")
    medias = relationship("Media", back_populates="tweet", cascade="all, delete-orphan")


class Follow(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followee_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    follower = relationship("User", back_populates="following", foreign_keys=[follower_id])
    followee = relationship("User", back_populates="followers", foreign_keys=[followee_id])

    __table_args__ = (UniqueConstraint("follower_id", "followee_id", name="uq_follower_followee"),)


class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tweet = relationship("Tweet", back_populates="likes")
    user = relationship("User", back_populates="likes")

    __table_args__ = (UniqueConstraint("tweet_id", "user_id", name="uq_tweet_user_like"),)


class Media(Base):
    __tablename__ = "medias"
    id = Column(Integer, primary_key=True)
    # URL/public path to media
    url = Column(String(500), nullable=False)
    # allow null until associated with a tweet
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=True)

    tweet = relationship("Tweet", back_populates="medias")
