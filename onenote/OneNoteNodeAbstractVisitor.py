from abc import abstractmethod, ABC
from typing import Callable

from .OneNoteNode import OneNoteNode


class OneNoteNodeAbstractVisitor(ABC, Callable[['OneNoteNode'], None]):
    def __call__(self, *args, **kwargs):
        return self.visit(*args, **kwargs)

    @abstractmethod
    def visit(self, node: 'OneNoteNode'):
        pass
