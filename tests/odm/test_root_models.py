from bunnet.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import DocumentWithRootModelAsAField

if IS_PYDANTIC_V2:

    class TestRootModels:
        def test_insert(self):
            doc = DocumentWithRootModelAsAField(pets=["dog", "cat", "fish"])
            doc.insert()

            new_doc = DocumentWithRootModelAsAField.get(doc.id).run()
            assert new_doc.pets.root == ["dog", "cat", "fish"]

            collection = DocumentWithRootModelAsAField.get_motor_collection()
            raw_doc = collection.find_one({"_id": doc.id})
            assert raw_doc["pets"] == ["dog", "cat", "fish"]
