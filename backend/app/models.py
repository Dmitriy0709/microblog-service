from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

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

if TYPE_CHECKING:
    from sqlalchemy.orm import RelationshipProperty

Base = declarative_base()

class User(Base):  # type: ignore[misc]
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    api_key = Column(String(200), nullable=False, unique=True)

    tweets: RelationshipProperty[List[Tweet]] = relationship("Tweet", back_populates="author", cascade="all, delete-orphan")  # type: ignore[assignment]
    likes: RelationshipProperty[List[Like]] = relationship("Like", back_populates="user", cascade="all, delete-orphan")  # type: ignore[assignment]
    following: RelationshipProperty[List[Follow]] = relationship(
        "Follow", back_populates="follower", foreign_keys="Follow.follower_id", cascade="all, delete-orphan"
    )  # type: ignore[assignment]
    followers: RelationshipProperty[List[Follow]] = relationship(
        "Follow", back_populates="followee", foreign_keys="Follow.followee_id", cascade="all, delete-orphan"
    )  # type: ignore[assignment]

class Tweet(Base):  # type: ignore[misc]
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.current_timestamp(), default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author: RelationshipProperty[User] = relationship("User", back_populates="tweets")  # type: ignore[assignment]
    likes: RelationshipProperty[List[Like]] = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")  # type: ignore[assignment]
    medias: RelationshipProperty[List[Media]] = relationship("Media", back_populates="tweet", cascade="all, delete-orphan")  # type: ignore[assignment]

class Follow(Base):  # type: ignore[misc]
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followee_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    follower: RelationshipProperty[User] = relationship("User", back_populates="following", foreign_keys=[follower_id])  # type: ignore[assignment]
    followee: RelationshipProperty[User] = relationship("User", back_populates="followers", foreign_keys=[followee_id])  # type: ignore[assignment]

    __table_args__ = (UniqueConstraint("follower_id", "followee_id", name="uq_follower_followee"),)

class Like(Base):  # type: ignore[misc]
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tweet: RelationshipProperty[Tweet] = relationship("Tweet", back_populates="likes")  # type: ignore[assignment]
    user: RelationshipProperty[User] = relationship("User", back_populates="likes")  # type: ignore[assignment]

    __table_args__ = (UniqueConstraint("tweet_id", "user_id", name="uq_tweet_user_like"),)

class Media(Base):  # type: ignore[misc]
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=True)

    tweet: RelationshipProperty[Tweet] = relationship("Tweet", back_populates="medias")  # type: ignore[assignment]
