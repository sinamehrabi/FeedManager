import logging
import os
from celery import Celery
from constants import ConfigKeys
from feed_crawler import add_items_to_feeds
from dotenv import load_dotenv
load_dotenv()

app = Celery('worker', broker=os.getenv(ConfigKeys.AMQPUri))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(ConfigKeys.FeedTaskPeriodSeconds, add.s(), name='add every 1 minute')


@app.task
def add():
    logging.info("add to feed started")
    add_items_to_feeds()
    logging.info("add to feed stoped")
