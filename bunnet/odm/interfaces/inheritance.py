from typing import (
    ClassVar,
)


class InheritanceInterface:
    _children: ClassVar[dict[str, type]]
    _parent: ClassVar[type | None]
    _inheritance_inited: ClassVar[bool]
    _class_id: ClassVar[str | None] = None

    @classmethod
    def add_child(cls, name: str, clas: type):
        cls._children[name] = clas
        if cls._parent is not None:
            cls._parent.add_child(name, clas)
