import logging
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Type, Optional

from bunnet.odm.documents import Document
from bunnet.odm.utils.init import init_bunnet
from bunnet.migrations.controllers.iterative import BaseMigrationController
from bunnet.migrations.database import DBHandler
from bunnet.migrations.models import (
    MigrationLog,
    RunningMode,
    RunningDirections,
)

logger = logging.getLogger(__name__)


class MigrationNode:
    def __init__(
        self,
        name: str,
        forward_class: Optional[Type[Document]] = None,
        backward_class: Optional[Type[Document]] = None,
        next_migration: Optional["MigrationNode"] = None,
        prev_migration: Optional["MigrationNode"] = None,
    ):
        """
        Node of the migration linked list

        :param name: name of the migration
        :param forward_class: Forward class of the migration
        :param backward_class: Backward class of the migration
        :param next_migration: link to the next migration
        :param prev_migration: link to the previous migration
        """
        self.name = name
        self.forward_class = forward_class
        self.backward_class = backward_class
        self.next_migration = next_migration
        self.prev_migration = prev_migration

    @staticmethod
    def clean_current_migration():
        MigrationLog.find(
            {"is_current": True},
        ).update({"$set": {"is_current": False}}).run()

    def update_current_migration(self):
        """
        Set sel as a current migration

        :return:
        """
        self.clean_current_migration()
        MigrationLog(is_current=True, name=self.name).insert()

    def run(self, mode: RunningMode, allow_index_dropping: bool):
        """
        Migrate

        :param mode: RunningMode
        :param allow_index_dropping: if index dropping is allowed
        :return: None
        """
        if mode.direction == RunningDirections.FORWARD:
            migration_node = self.next_migration
            if migration_node is None:
                return None
            if mode.distance == 0:
                logger.info("Running migrations forward without limit")
                while True:
                    migration_node.run_forward(
                        allow_index_dropping=allow_index_dropping
                    )
                    migration_node = migration_node.next_migration
                    if migration_node is None:
                        break
            else:
                logger.info(f"Running {mode.distance} migrations forward")
                for i in range(mode.distance):
                    migration_node.run_forward(
                        allow_index_dropping=allow_index_dropping
                    )
                    migration_node = migration_node.next_migration
                    if migration_node is None:
                        break
        elif mode.direction == RunningDirections.BACKWARD:
            migration_node = self
            if mode.distance == 0:
                logger.info("Running migrations backward without limit")
                while True:
                    migration_node.run_backward(
                        allow_index_dropping=allow_index_dropping
                    )
                    migration_node = migration_node.prev_migration
                    if migration_node is None:
                        break
            else:
                logger.info(f"Running {mode.distance} migrations backward")
                for i in range(mode.distance):
                    migration_node.run_backward(
                        allow_index_dropping=allow_index_dropping
                    )
                    migration_node = migration_node.prev_migration
                    if migration_node is None:
                        break

    def run_forward(self, allow_index_dropping):
        if self.forward_class is not None:
            self.run_migration_class(
                self.forward_class, allow_index_dropping=allow_index_dropping
            )
        self.update_current_migration()

    def run_backward(self, allow_index_dropping):
        if self.backward_class is not None:
            self.run_migration_class(
                self.backward_class, allow_index_dropping=allow_index_dropping
            )
        if self.prev_migration is not None:
            self.prev_migration.update_current_migration()
        else:
            self.clean_current_migration()

    def run_migration_class(self, cls: Type, allow_index_dropping: bool):
        """
        Run Backward or Forward migration class

        :param cls:
        :param allow_index_dropping: if index dropping is allowed
        :return:
        """
        migrations = [
            getattr(cls, migration)
            for migration in dir(cls)
            if isinstance(getattr(cls, migration), BaseMigrationController)
        ]

        client = DBHandler.get_cli()
        db = DBHandler.get_db()
        if client is None:
            raise RuntimeError("client must not be None")
        with client.start_session() as s:
            with s.start_transaction():
                for migration in migrations:
                    for model in migration.models:
                        init_bunnet(
                            database=db,
                            document_models=[model],  # type: ignore
                            allow_index_dropping=allow_index_dropping,
                        )  # TODO this is slow
                    logger.info(
                        f"Running migration {migration.function.__name__} "
                        f"from module {self.name}"
                    )
                    migration.run(session=s)

    @classmethod
    def build(cls, path: Path):
        """
        Build the migrations linked list

        :param path: Relative path to the migrations directory
        :return:
        """
        logger.info("Building migration list")
        names = []
        for modulepath in path.glob("*.py"):
            if modulepath.name != "__init__.py":
                names.append(modulepath.name)
        names.sort()

        db = DBHandler.get_db()
        init_bunnet(
            database=db, document_models=[MigrationLog]  # type: ignore
        )
        current_migration = MigrationLog.find_one({"is_current": True}).run()

        root_migration_node = cls("root")
        prev_migration_node = root_migration_node

        for name in names:
            module = SourceFileLoader(
                (path / name).stem, str((path / name).absolute())
            ).load_module((path / name).stem)
            forward_class = getattr(module, "Forward", None)
            backward_class = getattr(module, "Backward", None)
            migration_node = cls(
                name=name,
                prev_migration=prev_migration_node,
                forward_class=forward_class,
                backward_class=backward_class,
            )
            prev_migration_node.next_migration = migration_node
            prev_migration_node = migration_node

            if (
                current_migration is not None
                and current_migration.name == name
            ):
                root_migration_node = migration_node

        return root_migration_node
