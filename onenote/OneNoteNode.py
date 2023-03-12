import traceback
import pywintypes
from abc import ABC, abstractmethod
from logging import info as log
from win32com import client as win32
from xml.etree import ElementTree

from .HierarchyScope import HierarchyScope


class OneNoteNode(ABC):
    def __init__(self, app: win32.CDispatch = None):
        self._app = app if app is not None else self._create_onenote_com_object()

    @abstractmethod
    def node_id(self) -> str:
        pass

    @staticmethod
    def _create_onenote_com_object() -> win32.CDispatch:
        try:
            return win32.gencache.EnsureDispatch("OneNote.Application.12")
        except pywintypes.com_error as e:
            traceback.print_exc()
            log("❗!!Error!!❗ Hint: Make sure OneNote is open first.")

    def _get_hierarchy(self, node_id: str, scope: HierarchyScope) -> ElementTree:
        return ElementTree.fromstring(self._app.GetHierarchy(node_id, scope.value, ""))

    def _get_children_xml(self) -> ElementTree:
        return self._get_hierarchy(self.node_id(), HierarchyScope.Children)

    def _get_pages_xml(self) -> ElementTree:
        return self._get_hierarchy(self.node_id(), HierarchyScope.Pages)

    def _get_notebooks_xml(self) -> ElementTree:
        return self._get_hierarchy(self.node_id(), HierarchyScope.Notebooks)

    def _get_sections_xml(self) -> ElementTree:
        return self._get_hierarchy(self.node_id(), HierarchyScope.Sections)

    def _produce_child_node(self, element: ElementTree, index: int) -> 'OneNoteNode':
        from onenote.OneNoteNodeFactory import create_onenote_node_from_xml_element
        return create_onenote_node_from_xml_element(element, index, self, self._app)

    def get_children(self) -> list['OneNoteNode']:
        for i, child_element in enumerate(self._get_children_xml()):
            child = self._produce_child_node(child_element, i)
            yield child
