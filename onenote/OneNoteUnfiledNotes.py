from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteElementBasedNode import OneNoteElementBasedNode
from .OneNoteNode import OneNoteNode
from .OneNotePage import OneNotePage


class OneNoteUnfiledNotes(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def get_pages(self) -> list[OneNotePage]:
        for child in self.get_children():
            if isinstance(child, OneNotePage):
                yield child
            else:
                raise Exception(f'Unexpected child type: {type(child)}')


OneNoteElementBasedNode.register(OneNoteUnfiledNotes)
