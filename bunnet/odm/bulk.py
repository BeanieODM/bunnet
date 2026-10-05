from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, Field
from pymongo import (
    DeleteMany,
    DeleteOne,
    InsertOne,
    ReplaceOne,
    UpdateMany,
    UpdateOne,
)
from pymongo.client_session import ClientSession
from pymongo.results import BulkWriteResult

from bunnet.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic import ConfigDict


class Operation(BaseModel):
    operation: type[InsertOne] | type[DeleteOne] | type[DeleteMany] | type[ReplaceOne] | type[UpdateOne] | type[UpdateMany]
    first_query: Mapping[str, Any]
    second_query: dict[str, Any] | None = None
    pymongo_kwargs: dict[str, Any] = Field(default_factory=dict)
    object_class: type

    if IS_PYDANTIC_V2:
        model_config = ConfigDict(
            arbitrary_types_allowed=True,
        )
    else:

        class Config:
            arbitrary_types_allowed = True


class BulkWriter:
    def __init__(self, session: ClientSession | None = None):
        self.operations: list[Operation] = []
        self.session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.commit()

    def commit(self) -> BulkWriteResult | None:
        """
        Commit all the operations to the database
        :return:
        """
        obj_class = None
        requests = []
        if self.operations:
            for op in self.operations:
                if obj_class is None:
                    obj_class = op.object_class

                if obj_class != op.object_class:
                    raise ValueError(
                        "All the operations should be for a single document model"
                    )
                if op.operation in [InsertOne, DeleteOne]:
                    query = op.operation(op.first_query, **op.pymongo_kwargs)
                else:
                    query = op.operation(
                        op.first_query, op.second_query, **op.pymongo_kwargs
                    )
                requests.append(query)

            return obj_class.get_motor_collection().bulk_write(  # type: ignore
                requests, session=self.session
            )
        return None

    def add_operation(self, operation: Operation):
        self.operations.append(operation)
