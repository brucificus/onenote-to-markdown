import abc
from typing import ContextManager, Union, Callable


class ChangeTrackingJsonStrContextManager(ContextManager, abc.ABC):
    def __init__(self, initial_value: Union[str, Callable[[], str]] = None):
        self._enters = 0
        self._initial_value_factory = initial_value if callable(initial_value) else lambda: initial_value
        self._initial_value: str = None
        self._current_value: str = None
        self._ever_entered = False

    def __enter__(self):
        if self._enters == 0 and self.is_dirty:
            raise ValueError("Cannot enter context when dirty. Call commit_changes or discard_changes first.")
        self._enters += 1
        if self._enters == 1 and not self._ever_entered:
            self._initial_value = self._initial_value_factory()
            self._current_value = self._initial_value
            self._ever_entered = True

    @property
    def json_value(self) -> str:
        if self._enters != 0:
            return self._current_value
        if self.is_dirty:
            raise ValueError("Cannot access json_value when dirty. Call commit_changes or discard_changes first.")
        if not self._ever_entered and self._initial_value is None:
            with self:
                pass
        return self._current_value

    @json_value.setter
    def json_value(self, value: str):
        if self._enters == 0:
            raise ValueError("Cannot write to json_value before entering context.")
        self._current_value = value

    def commit_changes(self):
        if self._enters != 0:
            raise ValueError("Cannot commit changes before exiting context.")
        if not self._ever_entered:
            return
        self._initial_value = self._current_value

    def discard_changes(self):
        if self._enters != 0:
            raise ValueError("Cannot discard changes before exiting context.")
        if not self._ever_entered:
            return
        self._current_value = self._initial_value

    @property
    def is_dirty(self) -> bool:
        if not self._ever_entered:
            return False
        return self._initial_value != self._current_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._enters -= 1
