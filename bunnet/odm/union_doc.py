from typing import ClassVar, Type, Dict, Optional

from pymongo.database import Database

from bunnet.exceptions import UnionDocNotInited
from bunnet.odm.interfaces.aggregate import AggregateInterface
from bunnet.odm.interfaces.detector import DetectionInterface, ModelType
from bunnet.odm.interfaces.find import FindInterface
from bunnet.odm.interfaces.getters import OtherGettersInterface
from bunnet.odm.settings.union_doc import UnionDocSettings


class UnionDoc(
    FindInterface,
    AggregateInterface,
    OtherGettersInterface,
    DetectionInterface,
):
    _document_models: ClassVar[Optional[Dict[str, Type]]] = None
    _is_inited: ClassVar[bool] = False
    _settings: ClassVar[UnionDocSettings]

    @classmethod
    def get_settings(cls) -> UnionDocSettings:
        return cls._settings

    @classmethod
    def init(cls, database: Database):
        cls._settings = UnionDocSettings.init(database=database, doc_class=cls)
        cls._is_inited = True

    @classmethod
    def register_doc(cls, doc_model: Type):
        if cls._document_models is None:
            cls._document_models = {}

        if cls._is_inited is False:
            raise UnionDocNotInited

        cls._document_models[doc_model.__name__] = doc_model
        return cls.get_settings().name

    @classmethod
    def get_model_type(cls) -> ModelType:
        return ModelType.UnionDoc
