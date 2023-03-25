import abc
from typing import Callable, Iterable


class OneNoteExportTaskBase(Callable[[], None], abc.ABC):
    def __init__(self, prerequisites: Iterable['OneNoteExportTask']):
        self._prerequisites = prerequisites
        self._is_complete = False

    def _satisfy_prerequisites(self):
        for prerequisite in self._prerequisites:
            prerequisite()

    def __call__(self):
        if not self.is_complete:
            self._satisfy_prerequisites()
            self._execute()
        self._is_complete = True

    @property
    def is_complete(self) -> bool:
        return self._is_complete

    @abc.abstractmethod
    def _execute(self):
        pass
