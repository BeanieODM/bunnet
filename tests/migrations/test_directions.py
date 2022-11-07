import pytest
from pydantic.main import BaseModel

from bunnet import init_bunnet
from bunnet.executors.migrate import MigrationSettings, run_migrate
from bunnet.migrations.models import RunningDirections
from bunnet.odm.documents import Document


class Tag(BaseModel):
    color: str
    name: str


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


@pytest.fixture()
def notes(db):
    init_bunnet(database=db, document_models=[Note])
    Note.delete_all()
    for i in range(1, 8):
        note = Note(title=str(i), tag=Tag(name="test", color="red"))
        note.insert()
    yield i
    Note.delete_all()


def test_migration_by_one(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/many_migrations",
        distance=1,
    )

    init_bunnet(database=db, document_models=[Note])

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "2", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "three", "four", "five", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    run_migrate(migration_settings)

    migration_settings.direction = RunningDirections.BACKWARD

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "three", "four", "five", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "2", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)


def test_migration_by_two(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/many_migrations",
        distance=2,
    )

    init_bunnet(database=db, document_models=[Note])

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    run_migrate(migration_settings)

    migration_settings.direction = RunningDirections.BACKWARD

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "three", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["one", "two", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)


def test_migration_by_10(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/many_migrations",
        distance=10,
    )

    init_bunnet(database=db, document_models=[Note])

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    migration_settings.direction = RunningDirections.BACKWARD

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]


def test_migration_all(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/many_migrations",
    )

    init_bunnet(database=db, document_models=[Note])

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
        ]

    migration_settings.direction = RunningDirections.BACKWARD

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]

    run_migrate(migration_settings)
    for note in Note.find_all():
        assert note.title in ["1", "2", "3", "4", "5", "6", "7"]
