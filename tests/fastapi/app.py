from fastapi import FastAPI
from pymongo import MongoClient

from bunnet import init_bunnet
from tests.conftest import Settings
from tests.fastapi.models import DoorAPI, HouseAPI, RoofAPI, WindowAPI
from tests.fastapi.routes import house_router

app = FastAPI()


@app.on_event("startup")
async def app_init():
    # CREATE MOTOR CLIENT
    client = MongoClient(Settings().mongodb_dsn)

    # INIT BEANIE
    init_bunnet(
        client.bunnet_db,
        document_models=[HouseAPI, WindowAPI, DoorAPI, RoofAPI],
    )

    # ADD ROUTES
    app.include_router(house_router, prefix="/v1", tags=["house"])
