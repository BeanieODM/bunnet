from pydantic.main import BaseModel

from bunnet import Document, iterative_migration


class Tag(BaseModel):
    color: str
    name: str


class Note(Document):
    title: str
    tag: Tag

    class Settings:
        name = "notes"


class Forward:
    @iterative_migration()
    def change_title(self, input_document: Note, output_document: Note):
        if input_document.title == "1":
            output_document.title = "one"


class Backward:
    @iterative_migration()
    def change_title(self, input_document: Note, output_document: Note):
        if input_document.title == "one":
            output_document.title = "1"
