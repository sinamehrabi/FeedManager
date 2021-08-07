from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession
from models import DeclarativeBase, User
from schema import UserDTO
from constants import RPCMicroServices
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class UserService:
    name = RPCMicroServices.UserService
    db = DatabaseSession(DeclarativeBase)

    @rpc
    def create_user(self, dto):
        user_dto = UserDTO(**dto)
        user = self.db.query(User).filter(User.email == user_dto.email).one_or_none()
        if not user:
            new_user = User(
                email=user_dto.email,
                hashed_password=get_password_hash(user_dto.password)
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.flush()

            return UserDTO(username=new_user.username, email=new_user.email).dict()
        else:
            return False

    @rpc
    def get_user(self, username):
        user = self.db.query(User).filter(User.username == username).first()
        if user:
            data = UserDTO(username=user.username, email=user.email, is_active=user.is_active)
            return data.dict()
        else:
            return False

    @rpc
    def login_user(self, email, password):
        user = self.db.query(User).filter(User.email == email).first()
        hashed_password = verify_password(password, user.hashed_password)
        if hashed_password:
            if user:
                data = UserDTO(username=user.username, email=user.email, is_active=user.is_active)
                return data.dict()
            else:
                return False
        else:
            return False
