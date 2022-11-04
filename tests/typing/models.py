from pydantic import BaseModel

from bunnet import Document


class Test(Document):
    foo: str
    bar: str
    baz: str


class ProjectionTest(BaseModel):
    foo: str
    bar: int
