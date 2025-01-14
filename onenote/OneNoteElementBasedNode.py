from functools import cache
from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteAPI import OneNoteAPI
from .OneNoteNode import OneNoteNode


class OneNoteElementBasedNode(OneNoteNode):
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
    @cache
    def name(self) -> str:
        return self._element.attrib['name']

    @property
    @cache
    def route(self) -> tuple[str, ...]:
        parent = self.parent
        self_route_part = (self.name,)
        if self.parent is None:
            return self_route_part
        if hasattr(parent, 'route'):
            return parent.route + self_route_part
        from .OneNoteApplication import OneNoteApplication
        if isinstance(parent, OneNoteApplication):
            return self_route_part
        raise ValueError(f'Unexpected parent type: {type(self.parent)}')

    @property
    def index(self) -> int:
        return self._index

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"


OneNoteNode.register(OneNoteElementBasedNode)
