from functools import cache

from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteElementBasedNode import OneNoteElementBasedNode
from .OneNoteNode import OneNoteNode
from .OneNotePage import OneNotePage
from .OneNoteSection import OneNoteSection


class OneNoteUnfiledNotes(OneNoteNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(app)
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
        return 'Unfiled Notes'

    @property
    @cache
    def path(self) -> tuple[str, ...]:
        return self.name,

    @property
    def index(self) -> int:
        return self._index

    def get_pages(self) -> list[OneNotePage]:
        for child in self.get_children():
            if isinstance(child, OneNotePage):
                yield child
            if isinstance(child, OneNoteSection):
                yield child
            else:
                raise Exception(f'Unexpected child type: {type(child)}')


OneNoteElementBasedNode.register(OneNoteUnfiledNotes)
