from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteElementBasedNode import OneNoteElementBasedNode
from .OneNoteNode import OneNoteNode
from .OneNoteSection import OneNoteSection


class OneNoteSectionGroup(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def get_section_groups(self) -> list['OneNoteSectionGroup']:
        for child in self.get_children():
            if isinstance(child, OneNoteSectionGroup):
                yield child
            elif isinstance(child, OneNoteSection):
                pass
            else:
                raise Exception(f'Unexpected child type: {type(child)}')

    def get_sections(self) -> list[OneNoteSection]:
        for child in self.get_children():
            if isinstance(child, OneNoteSection):
                yield child
            elif isinstance(child, OneNoteSectionGroup):
                pass
            else:
                raise Exception(f'Unexpected child type: {type(child)}')


OneNoteElementBasedNode.register(OneNoteSectionGroup)
