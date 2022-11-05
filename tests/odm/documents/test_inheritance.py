from bunnet import Link
from tests.models import (
    Vehicle,
    Bicycle,
    Bike,
    Car,
    Bus,
    TunedDocument,
    Owner,
)


class TestInheritance:
    def test_inheritance(self, db):
        bicycle_1 = Bicycle(color="white", frame=54, wheels=29).insert()
        bicycle_2 = Bicycle(color="red", frame=52, wheels=28).insert()

        bike_1 = Bike(color="black", fuel="gasoline").insert()

        car_1 = Car(color="grey", body="sedan", fuel="gasoline").insert()
        car_2 = Car(color="white", body="crossover", fuel="diesel").insert()

        bus_1 = Bus(
            color="white", seats=80, body="bus", fuel="diesel"
        ).insert()
        bus_2 = Bus(
            color="yellow", seats=26, body="minibus", fuel="diesel"
        ).insert()

        white_vehicles = Vehicle.find(
            Vehicle.color == "white", with_children=True
        ).to_list()

        cars_only = Car.find().to_list()
        cars_and_buses = Car.find(
            Car.fuel == "diesel", with_children=True
        ).to_list()

        big_bicycles = Bicycle.find(Bicycle.wheels > 28).to_list()

        Bike.find().update({"$set": {Bike.color: "yellow"}}).run()
        sedan = Car.find_one(Car.body == "sedan").run()

        sedan.color = "yellow"
        sedan.save()

        # get using Vehicle should return Bike instance
        updated_bike = Vehicle.get(bike_1.id, with_children=True).run()

        assert isinstance(sedan, Car)
        assert isinstance(updated_bike, Bike)
        assert updated_bike.color == "yellow"

        assert Vehicle._parent is TunedDocument
        assert Bus._parent is Car

        assert len(big_bicycles) == 1
        assert big_bicycles[0].wheels > 28

        assert len(white_vehicles) == 3
        assert len(cars_only) == 2

        assert {Car, Bus} == set(i.__class__ for i in cars_and_buses)
        assert {Bicycle, Car, Bus} == set(i.__class__ for i in white_vehicles)

        white_vehicles_2 = Car.find(Vehicle.color == "white").to_list()
        assert len(white_vehicles_2) == 1

        for i in cars_and_buses:
            assert i.fuel == "diesel"

        for e in (bicycle_1, bicycle_2, bike_1, car_1, car_2, bus_1, bus_2):
            assert isinstance(e, Vehicle)
            e.delete()

    def test_links(self, db):
        car_1 = Car(color="grey", body="sedan", fuel="gasoline").insert()
        car_2 = Car(color="white", body="crossover", fuel="diesel").insert()

        bus_1 = Bus(
            color="white", seats=80, body="bus", fuel="diesel"
        ).insert()

        owner = Owner(name="John").insert()
        owner.vehicles = [car_1, car_2, bus_1]
        owner.save()

        # re-fetch from DB w/o links
        owner = Owner.get(owner.id).run()
        assert {Link} == set(i.__class__ for i in owner.vehicles)
        owner.fetch_all_links()
        assert {Car, Bus} == set(i.__class__ for i in owner.vehicles)

        # re-fetch from DB with resolved links
        owner = Owner.get(owner.id, fetch_links=True).run()
        assert {Car, Bus} == set(i.__class__ for i in owner.vehicles)

        for e in (owner, car_1, car_2, bus_1):
            e.delete()
