import re
from datetime import date, datetime
from uuid import uuid4

import pytest
from bson import Binary, Regex
from pydantic import AnyUrl

from bunnet.odm.utils.encoder import Encoder
from bunnet.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import (
    Child,
    DocumentForEncodingTest,
    DocumentForEncodingTestDate,
    DocumentWithComplexDictKey,
    DocumentWithDecimalField,
    DocumentWithHttpUrlField,
    DocumentWithKeepNullsFalse,
    DocumentWithStringField,
    ModelWithOptionalField,
    SampleWithMutableObjects,
)


def test_encode_datetime():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTest(datetime_field=datetime.now())
    doc.insert()
    new_doc = DocumentForEncodingTest.get(doc.id).run()
    assert isinstance(new_doc.datetime_field, datetime)


def test_encode_date():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTestDate()
    doc.insert()
    new_doc = DocumentForEncodingTestDate.get(doc.id).run()
    assert new_doc.date_field == doc.date_field
    assert isinstance(new_doc.date_field, date)


def test_encode_regex():
    raw_regex = r"^AA.*CC$"
    case_sensitive_regex = re.compile(raw_regex)
    case_insensitive_regex = re.compile(raw_regex, re.I)

    assert isinstance(Encoder().encode(case_sensitive_regex), Regex)
    assert isinstance(Encoder().encode(case_insensitive_regex), Regex)

    matching_doc = DocumentWithStringField(string_field="AABBCC")
    ignore_case_matching_doc = DocumentWithStringField(string_field="aabbcc")
    non_matching_doc = DocumentWithStringField(string_field="abc")

    for doc in (matching_doc, ignore_case_matching_doc, non_matching_doc):
        doc.insert()

    assert {matching_doc.id, ignore_case_matching_doc.id} == {
        doc.id
        for doc in DocumentWithStringField.find(
            DocumentWithStringField.string_field == case_insensitive_regex
        )
    }
    assert {matching_doc.id} == {
        doc.id
        for doc in DocumentWithStringField.find(
            DocumentWithStringField.string_field == case_sensitive_regex
        )
    }


def test_encode_with_custom_encoder():
    assert isinstance(
        Encoder(custom_encoders={datetime: str}).encode(datetime.now()), str
    )


def test_bytes():
    encoded_b = Encoder().encode(b"test")
    assert isinstance(encoded_b, Binary)
    assert encoded_b.subtype == 0

    doc = DocumentForEncodingTest(bytes_field=b"test")
    doc.insert()
    new_doc = DocumentForEncodingTest.get(doc.id).run()
    assert isinstance(new_doc.bytes_field, bytes)


def test_bytes_already_binary():
    b = Binary(b"123", 3)
    encoded_b = Encoder().encode(b)
    assert isinstance(encoded_b, Binary)
    assert encoded_b.subtype == 3


def test_mutable_objects_on_save():
    instance = SampleWithMutableObjects(
        d={"Bar": Child(child_field="Foo")}, lst=[Child(child_field="Bar")]
    )
    instance.save()
    assert isinstance(instance.d["Bar"], Child)
    assert isinstance(instance.lst[0], Child)


def test_decimal():
    test_amts = DocumentWithDecimalField(amt=1, other_amt=2)
    test_amts.insert()
    obj = DocumentWithDecimalField.get(test_amts.id).run()
    assert obj.amt == 1
    assert obj.other_amt == 2

    test_amts.amt = 6
    test_amts.save_changes()

    obj = DocumentWithDecimalField.get(test_amts.id).run()
    assert obj.amt == 6

    test_amts = (DocumentWithDecimalField.find_all().to_list())[0]
    test_amts.other_amt = 7
    test_amts.save_changes()

    obj = DocumentWithDecimalField.get(test_amts.id).run()
    assert obj.other_amt == 7


def test_keep_nulls_false():
    model = ModelWithOptionalField(i=10)
    doc = DocumentWithKeepNullsFalse(m=model)

    encoder = Encoder(keep_nulls=False, to_db=True)
    encoded_doc = encoder.encode(doc)
    assert encoded_doc == {"m": {"i": 10}}


@pytest.mark.skipif(not IS_PYDANTIC_V2, reason="Test only for Pydantic v2")
def test_should_encode_pydantic_v2_url_correctly():
    url = AnyUrl("https://example.com")
    encoder = Encoder()
    encoded_url = encoder.encode(url)
    assert isinstance(encoded_url, str)
    # pydantic2 add trailing slash for naked url. see https://github.com/pydantic/pydantic/issues/6943
    assert encoded_url == "https://example.com/"


def test_should_be_able_to_save_retrieve_doc_with_url():
    doc = DocumentWithHttpUrlField(url_field="https://example.com")
    assert isinstance(doc.url_field, AnyUrl)
    doc.save()

    new_doc = DocumentWithHttpUrlField.find_one(
        DocumentWithHttpUrlField.id == doc.id
    ).run()

    assert isinstance(new_doc.url_field, AnyUrl)
    assert new_doc.url_field == doc.url_field


def test_dict_with_complex_key():
    assert isinstance(Encoder().encode({uuid4(): datetime.now()}), dict)

    uuid = uuid4()
    # reset microseconds, because it looses by mongo
    dt = datetime.now().replace(microsecond=0)

    doc = DocumentWithComplexDictKey(dict_field={uuid: dt})
    doc.insert()
    new_doc = DocumentWithComplexDictKey.get(doc.id).run()

    assert isinstance(new_doc.dict_field, dict)
    assert new_doc.dict_field.get(uuid) == dt
