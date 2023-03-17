from typing import Callable

from .OneNoteNodeAbstractVisitor import OneNoteNodeAbstractVisitor
from .OneNoteNode import OneNoteNode
from .OneNoteNotebook import OneNoteNotebook
from .OneNoteApplication import OneNoteApplication
from .OneNoteSection import OneNoteSection
from .OneNoteSectionGroup import OneNoteSectionGroup
from .OneNotePage import OneNotePage
from .OneNoteUnfiledNotes import OneNoteUnfiledNotes


class OneNoteNodeVisitorBase(OneNoteNodeAbstractVisitor):
    def __init__(self, should_visit: Callable[[OneNoteNode], bool] = lambda node: True):
        self._should_visit = should_visit

    def visit_application(self, node: OneNoteApplication):
        pass

    def visit_notebook(self, node: OneNoteNotebook):
        pass

    def visit_section(self, node: OneNoteSection):
        pass

    def visit_section_group(self, node: OneNoteSectionGroup):
        pass

    def visit_page(self, node: OneNotePage):
        pass

    def visit_unfiled_notes(self, node: OneNoteUnfiledNotes):
        pass

    def visit(self, node: OneNoteNode):
        if not self._should_visit(node):
            return

        if isinstance(node, OneNoteApplication):
            self.visit_application(node)
        elif isinstance(node, OneNoteNotebook):
            self.visit_notebook(node)
        elif isinstance(node, OneNoteSection):
            self.visit_section(node)
        elif isinstance(node, OneNoteSectionGroup):
            self.visit_section_group(node)
        elif isinstance(node, OneNotePage):
            self.visit_page(node)
        elif isinstance(node, OneNoteUnfiledNotes):
            self.visit_unfiled_notes(node)
        else:
            raise ValueError(f'Unexpected node type: {type(node)}')

        self.visit_children(node)

    def visit_children(self, node: OneNoteNode):
        for child in node.get_children():
            child.accept(self)


OneNoteNodeAbstractVisitor.register(OneNoteNodeVisitorBase)
