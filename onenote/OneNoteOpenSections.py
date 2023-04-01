from functools import cache
from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteAPI import OneNoteAPI
from .OneNoteElementBasedNode import OneNoteElementBasedNode
from .OneNoteNode import OneNoteNode


class OneNoteOpenSections(OneNoteNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, onenote_api: OneNoteAPI = None):
        super().__init__(onenote_api)
        self._element = element
        self._parent = parent
        self._index = index

    @property
    @cache
    def node_id(self) -> str:
        return self._element.attrib['ID']

    @property
    def parent(self) -> OneNoteNode:
        return self._parent

    @property
    def name(self) -> str:
        return 'Open Sections'

    @property
    def route(self) -> tuple[str, ...]:
        return (self.name,)

    @property
    def index(self) -> int:
        return self._index

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"


OneNoteElementBasedNode.register(OneNoteOpenSections)
