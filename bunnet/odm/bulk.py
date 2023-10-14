from typing import Any, Dict, List, Mapping, Optional, Type, Union

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
    operation: Union[
        Type[InsertOne],
        Type[DeleteOne],
        Type[DeleteMany],
        Type[ReplaceOne],
        Type[UpdateOne],
        Type[UpdateMany],
    ]
    first_query: Mapping[str, Any]
    second_query: Optional[Dict[str, Any]] = None
    pymongo_kwargs: Dict[str, Any] = Field(default_factory=dict)
    object_class: Type

    if IS_PYDANTIC_V2:
        model_config = ConfigDict(
            arbitrary_types_allowed=True,
        )
    else:

        class Config:
            arbitrary_types_allowed = True


class BulkWriter:
    def __init__(self, session: Optional[ClientSession] = None):
        self.operations: List[Operation] = []
        self.session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.commit()

    def commit(self) -> Optional[BulkWriteResult]:
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
