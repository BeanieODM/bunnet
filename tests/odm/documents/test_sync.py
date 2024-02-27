import pytest

from bunnet.exceptions import ApplyChangesException
from bunnet.odm.documents import MergeStrategy
from tests.odm.models import DocumentToTestSync


class TestSync:
    def test_merge_remote(self):
        doc = DocumentToTestSync()
        doc.insert()

        doc2 = DocumentToTestSync.get(doc.id).run()
        doc2.s = "foo"

        doc.i = 100
        doc.save()

        doc2.sync()

        assert doc2.s == "TEST"
        assert doc2.i == 100

    def test_merge_local(self):
        doc = DocumentToTestSync(d={"option_1": {"s": "foo"}})
        doc.insert()

        doc2 = DocumentToTestSync.get(doc.id).run()
        doc2.s = "foo"
        doc2.n.option_1.s = "bar"
        doc2.d["option_1"]["s"] = "bar"

        doc.i = 100
        doc.save()

        doc2.sync(merge_strategy=MergeStrategy.local)

        assert doc2.s == "foo"
        assert doc2.n.option_1.s == "bar"
        assert doc2.d["option_1"]["s"] == "bar"

        assert doc2.i == 100

    def test_merge_local_impossible_apply_changes(self):
        doc = DocumentToTestSync(d={"option_1": {"s": "foo"}})
        doc.insert()

        doc2 = DocumentToTestSync.get(doc.id).run()
        doc2.d["option_1"]["s"] = {"foo": "bar"}

        doc.d = {"option_1": "nothing"}
        doc.save()
        with pytest.raises(ApplyChangesException):
            doc2.sync(merge_strategy=MergeStrategy.local)
