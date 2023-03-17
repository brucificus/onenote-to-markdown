from datetime import datetime
from functools import cache
from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteElementBasedNode import OneNoteElementBasedNode
from .OneNoteNode import OneNoteNode
from .OneNotePage import OneNotePage


class OneNoteSection(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def get_pages(self) -> list[OneNotePage]:
        for child in self.get_children():
            if isinstance(child, OneNotePage) and not child.is_subpage:
                yield child
            else:
                raise Exception(f'Unexpected child type: {type(child)}')

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
    def is_readonly(self) -> bool:
        return self._element.attrib['readOnly'] == 'true'

    @property
    @cache
    def is_encrypted(self) -> bool:
        return 'encrypted' in self._element.attrib and self._element.attrib['encrypted'] == 'true'

    @property
    @cache
    def is_locked(self) -> bool:
        return 'locked' in self._element.attrib and self._element.attrib['locked'] == 'true'


OneNoteElementBasedNode.register(OneNoteSection)
