from typing import Optional, List, Union
from datetime import datetime

from pydantic import BaseModel


class UserDTO(BaseModel):
    email: str = None
    password: Optional[str]
    username: str = None
    is_active: bool = None


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


class AuthDTO(BaseModel):
    access_token: str = None
    refresh_token: str = None


class FeedDTO(BaseModel):
    id: int = None
    title: str = None
    link: str = None
    rss_link: str = None
    last_updated: Optional[Union[str, datetime]] = None


class ListFeedDTO(BaseModel):
    data: List[FeedDTO]


class FeedItemDTO(BaseModel):
    id: int = None
    title: str = None
    link: str = None
    updated_feed_item: Optional[Union[str, datetime]] = None
    summary: str = None
    is_read: bool = False
    is_favorite: bool = False
    read_later: bool = False
    comment: str = None


class ListFeedItemDTO(BaseModel):
    data: List[FeedItemDTO]


class CommentDTO(BaseModel):
    comment: str = None
