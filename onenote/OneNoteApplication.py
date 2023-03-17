from .OneNoteNode import OneNoteNode


class OneNoteApplication(OneNoteNode):
    @property
    def node_id(self) -> str:
        return ""


OneNoteNode.register(OneNoteApplication)
