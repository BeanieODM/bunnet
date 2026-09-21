from typing import Any

from tests.typing.models import ProjectionTest, Test


def aggregate() -> list[dict[str, Any]]:
    result = Test.aggregate([]).to_list()
    result_2 = Test.find().aggregate([]).to_list()
    return result or result_2


def aggregate_with_projection() -> list[ProjectionTest]:
    result = (
        Test.find().aggregate([], projection_model=ProjectionTest).to_list()
    )
    result_2 = Test.aggregate([], projection_model=ProjectionTest).to_list()
    return result or result_2
