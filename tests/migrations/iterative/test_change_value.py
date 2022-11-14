import pytest
from pydantic.main import BaseModel

from bunnet import init_bunnet
from bunnet.executors.migrate import MigrationSettings, run_migrate
from bunnet.migrations.models import RunningDirections
from bunnet.odm.documents import Document
from bunnet.odm.models import InspectionStatuses


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
    for i in range(10):
        note = Note(title=str(i), tag=Tag(name="test", color="red"))
        note.insert()
    yield
    Note.delete_all()


def test_migration_change_value(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/change_value",
    )
    run_migrate(migration_settings)

    init_bunnet(database=db, document_models=[Note])
    inspection = Note.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = ~Note.find_one({"title": "five"})
    assert note is not None

    note = ~Note.find_one({"title": "5"})
    assert note is None

    migration_settings.direction = RunningDirections.BACKWARD
    run_migrate(migration_settings)
    inspection = Note.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = ~Note.find_one({"title": "5"})
    assert note is not None

    note = ~Note.find_one({"title": "five"})
    assert note is None
