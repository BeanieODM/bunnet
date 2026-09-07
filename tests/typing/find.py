
from tests.typing.models import ProjectionTest, Test


def find_many() -> list[Test]:
    return Test.find().to_list()


def find_many_with_projection() -> list[ProjectionTest]:
    return Test.find().project(projection_model=ProjectionTest).to_list()


def find_many_generator() -> list[Test]:
    docs: list[Test] = []
    for doc in Test.find():
        docs.append(doc)
    return docs


def find_many_generator_with_projection() -> list[ProjectionTest]:
    docs: list[ProjectionTest] = []
    for doc in Test.find().project(projection_model=ProjectionTest):
        docs.append(doc)
    return docs


def find_one() -> Test | None:
    return Test.find_one().run()


def find_one_with_projection() -> ProjectionTest | None:
    return Test.find_one().project(projection_model=ProjectionTest).run()
