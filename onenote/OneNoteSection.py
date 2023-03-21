from datetime import datetime
from functools import cache
from typing import Iterable
from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteElementBasedNode import OneNoteElementBasedNode
from .OneNoteNode import OneNoteNode
from .OneNotePage import OneNotePage


class OneNoteSection(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def _get_non_subpage_pages(self) -> Iterable[OneNotePage]:
        for child in super()._get_children():
            if isinstance(child, OneNotePage) and not child.is_subpage:
                yield child
            elif child.is_subpage:
                continue
            else:
                raise ValueError(f'Unexpected child type: {type(child)}')

    def _get_children(self) -> Iterable[OneNotePage]:
        return self._get_non_subpage_pages()

    @property
    @cache
    def children(self) -> tuple[OneNotePage, ...]:
        result_children = self._get_children()
        return tuple(result_children)

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
