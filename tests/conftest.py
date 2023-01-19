import pytest
from pydantic import BaseSettings
from pymongo import MongoClient


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017/bunnet_db"
    mongodb_db_name: str = "bunnet_db"


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture()
def cli(settings):
    return MongoClient(settings.mongodb_dsn)


@pytest.fixture()
def db(cli, settings):
    return cli[settings.mongodb_db_name]
