from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteNode import OneNoteNode
from .OneNoteElementBasedNode import OneNoteElementBasedNode


class OneNoteNotebook(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)


OneNoteElementBasedNode.register(OneNoteNotebook)
