from abc import ABC, abstractmethod

from bunnet.odm.documents import Document


class BaseMigrationController(ABC):
    def __init__(self, function):
        self.function = function

    @abstractmethod
    def run(self, session):
        pass

    @property
    @abstractmethod
    def models(self) -> list[type[Document]]:
        pass
