import logging
from datetime import datetime

import backoff
import feedparser
import requests
from sqlalchemy import or_

from constants import RPCMicroServices
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession
from models import DeclarativeBase, Feed, FeedItem, UserFeed, UserFeedItem
from schema import FeedDTO, FeedItemDTO


class FeedService:
    name = RPCMicroServices.FeedService
    db = DatabaseSession(DeclarativeBase)

    @rpc
    def create_feeds_items(self):
        feeds = self.db.query(Feed).all()

        if feeds:
            for feed in feeds:

                parsed_feed = self.feed_parser(feed.rss_link)
                feed_items = parsed_feed.entries
                for item in feed_items:
                    if hasattr(item, 'updated_parsed'):
                        feed_item_last_published = datetime(*item.updated_parsed[:6])
                    elif hasattr(item, 'published_parsed'):
                        feed_item_last_published = datetime(*item.published_parsed[:6])
                    if not feed.last_updated or feed_item_last_published > feed.last_updated:
                        feed_item = FeedItem(
                            feed_id=feed.id,
                            title=item.title,
                            link=item.link,
                            updated_feed_item=feed_item_last_published,
                            summary=item.summary
                        )
                        self.db.add(feed_item)

                if hasattr(parsed_feed.feed, 'updated_parsed'):
                    feed.last_updated = datetime(*parsed_feed.feed.updated_parsed[:6])
                elif hasattr(parsed_feed.feed, 'published_parsed'):
                    feed.last_updated = datetime(*parsed_feed.feed.published_parsed[:6])

                feed.link = parsed_feed.feed.link
                self.db.commit()

    @staticmethod
    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=4)
    def feed_parser(rss_url):
        res = requests.get(rss_url)
        return feedparser.parse(res.content)

    @rpc
    def create_user_feed(self, feed_dto, username):
        feed = FeedDTO(**feed_dto)
        feed_obj = Feed(
            title=feed.title,
            link=feed.link,
            rss_link=feed.rss_link,
        )
        self.db.add(feed_obj)
        self.db.commit()

        self.db.add(UserFeed(
            username=username,
            feed_id=feed_obj.id
        ))
        self.db.commit()

    @rpc
    def create_feed(self, feed_dto):
        feed = FeedDTO(**feed_dto)
        feed_obj = Feed(
            title=feed.title,
            link=feed.link,
            rss_link=feed.rss_link,
        )
        self.db.add(feed_obj)
        self.db.commit()

    @rpc
    def read_user_feeds(self, username):
        feeds = self.db.query(Feed).join(UserFeed).filter(UserFeed.username == username).all()
        if feeds:
            list_of_feeds = []
            for feed in feeds:
                list_of_feeds.append(FeedDTO(**feed.__dict__).dict())
            return {"data": list_of_feeds}
        else:
            return False

    @rpc
    def select_feed(self, username, feed_id):
        user_feed = self.db.query(UserFeed).filter(UserFeed.feed_id == feed_id, UserFeed.username == username).first()
        if not user_feed:
            self.db.add(UserFeed(
                username=username,
                feed_id=int(feed_id)
            ))
            self.db.commit()
            return True
        else:
            return False

    @rpc
    def deselect_feed(self, username, feed_id):
        user_feed = self.db.query(UserFeed).filter(UserFeed.feed_id == feed_id, UserFeed.username == username).first()
        if user_feed:
            self.db.delete(user_feed)
            self.db.commit()
            return True
        else:
            return False

    @rpc
    def read_feeds(self):
        feeds = self.db.query(Feed).all()
        if feeds:
            list_of_feeds = []
            for feed in feeds:
                list_of_feeds.append(FeedDTO(**feed.__dict__).dict())
            return {"data": list_of_feeds}
        else:
            return False

    @rpc
    def read_one_feed(self, feed_id):
        feed = self.db.query(Feed).filter(Feed.id == int(feed_id)).first()
        if feed:
            feed_obj = FeedDTO(**feed.__dict__)
            return feed_obj.dict()
        else:
            return False

    @rpc
    def read_user_feed_items(self, feed_id, username):
        user_feed = self.db.query(UserFeed).filter(UserFeed.username == username, UserFeed.feed_id == feed_id).first()
        if user_feed:
            feed_items = self.db.query(FeedItem).outerjoin(UserFeedItem).filter(
                or_(FeedItem.feed_id == feed_id, UserFeedItem.username == username)).all()
            list_of_feed_items = []
            if feed_items:
                for item in feed_items:
                    list_of_feed_items.append(FeedItemDTO(**item.__dict__).dict())
                return {"data": list_of_feed_items}
            else:
                return False
        else:
            return False

