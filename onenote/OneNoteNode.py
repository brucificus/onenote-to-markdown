from functools import cache
from abc import ABC, abstractmethod
from typing import Callable, Iterable
from win32com import client as win32
from xml.etree import ElementTree

from .HierarchyScope import HierarchyScope


class OneNoteNode(ABC):
    def __init__(self, app: win32.CDispatch = None):
        self._app = app if app is not None else self._create_onenote_com_object()

    @property
    @abstractmethod
    def node_id(self) -> str:
        pass

    @staticmethod
    def _create_onenote_com_object() -> win32.CDispatch:
        return win32.gencache.EnsureDispatch("OneNote.Application.12")

    def accept(self, visitor: Callable[['OneNoteNode'], None]):
        visitor(self)

    def _get_hierarchy_xml(self, node_id: str, scope: HierarchyScope) -> ElementTree:
        return ElementTree.fromstring(self._app.GetHierarchy(node_id, scope.value, ""))

    def _get_children_xml(self) -> ElementTree:
        return self._get_hierarchy_xml(self.node_id, HierarchyScope.Children)

    def _get_pages_xml(self) -> ElementTree:
        return self._get_hierarchy_xml(self.node_id, HierarchyScope.Pages)

    def _get_notebooks_xml(self) -> ElementTree:
        return self._get_hierarchy_xml(self.node_id, HierarchyScope.Notebooks)

    def _get_sections_xml(self) -> ElementTree:
        return self._get_hierarchy_xml(self.node_id, HierarchyScope.Sections)

    def _produce_child_node(self, element: ElementTree, index: int) -> 'OneNoteNode':
        from onenote.create_onenote_node import create_onenote_node_from_xml_element
        return create_onenote_node_from_xml_element(element, index, self, self._app)

    def _get_children(self) -> Iterable['OneNoteNode']:
        for i, child_element in enumerate(self._get_children_xml()):
            child = self._produce_child_node(child_element, i)
            yield child

    @property
    @cache
    def children(self) -> tuple['OneNoteNode', ...]:
        result_children = self._get_children()
        return tuple(result_children)
