from typing import Optional

from .OneNoteNode import OneNoteNode


class OneNoteApplication(OneNoteNode):
    @property
    def node_id(self) -> str:
        return ""

    def get_notebooks(self) -> list['OneNoteNotebook']:
        from .OneNoteNotebook import OneNoteNotebook
        from .OneNoteUnfiledNotes import OneNoteUnfiledNotes
        for child in self.get_children():
            if isinstance(child, OneNoteNotebook):
                yield child
            elif isinstance(child, OneNoteUnfiledNotes):
                pass
            else:
                raise Exception(f'Unexpected child type: {type(child)}')

    def get_unfiled_notes(self) -> Optional['OneNoteUnfiledNotes']:
        from .OneNoteNotebook import OneNoteNotebook
        from .OneNoteUnfiledNotes import OneNoteUnfiledNotes
        for child in self.get_children():
            if isinstance(child, OneNoteUnfiledNotes):
                return child
            elif isinstance(child, OneNoteNotebook):
                pass
            else:
                raise Exception(f'Unexpected child type: {type(child)}')
        return None


OneNoteNode.register(OneNoteApplication)
