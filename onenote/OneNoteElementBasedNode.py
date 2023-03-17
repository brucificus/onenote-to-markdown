import os
import re
from functools import cache

from win32com import client as win32
from xml.etree import ElementTree

from . import OneNoteApplication
from .OneNoteNode import OneNoteNode


class OneNoteElementBasedNode(OneNoteNode):
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
        return self._element.attrib['name']

    @property
    @cache
    def route(self) -> tuple[str, ...]:
        parent = self.parent
        self_route_part = (self.name,)
        if self.parent is None:
            return self_route_part
        elif hasattr(parent, 'route'):
            return parent.route + self_route_part
        elif isinstance(parent, OneNoteApplication):
            return self_path_part
        else:
            raise Exception(f'Unexpected parent type: {type(self.parent)}')

    @property
    def index(self) -> int:
        return self._index


OneNoteNode.register(OneNoteElementBasedNode)
