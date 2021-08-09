from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pytest
import os
from models import DeclarativeBase, User
from main import UserService
from nameko.testing.services import worker_factory
from dotenv import load_dotenv
from constants import ConfigKeys

load_dotenv()


@pytest.fixture
def session():
    """ Create a test database and session
    """
    engine = create_engine(os.getenv(ConfigKeys.DBUri))
    DeclarativeBase.metadata.create_all(engine)
    session_cls = sessionmaker(bind=engine)
    return session_cls()


def test_user_register_and_login_integration(session):
    services = worker_factory(UserService, db=session)
    test_user = {
        "email": "test_user@test.com",
        "password": "test_user_pass"
    }
    result = services.create_user(test_user)
    user = services.get_user(result['username'])
    assert user['email'] == test_user['email']
    login_user = services.login_user(test_user['email'], test_user['password'])
    assert login_user['username'] == user['username']
