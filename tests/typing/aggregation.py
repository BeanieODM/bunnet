from typing import List, Dict, Any

from tests.typing.models import Test, ProjectionTest


def aggregate() -> List[Dict[str, Any]]:
    result = Test.aggregate([]).to_list()
    result_2 = Test.find().aggregate([]).to_list()
    return result or result_2


def aggregate_with_projection() -> List[ProjectionTest]:
    result = (
        Test.find().aggregate([], projection_model=ProjectionTest).to_list()
    )
    result_2 = Test.aggregate([], projection_model=ProjectionTest).to_list()
    return result or result_2
