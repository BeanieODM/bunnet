from typing import Any, ClassVar, Dict, Optional, Union

from pydantic import BaseModel

from bunnet.exceptions import ViewWasNotInitialized
from bunnet.odm.fields import Link, LinkInfo
from bunnet.odm.interfaces.aggregate import AggregateInterface
from bunnet.odm.interfaces.detector import DetectionInterface, ModelType
from bunnet.odm.interfaces.find import FindInterface
from bunnet.odm.interfaces.getters import OtherGettersInterface
from bunnet.odm.settings.view import ViewSettings


class View(
    BaseModel,
    FindInterface,
    AggregateInterface,
    OtherGettersInterface,
    DetectionInterface,
):
    """
    What is needed:

    Source collection or view
    pipeline

    """

    # Relations
    _link_fields: ClassVar[Optional[Dict[str, LinkInfo]]] = None

    # Settings
    _settings: ClassVar[ViewSettings]

    @classmethod
    def get_settings(cls) -> ViewSettings:
        """
        Get view settings, which was created on
        the initialization step

        :return: ViewSettings class
        """
        if cls._settings is None:
            raise ViewWasNotInitialized
        return cls._settings

    def fetch_link(self, field: Union[str, Any]):
        ref_obj = getattr(self, field, None)
        if isinstance(ref_obj, Link):
            value = ref_obj.fetch(fetch_links=True)
            setattr(self, field, value)
        if isinstance(ref_obj, list) and ref_obj:
            values = Link.fetch_list(ref_obj, fetch_links=True)
            setattr(self, field, values)

    def fetch_all_links(self):
        link_fields = self.get_link_fields()
        if link_fields is not None:
            for ref in link_fields.values():
                self.fetch_link(ref.field_name)  # TODO lists

    @classmethod
    def get_link_fields(cls) -> Optional[Dict[str, LinkInfo]]:
        return cls._link_fields

    @classmethod
    def get_model_type(cls) -> ModelType:
        return ModelType.View
