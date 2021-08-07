from typing import Optional

from pydantic import BaseModel


class UserDTO(BaseModel):
    email: str = None
    password: Optional[str]
    username: str = None
    is_active: bool = None


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


class AuthDTO(BaseModel):
    access_token: str
    refresh_token: str
