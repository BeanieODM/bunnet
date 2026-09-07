from datetime import timedelta
from typing import Any

from pydantic import BaseModel, Field
from pymongo.collection import Collection
from pymongo.database import Database

from bunnet.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic import ConfigDict


class ItemSettings(BaseModel):
    name: str | None = None

    use_cache: bool = False
    cache_capacity: int = 32
    cache_expiration_time: timedelta = timedelta(minutes=10)
    bson_encoders: dict[Any, Any] = Field(default_factory=dict)
    projection: dict[str, Any] | None = None

    motor_db: Database | None = None
    motor_collection: Collection | None = None

    union_doc: type | None = None
    union_doc_alias: str | None = None
    class_id: str = "_class_id"

    is_root: bool = False

    if IS_PYDANTIC_V2:
        model_config = ConfigDict(
            arbitrary_types_allowed=True,
        )
    else:

        class Config:
            arbitrary_types_allowed = True
