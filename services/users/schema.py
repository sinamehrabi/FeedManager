from pydantic import BaseModel


class UserDTO(BaseModel):
    email: str = None
    password: str = None
    username: str = None
    is_active: bool = None
