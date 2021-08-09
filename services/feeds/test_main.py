from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from models import DeclarativeBase, Feed, FeedItem, UserFeed, UserFeedItem
from nameko.testing.services import worker_factory
from main import FeedService
from constants import ConfigKeys
from dotenv import load_dotenv
import random
import pytest
import os

load_dotenv()


@pytest.fixture
def session():
    """ Create a test database and session
    """
    engine = create_engine(os.getenv(ConfigKeys.DBUri))
    DeclarativeBase.metadata.create_all(engine)
    session_cls = sessionmaker(bind=engine)
    return session_cls()


def test_create_feed(session):
    service = worker_factory(FeedService, db=session)
    feed_data = {
        "title": "realpython",
        "link": "https://cnerd.ir",
        "rss_link": "https://realpython.com/atom.xml"
    }
    service.create_feed(feed_data)
    assert session.query(Feed.title, Feed.link, Feed.rss_link).all() == [
        ("realpython", "https://cnerd.ir", "https://realpython.com/atom.xml")]


def test_create_user_feed(session):
    service = worker_factory(FeedService, db=session)
    feed_data = {
        "title": "theverge",
        "link": "https://www.theverge.com/",
        "rss_link": "https://www.theverge.com/rss/index.xml"
    }
    service.create_user_feed(feed_data, "test_user1")
    feed = session.query(Feed).filter(Feed.rss_link == "https://www.theverge.com/rss/index.xml").first()
    assert feed.title == "theverge"
    assert feed.link == "https://www.theverge.com/"

    user_feed = session.query(UserFeed).filter(UserFeed.feed_id == feed.id).first()
    assert user_feed.username == "test_user1"


def test_create_feed_items(session):
    service = worker_factory(FeedService, db=session)
    service.create_feeds_items()
    assert session.query(func.count(FeedItem.id)).scalar() != 0


def test_read_feeds(session):
    services = worker_factory(FeedService, db=session)
    feeds = services.read_feeds()
    assert len(feeds['data']) > 0


def test_user_feed_select(session):
    services = worker_factory(FeedService, db=session)
    feeds = services.read_feeds()
    random_feed_id = feeds['data'][random.randint(0, len(feeds['data'])-1)]['id']
    select_status = services.select_feed("test_user2", random_feed_id)
    user_feed = session.query(UserFeed).filter(UserFeed.feed_id == random_feed_id,
                                               UserFeed.username == "test_user2").first()
    assert user_feed is not None
    assert select_status is True
    assert user_feed.username == "test_user2"
    assert user_feed.feed_id == random_feed_id


def test_user_feed_deselect(session):
    services = worker_factory(FeedService, db=session)
    user_feed = session.query(UserFeed).filter(UserFeed.username == "test_user2").first()
    user_feed_id = user_feed.feed_id
    services.deselect_feed(user_feed.username, user_feed.feed_id)
    user_feed_deselected = session.query(UserFeed).filter(UserFeed.username == "test_user2",
                                                          UserFeed.feed_id == user_feed_id).first()
    assert user_feed_deselected is None


def test_user_feed_item_read_and_item_action_integration(session):
    services = worker_factory(FeedService, db=session)
    username = "test_user1"
    user_feed = session.query(UserFeed).filter(UserFeed.username == username).first()
    user_feed_id = user_feed.feed_id
    user_feed_items = services.read_user_feed_items(user_feed_id, username)
    random_feed_item_id = user_feed_items['data'][random.randint(0, len(user_feed_items['data'])-1)]['id']
    services.item_action(user_feed_id, random_feed_item_id, username, is_favorite=True, read_later=True)
    user_feed_one_item = services.read_user_feed_one_item(user_feed_id, random_feed_item_id, username)
    assert user_feed_one_item['is_favorite'] is True
    assert user_feed_one_item['is_read'] is False
    assert user_feed_one_item['read_later'] is True
