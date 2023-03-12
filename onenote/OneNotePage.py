from itertools import takewhile
from win32com import client as win32
from xml.etree import ElementTree

from .OneNoteElementBasedNode import OneNoteElementBasedNode


class OneNotePage(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteElementBasedNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def is_subpage(self) -> bool:
        return 'isSubPage' in self._element.attrib and self._element.attrib['isSubPage'] == 'true'

    def export_docx(self, path: str):
        self._app.Publish(self.node_id(), path, win32.constants.pfWord, "")

    def export_pdf(self, path: str):
        self._app.Publish(self.node_id(), path, 3, "")

    def get_children(self) -> list['OneNoteNode']:
        return self.get_subpages()

    def get_subpages(self) -> list['OneNotePage']:
        if self.is_subpage():
            return []
        else:
            parents_children = sorted(self.parent().get_children(), key=lambda x: x.index())
            parents_children_after_me = [x for x in parents_children if x.index() > self.index()]
            sibling_subpages_before_next_non_subpage = takewhile(lambda x: x.is_subpage(), parents_children_after_me)
            for subpage in sibling_subpages_before_next_non_subpage:
                if isinstance(subpage, OneNotePage):
                    yield subpage
                else:
                    raise Exception(f'Unexpected child type: {type(subpage)}')


OneNoteElementBasedNode.register(OneNotePage)
