from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "users"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    api_key = Column(String(200), nullable=False, unique=True)

    tweets = relationship("Tweet", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    following = relationship(
        "Follow", back_populates="follower", foreign_keys="Follow.follower_id", cascade="all, delete-orphan"
    )
    followers = relationship(
        "Follow", back_populates="followee", foreign_keys="Follow.followee_id", cascade="all, delete-orphan"
    )

class Tweet(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "tweets"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
        default=datetime.utcnow,
    )
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("User", back_populates="tweets")
    likes = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")
    medias = relationship("Media", back_populates="tweet", cascade="all, delete-orphan")

class Follow(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "follows"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followee_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    follower = relationship("User", back_populates="following", foreign_keys=[follower_id])
    followee = relationship("User", back_populates="followers", foreign_keys=[followee_id])

    __table_args__ = (UniqueConstraint("follower_id", "followee_id", name="uq_follower_followee"),)

class Like(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "likes"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tweet = relationship("Tweet", back_populates="likes")
    user = relationship("User", back_populates="likes")

    __table_args__ = (UniqueConstraint("tweet_id", "user_id", name="uq_tweet_user_like"),)

class Media(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "medias"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=True)

    tweet = relationship("Tweet", back_populates="medias")
