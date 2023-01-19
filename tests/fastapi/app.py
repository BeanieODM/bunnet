import motor.motor_asyncio
from bunnet import init_bunnet
from fastapi import FastAPI

from tests.conftest import Settings
from tests.fastapi.models import HouseAPI, WindowAPI, DoorAPI, RoofAPI
from tests.fastapi.routes import house_router

app = FastAPI()


@app.on_event("startup")
def app_init():
    # CREATE MOTOR CLIENT
    client = motor.motor_asyncio.AsyncIOMotorClient(Settings().mongodb_dsn)

    # INIT BEANIE
    init_bunnet(
        client.bunnet_db,
        document_models=[HouseAPI, WindowAPI, DoorAPI, RoofAPI],
    )

    # ADD ROUTES
    app.include_router(house_router, prefix="/v1", tags=["house"])
