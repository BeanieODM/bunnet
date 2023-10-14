from functools import wraps
from typing import TYPE_CHECKING, Callable

from bunnet.exceptions import StateManagementIsTurnedOff, StateNotSaved

if TYPE_CHECKING:
    from bunnet.odm.documents import DocType


def check_if_state_saved(self: "DocType"):
    if not self.use_state_management():
        raise StateManagementIsTurnedOff(
            "State management is turned off for this document"
        )
    if self._saved_state is None:
        raise StateNotSaved("No state was saved")


def saved_state_needed(f: Callable):
    @wraps(f)
    def sync_wrapper(self: "DocType", *args, **kwargs):
        check_if_state_saved(self)
        return f(self, *args, **kwargs)

    return sync_wrapper


def check_if_previous_state_saved(self: "DocType"):
    if not self.use_state_management():
        raise StateManagementIsTurnedOff(
            "State management is turned off for this document"
        )
    if not self.state_management_save_previous():
        raise StateManagementIsTurnedOff(
            "State management's option to save previous state is turned off for this document"
        )


def previous_saved_state_needed(f: Callable):
    @wraps(f)
    def sync_wrapper(self: "DocType", *args, **kwargs):
        check_if_previous_state_saved(self)
        return f(self, *args, **kwargs)

    return sync_wrapper


def save_state_after(f: Callable):
    @wraps(f)
    def wrapper(self: "DocType", *args, **kwargs):
        result = f(self, *args, **kwargs)
        self._save_state()
        return result

    return wrapper


def swap_revision_after(f: Callable):
    @wraps(f)
    def wrapper(self: "DocType", *args, **kwargs):
        result = f(self, *args, **kwargs)
        self._swap_revision()
        return result

    return wrapper
