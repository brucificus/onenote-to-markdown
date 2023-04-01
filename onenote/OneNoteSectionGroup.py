from datetime import datetime
from functools import cache
from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteAPI import OneNoteAPI
from .OneNoteElementBasedNode import OneNoteElementBasedNode
from .OneNoteNode import OneNoteNode


class OneNoteSectionGroup(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, onenote_api: OneNoteAPI = None):
        super().__init__(element, parent, index, onenote_api)

    @property
    @cache
    def path(self) -> str:
        return self._element.attrib['path']

    @property
    @cache
    def modified_at(self) -> datetime:
        return datetime.fromisoformat(self._element.attrib['lastModifiedTime'])


OneNoteElementBasedNode.register(OneNoteSectionGroup)
