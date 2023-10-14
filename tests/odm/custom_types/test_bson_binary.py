import bson

from bunnet import BsonBinary
from tests.odm.models import DocumentWithBsonBinaryField


def test_bson_binary():
    doc = DocumentWithBsonBinaryField(binary_field=bson.Binary(b"test"))
    doc.insert()
    assert doc.binary_field == BsonBinary(b"test")

    new_doc = DocumentWithBsonBinaryField.get(doc.id).run()
    assert new_doc.binary_field == BsonBinary(b"test")

    doc = DocumentWithBsonBinaryField(binary_field=b"test")
    doc.insert()
    assert doc.binary_field == BsonBinary(b"test")

    new_doc = DocumentWithBsonBinaryField.get(doc.id).run()
    assert new_doc.binary_field == BsonBinary(b"test")
