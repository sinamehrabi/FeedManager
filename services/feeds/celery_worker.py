import logging
from celery import Celery
from feed_crawler import add_items_to_feeds
app = Celery('worker', broker='amqp://guest:guest@rabbit/')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60, add.s(), name='add every 1 minute')


@app.task
def add():
    logging.info("add to feed started")
    add_items_to_feeds()
    logging.info("add to feed stoped")
