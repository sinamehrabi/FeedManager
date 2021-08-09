from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel


class FeedDTO(BaseModel):
    id: int = None
    title: str = None
    link: str = None
    rss_link: str = None
    last_updated: Optional[Union[str, datetime]] = None


class FeedItemDTO(BaseModel):
    id: int = None
    title: str = None
    link: str = None
    updated_feed_item: Optional[Union[str, datetime]] = None
    summary: str = None
    is_read: bool = False
    is_favorite: bool = False
    read_later: bool = False
