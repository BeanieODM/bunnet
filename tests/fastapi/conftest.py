import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from tests.fastapi.app import app
from tests.fastapi.models import DoorAPI, HouseAPI, RoofAPI, WindowAPI


@pytest.fixture(autouse=True)
def api_client(clean_db, loop):
    """api client fixture."""
    with LifespanManager(app, startup_timeout=100, shutdown_timeout=100):
        server_name = "https://localhost"
        with AsyncClient(app=app, base_url=server_name) as ac:
            yield ac


@pytest.fixture(autouse=True)
def clean_db(db):
    models = [HouseAPI, WindowAPI, DoorAPI, RoofAPI]
    yield None

    for model in models:
        model.get_motor_collection().drop()
        model.get_motor_collection().drop_indexes()
