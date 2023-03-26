from .OneNoteNode import OneNoteNode


class OneNoteApplication(OneNoteNode):
    @property
    def node_id(self) -> str:
        return ""

    def __str__(self):
        return "OneNoteApplication"

    def __repr__(self):
        return "OneNoteApplication()"

OneNoteNode.register(OneNoteApplication)
