from datetime import datetime
from functools import cache
from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteAPI import OneNoteAPI
from .OneNoteNode import OneNoteNode
from .OneNoteElementBasedNode import OneNoteElementBasedNode


class OneNoteNotebook(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, onenote_api: OneNoteAPI = None):
        super().__init__(element, parent, index, onenote_api)

    @property
    @cache
    def nickname(self) -> str:
        return self._element.attrib['nickname']

    @property
    @cache
    def path(self) -> str:
        return self._element.attrib['path']

    @property
    @cache
    def modified_at(self) -> datetime:
        return datetime.fromisoformat(self._element.attrib['lastModifiedTime'])

    @property
    @cache
    def color(self) -> str:
        return self._element.attrib['color']


OneNoteElementBasedNode.register(OneNoteNotebook)
