from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid

import datetime

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Float
)
from sqlalchemy.ext.declarative import declarative_base


class Base:
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )


DeclarativeBase = declarative_base(cls=Base)


class Feed(DeclarativeBase):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    rss_link = Column(String)
    feed_posts = relationship("FeedItem")


class FeedItem(DeclarativeBase):
    __tablename__ = "feed_posts"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(ForeignKey(Feed.id))
    title = Column(String(50))
    link = Column(String)
    updated_feed = Column(DateTime)
    summary = Column(String)


class UserFeed(DeclarativeBase):
    __tablename__ = "user_feeds"
    __table_args__ = (UniqueConstraint('username', 'feed_id', name='_user_feed_uc'),)

    username = Column(String)
    feed_id = Column(ForeignKey(Feed.id))


class UserFeedItem(DeclarativeBase):
    __tablename__ = "user_feed_items"
    __table_args__ = (UniqueConstraint('username', 'feed_item_id', name='_user_feed_item_uc'),)

    username = Column(String)
    feed_item_id = Column(ForeignKey(FeedItem.id))
    is_read = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)

