from constants import RPCMicroServices
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession
from models import DeclarativeBase


class UserService:
    name = RPCMicroServices.FeedService
    db = DatabaseSession(DeclarativeBase)

    @rpc
    def haminjuri(self):
        pass
