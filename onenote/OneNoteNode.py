from abc import ABC, abstractmethod
from functools import cache
from typing import Iterable
from xml.etree import ElementTree

from .HierarchyScope import HierarchyScope
from .OneNoteAPI import OneNoteAPI


class OneNoteNode(ABC):
    def __init__(self, onenote_api: OneNoteAPI = None):
        self._onenote_api = onenote_api or OneNoteAPI()

    @property
    @abstractmethod
    def node_id(self) -> str:
        pass

    def _get_hierarchy_xml(self, node_id: str, hierarchy_scope: HierarchyScope) -> ElementTree:
        return self._onenote_api.get_hierarchy(node_id, hierarchy_scope)

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
        return create_onenote_node_from_xml_element(element, index, self, self._onenote_api)

    def _get_children(self) -> Iterable['OneNoteNode']:
        for i, child_element in enumerate(self._get_children_xml()):
            child = self._produce_child_node(child_element, i)
            yield child

    @property
    @cache
    def children(self) -> tuple['OneNoteNode', ...]:
        result_children = self._get_children()
        return tuple(result_children)
