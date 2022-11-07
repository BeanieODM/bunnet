import pytest
from pydantic.main import BaseModel

from bunnet import init_bunnet
from bunnet.executors.migrate import MigrationSettings, run_migrate
from bunnet.migrations.models import RunningDirections
from bunnet.odm.documents import Document
from bunnet.odm.models import InspectionStatuses


class OldTag(BaseModel):
    color: str
    name: str


class Tag(BaseModel):
    color: str
    title: str


class OldNote(Document):
    title: str
    tag: OldTag

    class Settings:
        name = "notes"


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
        note = OldNote(title=str(i), tag=OldTag(name="test", color="red"))
        note.insert()
    yield
    OldNote.delete_all()


def test_migration_change_subfield_value(settings, notes, db):
    migration_settings = MigrationSettings(
        connection_uri=settings.mongodb_dsn,
        database_name=settings.mongodb_db_name,
        path="tests/migrations/migrations_for_test/change_subfield",
    )
    run_migrate(migration_settings)

    init_bunnet(database=db, document_models=[Note])
    inspection = Note.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = ~Note.find_one({})
    assert note.tag.title == "test"

    migration_settings.direction = RunningDirections.BACKWARD
    run_migrate(migration_settings)
    inspection = OldNote.inspect_collection()
    assert inspection.status == InspectionStatuses.OK
    note = ~OldNote.find_one({})
    assert note.tag.name == "test"
