import json
import io
from typing import ContextManager, Optional, Union, Callable

import panflute

from markdown_dom.ChangeTrackingJsonStrContextManager import ChangeTrackingJsonStrContextManager


class ChangeTrackingPanfluteDocumentContextManager(ContextManager[panflute.Doc]):
    def __init__(self, document_ast_context_manager: ChangeTrackingJsonStrContextManager):
        if not isinstance(document_ast_context_manager, ChangeTrackingJsonStrContextManager):
            raise TypeError("document_ast_context_manager must be ChangeTrackingJsonStrContextManager")

        self._document_ast_context_manager = document_ast_context_manager
        self._enters = 0
        self._panflute_document: Optional[panflute.Doc] = None

    def __enter__(self):
        self._enters += 1
        self._document_ast_context_manager.__enter__()
        if self._enters == 1:
            self._panflute_document = self._load_document_from_ast_json(self._document_ast_context_manager.json_value)

    @staticmethod
    def _load_document_from_ast_json(document_ast_json: str) -> panflute.Doc:
        if not document_ast_json:
            return panflute.Doc()

        return json.loads(
            document_ast_json,
            object_hook=panflute.elements.from_json
        )

    @staticmethod
    def _dump_document_to_ast_json(document: panflute.Doc) -> str:
        with io.StringIO() as f:
            panflute.dump(document, f)
            return f.getvalue()

    @classmethod
    def from_ast_json(cls, document_ast_json: Union[str, Callable[[], str]]) -> 'ChangeTrackingPanfluteDocumentContextManager':
        if not isinstance(document_ast_json, (str, Callable)):
            raise TypeError("document_ast_json must be str or a callable that returns str")
        return cls(ChangeTrackingJsonStrContextManager(document_ast_json))

    @property
    def panflute_document(self) -> panflute.Doc:
        if self._enters == 0:
            raise ValueError("Cannot access panflute_document before entering context.")
        return self._panflute_document

    @panflute_document.setter
    def panflute_document(self, value: panflute.Doc):
        if self._enters == 0:
            raise ValueError("Cannot access panflute_document before entering context.")
        self._panflute_document = value
        self._document_ast_context_manager.json_value = self._dump_document_to_ast_json(self._panflute_document)

    @property
    def is_dirty(self) -> bool:
        if self._enters != 0:
            raise ValueError("Cannot read is_dirty before exiting context.")
        return self._document_ast_context_manager.is_dirty

    @property
    def document_ast_json(self) -> str:
        if self._enters != 0:
            raise ValueError("Cannot read document_ast_json before exiting context.")
        return self._document_ast_context_manager.json_value

    @document_ast_json.setter
    def document_ast_json(self, value: str):
        if self._enters == 0:
            raise ValueError("Cannot write document_ast_json before entering context.")
        self._document_ast_context_manager.json_value = value
        self._panflute_document = self._load_document_from_ast_json(value)

    def commit_changes(self):
        if self._enters != 0:
            raise ValueError("Cannot commit changes before exiting context.")
        self._document_ast_context_manager.commit_changes()

    def discard_changes(self):
        if self._enters != 0:
            raise ValueError("Cannot discard changes before exiting context.")
        self._document_ast_context_manager.discard_changes()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._enters == 1:
            self._document_ast_context_manager.json_value = self._dump_document_to_ast_json(self._panflute_document)
        self._document_ast_context_manager.__exit__(exc_type, exc_val, exc_tb)
        self._enters -= 1
