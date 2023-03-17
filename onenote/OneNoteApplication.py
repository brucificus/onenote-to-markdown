from typing import Optional

from .OneNoteNode import OneNoteNode
from .OneNoteNotebook import OneNoteNotebook
from .OneNoteUnfiledNotes import OneNoteUnfiledNotes


class OneNoteApplication(OneNoteNode):
    @property
    def node_id(self) -> str:
        return ""

    def get_notebooks(self) -> list[OneNoteNotebook]:
        for child in self.get_children():
            if isinstance(child, OneNoteNotebook):
                yield child
            elif isinstance(child, OneNoteUnfiledNotes):
                continue
            raise Exception(f'Unexpected child type: {type(child)}')

    def get_unfiled_notes(self) -> Optional[OneNoteUnfiledNotes]:
        for child in self.get_children():
            if isinstance(child, OneNoteUnfiledNotes):
                return child
            if isinstance(child, OneNoteNotebook):
                continue
            raise Exception(f'Unexpected child type: {type(child)}')
        return None


OneNoteNode.register(OneNoteApplication)
