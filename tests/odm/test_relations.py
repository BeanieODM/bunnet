import pytest

from bunnet.exceptions import DocumentWasNotSaved
from bunnet.odm.fields import DeleteRules, Link, WriteRules
from tests.odm.models import (
    Door,
    House,
    Lock,
    Roof,
    Window,
    Yard,
    RootDocument,
    ADocument,
    BDocument,
    UsersAddresses,
    Region,
    AddressView,
    SelfLinked,
    LoopedLinksA,
    LoopedLinksB,
)


@pytest.fixture
def lock_not_inserted():
    return Lock(k=10)


@pytest.fixture
def locks_not_inserted():
    return [Lock(k=10), Lock(k=11)]


@pytest.fixture
def window_not_inserted(lock_not_inserted):
    return Window(x=10, y=10, lock=lock_not_inserted)


@pytest.fixture
def windows_not_inserted(lock_not_inserted):
    return [
        Window(
            x=10,
            y=10,
            lock=lock_not_inserted,
        ),
        Window(
            x=11,
            y=11,
            lock=lock_not_inserted,
        ),
    ]


@pytest.fixture
def door_not_inserted(locks_not_inserted, window_not_inserted):
    return Door(
        t=10,
        window=window_not_inserted,
        locks=locks_not_inserted,
    )


@pytest.fixture
def house_not_inserted(windows_not_inserted, door_not_inserted):
    return House(
        windows=windows_not_inserted, door=door_not_inserted, name="test"
    )


@pytest.fixture
def house(house_not_inserted):
    return house_not_inserted.insert(link_rule=WriteRules.WRITE)


@pytest.fixture
def houses():
    for i in range(10):
        roof = Roof() if i % 2 == 0 else None
        if i % 2 == 0:
            yards = [Yard(v=10, w=10 + i), Yard(v=11, w=10 + i)]
        else:
            yards = None
        house = House(
            door=Door(
                t=i,
                window=Window(x=20, y=21 + i, lock=Lock(k=20 + i))
                if i % 2 == 0
                else None,
                locks=[Lock(k=20 + i)],
            ),
            windows=[
                Window(x=10, y=10 + i, lock=Lock(k=10 + i)),
                Window(x=11, y=11 + i, lock=Lock(k=11 + i)),
            ],
            yards=yards,
            roof=roof,
            name="test",
            height=i,
        ).insert(link_rule=WriteRules.WRITE)
        if i == 9:
            house.windows[0].delete()
            house.windows[1].lock.delete()
            house.door.delete()


class TestInsert:
    def test_rule_do_nothing(self, house_not_inserted):
        with pytest.raises(DocumentWasNotSaved):
            house_not_inserted.insert()

    def test_rule_write(self, house_not_inserted):
        house_not_inserted.insert(link_rule=WriteRules.WRITE)
        locks = Lock.all().to_list()
        assert len(locks) == 5
        windows = Window.all().to_list()
        assert len(windows) == 3
        doors = Door.all().to_list()
        assert len(doors) == 1
        houses = House.all().to_list()
        assert len(houses) == 1

    def test_insert_with_link(
        self,
        house_not_inserted,
        door_not_inserted,
        window_not_inserted,
        lock_not_inserted,
        locks_not_inserted,
    ):
        lock_links = []
        for lock in locks_not_inserted:
            lock = lock.insert()
            link = Lock.link_from_id(lock.id)
            lock_links.append(link)
        door_not_inserted.locks = lock_links

        door_window_lock = lock_not_inserted.insert()
        door_window_lock_link = Lock.link_from_id(door_window_lock.id)
        window_not_inserted.lock = door_window_lock_link

        door_window = window_not_inserted.insert()
        door_window_link = Window.link_from_id(door_window.id)
        door_not_inserted.window = door_window_link

        door = door_not_inserted.insert()
        door_link = Door.link_from_id(door.id)
        house_not_inserted.door = door_link

        house = House.parse_obj(house_not_inserted)
        house.insert(link_rule=WriteRules.WRITE)
        house.json()

    def test_multi_insert_links(self):
        house = House(name="random", windows=[], door=Door())
        window = Window(x=13, y=23).insert()
        assert window.id
        house.windows.append(window)

        house = house.insert(link_rule=WriteRules.WRITE)
        new_window = Window(x=11, y=22)
        house.windows.append(new_window)
        house = house.save(link_rule=WriteRules.WRITE)
        for win in house.windows:
            assert isinstance(win, Window)
            assert win.id


class TestFind:
    def test_prefetch_find_many(self, houses):
        items = House.find(House.height > 2).sort(House.height).to_list()
        assert len(items) == 7
        for window in items[0].windows:
            assert isinstance(window, Link)
        assert items[0].yards is None
        for yard in items[1].yards:
            assert isinstance(yard, Link)
        assert isinstance(items[0].door, Link)
        assert items[0].roof is None
        assert isinstance(items[1].roof, Link)

        items = (
            House.find(House.height > 2, fetch_links=True)
            .sort(House.height)
            .to_list()
        )
        assert len(items) == 7
        for window in items[0].windows:
            assert isinstance(window, Window)
            assert isinstance(window.lock, Lock)
        assert items[0].yards == []
        for yard in items[1].yards:
            assert isinstance(yard, Yard)
        assert isinstance(items[0].door, Door)
        assert isinstance(items[1].door.window, Window)
        assert items[0].door.window is None
        assert isinstance(items[1].door.window.lock, Lock)
        for lock in items[0].door.locks:
            assert isinstance(lock, Lock)
        assert items[0].roof is None
        assert isinstance(items[1].roof, Roof)

        houses = House.find_many(House.height == 9, fetch_links=True).to_list()
        assert len(houses[0].windows) == 1
        assert isinstance(houses[0].windows[0].lock, Link)
        assert isinstance(houses[0].door, Link)

        houses[0].fetch_link(House.door)
        assert isinstance(houses[0].door, Link)

        houses = House.find_many(House.door.t > 5, fetch_links=True).to_list()

        assert len(houses) == 3

        houses = House.find_many(
            House.windows.y == 15, fetch_links=True
        ).to_list()

        assert len(houses) == 2

        houses = House.find_many(
            House.height > 5, limit=3, fetch_links=True
        ).to_list()

        assert len(houses) == 3

    def test_prefetch_find_one(self, house):
        house = House.find_one(House.name == "test").run()
        for window in house.windows:
            assert isinstance(window, Link)
        assert isinstance(house.door, Link)

        house = House.find_one(House.name == "test", fetch_links=True).run()
        for window in house.windows:
            print(window, type(window))
            assert isinstance(window, Window)
        assert isinstance(house.door, Door)

        house = House.get(house.id, fetch_links=True).run()
        for window in house.windows:
            assert isinstance(window, Window)
        assert isinstance(house.door, Door)

    def test_fetch(self, house):
        house = House.find_one(House.name == "test").run()
        for window in house.windows:
            assert isinstance(window, Link)
        assert isinstance(house.door, Link)

        house.fetch_all_links()
        for window in house.windows:
            assert isinstance(window, Window)
            assert isinstance(window.lock, Lock)
        assert isinstance(house.door, Door)
        assert isinstance(house.door.window, Window)
        for lock in house.door.locks:
            assert isinstance(lock, Lock)

        house = House.find_one(House.name == "test").run()
        assert isinstance(house.door, Link)
        house.fetch_link(House.door)
        assert isinstance(house.door, Door)
        assert isinstance(house.door.window, Window)
        for lock in house.door.locks:
            assert isinstance(lock, Lock)

        for window in house.windows:
            assert isinstance(window, Link)
        house.fetch_link(House.windows)
        for window in house.windows:
            assert isinstance(window, Window)
            assert isinstance(window.lock, Lock)

    def test_find_by_id_of_the_linked_docs(self, house):
        house_lst_1 = House.find(House.door.id == house.door.id).to_list()
        house_lst_2 = House.find(
            House.door.id == house.door.id, fetch_links=True
        ).to_list()
        assert len(house_lst_1) == 1
        assert len(house_lst_2) == 1

        house_1 = House.find_one(House.door.id == house.door.id).run()
        house_2 = House.find_one(
            House.door.id == house.door.id, fetch_links=True
        ).run()
        assert house_1 is not None
        assert house_2 is not None


class TestReplace:
    def test_do_nothing(self, house):
        house.door.t = 100
        house.replace()
        new_house = House.get(house.id, fetch_links=True).run()
        assert new_house.door.t == 10

    def test_write(self, house):
        house.door.t = 100
        house.replace(link_rule=WriteRules.WRITE)
        new_house = House.get(house.id, fetch_links=True).run()
        assert new_house.door.t == 100


class TestSave:
    def test_do_nothing(self, house):
        house.door.t = 100
        house.save()
        new_house = House.get(house.id, fetch_links=True).run()
        assert new_house.door.t == 10

    def test_write(self, house):
        house.door.t = 100
        house.windows = [Window(x=100, y=100, lock=Lock(k=100))]
        house.save(link_rule=WriteRules.WRITE)
        new_house = House.get(house.id, fetch_links=True).run()
        assert new_house.door.t == 100
        for window in new_house.windows:
            assert window.x == 100
            assert window.y == 100
            assert isinstance(window.lock, Lock)
            assert window.lock.k == 100


class TestDelete:
    def test_do_nothing(self, house):
        house.delete()
        door = Door.get(house.door.id).run()
        assert door is not None

        windows = Window.all().to_list()
        assert windows is not None

        locks = Lock.all().to_list()
        assert locks is not None

    def test_delete_links(self, house):
        house.delete(link_rule=DeleteRules.DELETE_LINKS)
        door = Door.get(house.door.id).run()
        assert door is None

        windows = Window.all().to_list()
        assert windows == []

        locks = Lock.all().to_list()
        assert locks == []


class TestOther:
    def test_query_composition(self):
        SYS = {"id", "revision_id"}

        # Simple fields are initialized using the pydantic __fields__ internal property
        # such fields are properly isolated when multi inheritance is involved.
        assert set(RootDocument.__fields__.keys()) == SYS | {
            "name",
            "link_root",
        }
        assert set(ADocument.__fields__.keys()) == SYS | {
            "name",
            "link_root",
            "surname",
            "link_a",
        }
        assert set(BDocument.__fields__.keys()) == SYS | {
            "name",
            "link_root",
            "email",
            "link_b",
        }

        # Where Document.init_fields() has a bug that prevents proper link inheritance when parent
        # documents are initialized. Furthermore, some-why BDocument._link_fields are not deterministic
        assert set(RootDocument._link_fields.keys()) == {"link_root"}
        assert set(ADocument._link_fields.keys()) == {"link_root", "link_a"}
        assert set(BDocument._link_fields.keys()) == {"link_root", "link_b"}

    def test_with_projection(self):
        UsersAddresses(region_id=Region()).insert(link_rule=WriteRules.WRITE)
        res = (
            UsersAddresses.find_one(fetch_links=True)
            .project(AddressView)
            .run()
        )
        assert res.id is not None
        assert res.state == "TEST"
        assert res.city == "TEST"

    def test_self_linked(self):
        SelfLinked(item=SelfLinked(s="2"), s="1").insert(
            link_rule=WriteRules.WRITE
        )

        res = SelfLinked.find_one(fetch_links=True).run()
        assert isinstance(res, SelfLinked)
        assert res.item is None

        SelfLinked.delete_all()

        SelfLinked(
            item=SelfLinked(
                item=SelfLinked(item=SelfLinked(s="4"), s="3"), s="2"
            ),
            s="1",
        ).insert(link_rule=WriteRules.WRITE)

        res = SelfLinked.find_one(SelfLinked.s == "1", fetch_links=True).run()
        assert isinstance(res, SelfLinked)
        assert isinstance(res.item, SelfLinked)
        assert isinstance(res.item.item, SelfLinked)
        assert isinstance(res.item.item.item, Link)

    def test_looped_links(self):
        LoopedLinksA(b=LoopedLinksB(a=LoopedLinksA(b=LoopedLinksB()))).insert(
            link_rule=WriteRules.WRITE
        )
        res = LoopedLinksA.find_one(fetch_links=True).run()
        assert isinstance(res, LoopedLinksA)
        assert isinstance(res.b, LoopedLinksB)
        assert isinstance(res.b.a, LoopedLinksA)
        assert isinstance(res.b.a.b, LoopedLinksB)
        assert res.b.a.b.a is None
