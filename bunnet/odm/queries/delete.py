from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Mapping,
    Optional,
    Type,
    Union,
)

from pymongo import DeleteMany as DeleteManyPyMongo
from pymongo import DeleteOne as DeleteOnePyMongo
from pymongo.results import DeleteResult

from bunnet.odm.bulk import BulkWriter, Operation
from bunnet.odm.interfaces.clone import CloneInterface
from bunnet.odm.interfaces.run import RunInterface
from bunnet.odm.interfaces.session import SessionMethods

if TYPE_CHECKING:
    from bunnet.odm.documents import DocType


class DeleteQuery(SessionMethods, RunInterface, CloneInterface):
    """
    Deletion Query
    """

    def __init__(
        self,
        document_model: Type["DocType"],
        find_query: Mapping[str, Any],
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
    ):
        self.document_model = document_model
        self.find_query = find_query
        self.session = None
        self.bulk_writer = bulk_writer
        self.pymongo_kwargs: Dict[str, Any] = pymongo_kwargs


class DeleteMany(DeleteQuery):
    def run(self) -> Union[DeleteResult, None, Optional[DeleteResult]]:
        """
        Run the query
        :return:
        """
        if self.bulk_writer is None:
            return self.document_model.get_motor_collection().delete_many(
                self.find_query, session=self.session, **self.pymongo_kwargs
            )
        else:
            self.bulk_writer.add_operation(
                Operation(
                    operation=DeleteManyPyMongo,
                    first_query=self.find_query,
                    object_class=self.document_model,
                    pymongo_kwargs=self.pymongo_kwargs,
                )
            )
            return None


class DeleteOne(DeleteQuery):
    def run(self) -> Union[DeleteResult, None, Optional[DeleteResult]]:
        """
        Run the query
        :return:
        """
        if self.bulk_writer is None:
            return self.document_model.get_motor_collection().delete_one(
                self.find_query, session=self.session, **self.pymongo_kwargs
            )
        else:
            self.bulk_writer.add_operation(
                Operation(
                    operation=DeleteOnePyMongo,
                    first_query=self.find_query,
                    object_class=self.document_model,
                    pymongo_kwargs=self.pymongo_kwargs,
                )
            )
            return None
