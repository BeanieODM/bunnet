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
    def change_color(self, input_document: Note, output_document: Note):
        output_document.tag.color = "blue"


class Backward:
    @iterative_migration()
    def change_title(self, input_document: Note, output_document: Note):
        output_document.tag.color = "red"
