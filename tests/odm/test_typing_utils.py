from typing import Optional, Union

import pytest
from pydantic import BaseModel
from typing_extensions import Annotated

from bunnet import Document, Link
from bunnet.odm.fields import Indexed
from bunnet.odm.utils.pydantic import get_model_fields
from bunnet.odm.utils.typing import extract_id_class, get_index_attributes


class Lock(Document):
    k: int


class TestTyping:
    def test_extract_id_class(self):
        # Union
        assert extract_id_class(Union[str, int]) == str
        assert extract_id_class(Union[str, None]) == str
        assert extract_id_class(Union[str, None, int]) == str
        # Optional
        assert extract_id_class(Optional[str]) == str
        # Link
        assert extract_id_class(Link[Lock]) == Lock

    @pytest.mark.parametrize(
        "type,result",
        (
            (str, None),
            (Indexed(str), (1, {})),
            (Indexed(str, "text", unique=True), ("text", {"unique": True})),
            (Annotated[str, Indexed()], (1, {})),
            (
                Annotated[str, "other metadata", Indexed(unique=True)],
                (1, {"unique": True}),
            ),
            (Annotated[str, "other metadata"], None),
        ),
    )
    def test_get_index_attributes(self, type, result):
        class Foo(BaseModel):
            bar: type

        field = get_model_fields(Foo)["bar"]
        assert get_index_attributes(field) == result
