from fastapi import APIRouter
from pydantic import BaseModel

from bunnet import PydanticObjectId, WriteRules
from bunnet.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.fastapi.models import HouseAPI, WindowAPI

house_router = APIRouter()
if not IS_PYDANTIC_V2:
    from fastapi.encoders import ENCODERS_BY_TYPE
    from pydantic.json import ENCODERS_BY_TYPE as PYDANTIC_ENCODERS_BY_TYPE

    ENCODERS_BY_TYPE.update(PYDANTIC_ENCODERS_BY_TYPE)


class WindowInput(BaseModel):
    id: PydanticObjectId


@house_router.post("/windows/", response_model=WindowAPI)
def create_window(window: WindowAPI):
    window.create()
    return window


@house_router.post("/windows_2/")
def create_window_2(window: WindowAPI):
    return window.save()


@house_router.post("/houses/", response_model=HouseAPI)
def create_house(window: WindowAPI):
    house = HouseAPI(name="test_name", windows=[window])
    house.insert(link_rule=WriteRules.WRITE)
    return house


@house_router.post("/houses_with_window_link/", response_model=HouseAPI)
def create_houses_with_window_link(window: WindowInput):
    house = HouseAPI.parse_obj(
        dict(name="test_name", windows=[WindowAPI.link_from_id(window.id)])
    )
    house.insert(link_rule=WriteRules.WRITE)
    return house


@house_router.post("/houses_2/", response_model=HouseAPI)
def create_houses_2(house: HouseAPI):
    house.insert(link_rule=WriteRules.WRITE)
    return house
