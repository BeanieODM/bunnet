from abc import abstractmethod
from collections.abc import Mapping
from typing import Any

from pymongo.client_session import ClientSession

from bunnet.odm.bulk import BulkWriter
from bunnet.odm.fields import ExpressionField
from bunnet.odm.operators.update.general import (
    CurrentDate,
    Inc,
    Set,
)


class UpdateMethods:
    """
    Update methods
    """

    @abstractmethod
    def update(
        self,
        *args: Mapping[str, Any],
        session: ClientSession | None = None,
        bulk_writer: BulkWriter | None = None,
        **kwargs,
    ):
        return self

    def set(
        self,
        expression: dict[ExpressionField | str, Any],
        session: ClientSession | None = None,
        bulk_writer: BulkWriter | None = None,
        **kwargs,
    ):
        """
        Set values

        Example:

        ```python

        class Sample(Document):
            one: int

        Document.find(Sample.one == 1).set({Sample.one: 100})

        ```

        Uses [Set operator](operators/update.md#set)

        :param expression: Dict[Union[ExpressionField, str], Any] - keys and
        values to set
        :param session: Optional[ClientSession] - pymongo session
        :param bulk_writer: Optional[BulkWriter] - bulk writer
        :return: self
        """
        return self.update(
            Set(expression), session=session, bulk_writer=bulk_writer, **kwargs
        )

    def current_date(
        self,
        expression: dict[ExpressionField | str, Any],
        session: ClientSession | None = None,
        bulk_writer: BulkWriter | None = None,
        **kwargs,
    ):
        """
        Set current date

        Uses [CurrentDate operator](operators/update.md#currentdate)

        :param expression: Dict[Union[ExpressionField, str], Any]
        :param session: Optional[ClientSession] - pymongo session
        :param bulk_writer: Optional[BulkWriter] - bulk writer
        :return: self
        """
        return self.update(
            CurrentDate(expression),
            session=session,
            bulk_writer=bulk_writer,
            **kwargs,
        )

    def inc(
        self,
        expression: dict[ExpressionField | str, Any],
        session: ClientSession | None = None,
        bulk_writer: BulkWriter | None = None,
        **kwargs,
    ):
        """
        Increment

        Example:

        ```python

        class Sample(Document):
            one: int

        Document.find(Sample.one == 1).inc({Sample.one: 100})

        ```

        Uses [Inc operator](operators/update.md#inc)

        :param expression: Dict[Union[ExpressionField, str], Any]
        :param session: Optional[ClientSession] - pymongo session
        :param bulk_writer: Optional[BulkWriter] - bulk writer
        :return: self
        """
        return self.update(
            Inc(expression), session=session, bulk_writer=bulk_writer, **kwargs
        )
