import pytest

from bunnet import init_bunnet
from bunnet.exceptions import Deprecation
from tests.odm.models import DocWithCollectionInnerClass


class TestDeprecations:
    def test_doc_with_inner_collection_class_init(self, db):
        with pytest.raises(Deprecation):
            init_bunnet(
                database=db,
                document_models=[DocWithCollectionInnerClass],
            )
