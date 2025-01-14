import pathlib
from datetime import datetime
from functools import cache
from itertools import takewhile
from typing import Iterable
from xml.etree import ElementTree

from onenote_export.Pathlike import Pathlike
from .OneNoteAPI import OneNoteAPI
from .OneNoteElementBasedNode import OneNoteElementBasedNode
from .PublishFormat import PublishFormat
from .retry_com import retry_com


class OneNotePage(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteElementBasedNode, index: int, onenote_api: OneNoteAPI = None):
        if not isinstance(parent, OneNoteElementBasedNode):
            raise ValueError(f'Unexpected parent type: {type(parent)}')
        super().__init__(element, parent, index, onenote_api)

    @property
    @cache
    def is_subpage(self) -> bool:
        return 'isSubPage' in self._element.attrib and self._element.attrib['isSubPage'] == 'true'

    def __export(self, path: Pathlike, publish_format: PublishFormat):
        self._onenote_api.publish(self.node_id, path, publish_format)

    def _export_docx(self, path: pathlib.Path):
        if not path.suffix == '.docx':
            raise ValueError(f"Expected path suffix '.docx', got: {path.suffix}")
        self.__export(path, PublishFormat.pfWord)

    def _export_pdf(self, path: pathlib.Path):
        if not path.suffix == '.pdf':
            raise ValueError(f"Expected path suffix '.pdf', got: {path.suffix}")
        self.__export(path, PublishFormat.pfPDF)

    def _export_xps(self, path: pathlib.Path):
        if not path.suffix == '.xps':
            raise ValueError(f"Expected path suffix '.xps', got: {path.suffix}")
        self.__export(path, PublishFormat.pfXPS)

    def _export_mhtml(self, path: pathlib.Path):
        if path.suffix not in ('.mhtml', '.mht'):
            raise ValueError(f"Expected path suffix '.mhtml' or '.mht', got: {path.suffix}")
        self.__export(path, PublishFormat.pfMHTML)

    def _get_subpages(self) -> Iterable['OneNotePage']:
        if self.is_subpage:
            return

        parents_children = sorted(self.parent.children, key=lambda x: x.index)
        parents_children_after_me = [x for x in parents_children if x.index > self.index]
        sibling_subpages_before_next_non_subpage = takewhile(lambda x: x.is_subpage, parents_children_after_me)
        for subpage in sibling_subpages_before_next_non_subpage:
            if isinstance(subpage, OneNotePage):
                yield subpage
            else:
                raise ValueError(f'Unexpected child type: {type(subpage)}')

    def _get_children(self) -> Iterable['OneNotePage']:
        return self._get_subpages()

    @property
    @cache
    def children(self) -> tuple['OneNotePage', ...]:
        result_children = self._get_children()
        return tuple(result_children)

    @property
    @cache
    def path(self) -> str:
        return self._element.attrib['path']

    @property
    @cache
    def created_at(self) -> datetime:
        return datetime.fromisoformat(self._element.attrib['dateTime'])

    @property
    @cache
    def modified_at(self) -> datetime:
        return datetime.fromisoformat(self._element.attrib['lastModifiedTime'])


OneNoteElementBasedNode.register(OneNotePage)
