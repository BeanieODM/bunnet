from typing import List, Optional

from tests.typing.models import ProjectionTest, Test


def find_many() -> List[Test]:
    return Test.find().to_list()


def find_many_with_projection() -> List[ProjectionTest]:
    return Test.find().project(projection_model=ProjectionTest).to_list()


def find_many_generator() -> List[Test]:
    docs: List[Test] = []
    for doc in Test.find():
        docs.append(doc)
    return docs


def find_many_generator_with_projection() -> List[ProjectionTest]:
    docs: List[ProjectionTest] = []
    for doc in Test.find().project(projection_model=ProjectionTest):
        docs.append(doc)
    return docs


def find_one() -> Optional[Test]:
    return Test.find_one().run()


def find_one_with_projection() -> Optional[ProjectionTest]:
    return Test.find_one().project(projection_model=ProjectionTest).run()
