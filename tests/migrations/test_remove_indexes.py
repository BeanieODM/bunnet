import pytest
from pydantic.main import BaseModel
from pymongo.collection import Collection

from bunnet import init_bunnet
from bunnet.executors.migrate import MigrationSettings, run_migrate
from bunnet.odm.documents import Document


class Tag(BaseModel):
    color: str
    name: str


class OldNote(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"
        indexes = ["title"]


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


@pytest.fixture()
def notes(db):
    init_bunnet(database=db, document_models=[OldNote])
    OldNote.delete_all()
    for i in range(10):
        note = OldNote(title=str(i), tag=Tag(name="test", color="red"))
        note.insert()
    yield
    OldNote.delete_all()


def test_remove_index_allowed(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/remove_index",
        allow_index_dropping=True,
    )
    run_migrate(migration_settings)

    init_bunnet(
        database=db, document_models=[Note], allow_index_dropping=False
    )
    collection: Collection = Note.get_motor_collection()
    index_info = collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
    }


def test_remove_index_default(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/remove_index",
    )
    run_migrate(migration_settings)

    init_bunnet(
        database=db, document_models=[Note], allow_index_dropping=False
    )
    collection: Collection = Note.get_motor_collection()
    index_info = collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "title_1": {"key": [("title", 1)], "v": 2},
    }


def test_remove_index_not_allowed(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/remove_index",
        allow_index_dropping=False,
    )
    run_migrate(migration_settings)

    init_bunnet(
        database=db, document_models=[Note], allow_index_dropping=False
    )
    collection: Collection = Note.get_motor_collection()
    index_info = collection.index_information()
    assert index_info == {
        "_id_": {"key": [("_id", 1)], "v": 2},
        "title_1": {"key": [("title", 1)], "v": 2},
    }
