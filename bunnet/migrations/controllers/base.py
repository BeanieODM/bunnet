from abc import ABC, abstractmethod
from typing import List, Type

from bunnet.odm.documents import Document


class BaseMigrationController(ABC):
    def __init__(self, function):
        self.function = function

    @abstractmethod
    def run(self, session):
        pass

    @property
    @abstractmethod
    def models(self) -> List[Type[Document]]:
        pass
