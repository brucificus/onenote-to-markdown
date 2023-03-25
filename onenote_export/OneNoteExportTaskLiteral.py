from typing import Callable, Iterable

from onenote_export.OneNoteExportTaskBase import OneNoteExportTaskBase


class OneNoteExportTaskLiteral(OneNoteExportTaskBase):
    def __init__(self, execute: Callable[[], None], description: str = None, prerequisites: Iterable[OneNoteExportTaskBase] = ()):
        super().__init__(prerequisites)
        self._execute_impl = execute

        if description is None:
            description = execute.__name__
        self._description = description

    def _execute(self):
        self._execute_impl()

    def __str__(self):
        return self._description

    def __repr__(self):
        return str(self)

    @property
    def description(self) -> str:
        return self._description


OneNoteExportTaskBase.register(OneNoteExportTaskLiteral)
