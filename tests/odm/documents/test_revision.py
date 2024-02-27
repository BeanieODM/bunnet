import pytest
from pymongo.errors import BulkWriteError

from bunnet import BulkWriter
from bunnet.exceptions import RevisionIdWasChanged
from bunnet.odm.operators.update.general import Inc
from tests.odm.models import (
    DocumentWithRevisionTurnedOn,
    LockWithRevision,
    WindowWithRevision,
)


def test_replace():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    doc.insert()

    doc.num_1 = 2
    doc.replace()

    doc.num_2 = 3
    doc.replace()

    for i in range(5):
        found_doc = DocumentWithRevisionTurnedOn.get(doc.id).run()
        found_doc.num_1 += 1
        found_doc.replace()

    doc.revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        doc.replace()

    doc.replace(ignore_revision=True)
    doc.replace()


def test_update():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)

    doc.insert()

    doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))
    doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))

    for i in range(5):
        found_doc = DocumentWithRevisionTurnedOn.get(doc.id).run()
        found_doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))

    doc._previous_revision_id = "wrong"
    with pytest.raises(RevisionIdWasChanged):
        doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))

    doc.update(
        Inc({DocumentWithRevisionTurnedOn.num_1: 1}), ignore_revision=True
    )
    doc.update(Inc({DocumentWithRevisionTurnedOn.num_1: 1}))


def test_save_changes():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    doc.insert()

    doc.num_1 = 2
    doc.save_changes()

    doc.num_2 = 3
    doc.save_changes()

    for i in range(5):
        found_doc = DocumentWithRevisionTurnedOn.get(doc.id).run()
        found_doc.num_1 += 1
        found_doc.save_changes()

    doc.revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        doc.save_changes()

    doc.save_changes(ignore_revision=True)
    doc.save_changes()


def test_save():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)

    doc.num_1 = 2
    doc.save()

    doc.num_2 = 3
    doc.save()

    for i in range(5):
        found_doc = DocumentWithRevisionTurnedOn.get(doc.id).run()
        found_doc.num_1 += 1
        found_doc.save()

    doc.revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(RevisionIdWasChanged):
        doc.save()

    doc.save(ignore_revision=True)
    doc.save()


def test_update_bulk_writer():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    doc.save()

    doc.num_1 = 2
    with BulkWriter() as bulk_writer:
        doc.save(bulk_writer=bulk_writer)

    doc = DocumentWithRevisionTurnedOn.get(doc.id).run()

    doc.num_2 = 3
    with BulkWriter() as bulk_writer:
        doc.save(bulk_writer=bulk_writer)

    doc = DocumentWithRevisionTurnedOn.get(doc.id).run()

    for i in range(5):
        found_doc = DocumentWithRevisionTurnedOn.get(doc.id).run()
        found_doc.num_1 += 1
        with BulkWriter() as bulk_writer:
            found_doc.save(bulk_writer=bulk_writer)

    doc.revision_id = "wrong"
    doc.num_1 = 4
    with pytest.raises(BulkWriteError):
        with BulkWriter() as bulk_writer:
            doc.save(bulk_writer=bulk_writer)

    with BulkWriter() as bulk_writer:
        doc.save(bulk_writer=bulk_writer, ignore_revision=True)


def test_empty_update():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    doc.insert()

    # This fails with RevisionIdWasChanged
    doc.update({"$set": {"num_1": 1}})


def test_save_changes_when_there_were_no_changes():
    doc = DocumentWithRevisionTurnedOn(num_1=1, num_2=2)
    doc.insert()
    revision = doc.revision_id

    doc.save_changes()
    assert doc.revision_id == revision

    DocumentWithRevisionTurnedOn.get(doc.id).run()
    assert doc.revision_id == revision


def test_revision_id_for_link():
    lock = LockWithRevision(k=1)
    lock.insert()

    lock_rev_id = lock.revision_id

    window = WindowWithRevision(x=0, y=0, lock=lock)

    window.insert()
    assert lock.revision_id == lock_rev_id
