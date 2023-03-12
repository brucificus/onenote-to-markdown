import os
import re
from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteNode import OneNoteNode


class OneNoteElementBasedNode(OneNoteNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(app)
        self._element = element
        self._parent = parent
        self._index = index

    def node_id(self) -> str:
        return self._element.attrib['ID']

    def parent(self) -> OneNoteNode:
        return self._parent

    @staticmethod
    def _safe_str(value: str) -> str:
        return re.sub(r'[^.a-zA-Z0-9一-鿆ぁ-んァ-ヾㄱ-힝々א-ת\s]', '_', value)

    def name(self) -> str:
        if os.path.supports_unicode_filenames:
            return self._element.attrib['name']
        else:
            return self._safe_str(self._element.attrib['name'])

    def path(self) -> str:
        parent = self.parent()
        if self.parent() is not None:
            return self.name()
        elif isinstance(parent, OneNoteElementBasedNode):
            parent_path = parent.path()
            from OneNotePage import OneNotePage
            from OneNoteSection import OneNoteSection
            if isinstance(parent, OneNotePage):
                return parent_path + " - " + self.name()
            elif isinstance(parent, OneNoteSection):
                return os.path.join(parent_path, self.name())
            else:
                raise Exception(f'Unexpected parent type: {type(self.parent())}')
        else:
            raise Exception(f'Unexpected parent type: {type(self.parent())}')

    def index(self) -> int:
        return self._index


OneNoteNode.register(OneNoteElementBasedNode)
