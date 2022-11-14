import pytest

from bunnet import init_bunnet
from bunnet.migrations.models import MigrationLog


@pytest.fixture(autouse=True)
def init(db):
    init_bunnet(
        database=db,
        document_models=[
            MigrationLog,
        ],
    )


# @pytest.fixture(autouse=True)
# def remove_migrations_log(db, init):
#     MigrationLog.delete_all()
