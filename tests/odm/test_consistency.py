from bunnet.odm.operators.update.general import Set
from tests.odm.models import (
    DocumentTestModel,
    DocumentWithTimeStampToTestConsistency,
)


class TestResponseOfTheChangingOperations:
    def test_insert(self, document_not_inserted):
        result = document_not_inserted.insert()
        assert isinstance(result, DocumentTestModel)

    def test_update(self, document):
        result = document.update(Set({"test_int": 43}))
        assert isinstance(result, DocumentTestModel)

    def test_save(self, document, document_not_inserted):
        document.test_int = 43
        result = document.save()
        assert isinstance(result, DocumentTestModel)

        document_not_inserted.test_int = 43
        result = document_not_inserted.save()
        assert isinstance(result, DocumentTestModel)

    def test_save_changes(self, document):
        document.test_int = 43
        result = document.save_changes()
        assert isinstance(result, DocumentTestModel)

    def test_replace(self, document):
        result = document.replace()
        assert isinstance(result, DocumentTestModel)

    def test_set(self, document):
        result = document.set({"test_int": 43})
        assert isinstance(result, DocumentTestModel)

    def test_inc(self, document):
        result = document.inc({"test_int": 1})
        assert isinstance(result, DocumentTestModel)

    def test_current_date(self):
        document = DocumentWithTimeStampToTestConsistency()
        document.insert()
        result = document.current_date({"ts": True})
        assert isinstance(result, DocumentWithTimeStampToTestConsistency)
