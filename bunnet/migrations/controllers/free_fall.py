from inspect import signature

from bunnet.migrations.controllers.base import BaseMigrationController
from bunnet.odm.documents import Document


def free_fall_migration(document_models: list[type[Document]]):
    class FreeFallMigrationController(BaseMigrationController):
        def __init__(self, function):
            self.function = function
            self.function_signature = signature(function)
            self.document_models = document_models

        def __call__(self, *args, **kwargs):
            pass

        @property
        def models(self) -> list[type[Document]]:
            return self.document_models

        def run(self, session):
            function_kwargs = {"session": session}
            if "self" in self.function_signature.parameters:
                function_kwargs["self"] = None
            self.function(**function_kwargs)

    return FreeFallMigrationController
