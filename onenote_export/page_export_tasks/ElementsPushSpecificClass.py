from typing import Optional, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementContainerElementCtor, PanfluteElementFilter
from markdown_re import PanfluteElementLike
from onenote_export.page_export_tasks._element_predicates import element_has_specific_class
from onenote_export.page_export_tasks._element_updates import push_element_content, conclude_element_classes_update


class ElementsPushSpecificClass(PanfluteElementPredicateFilterPairBase):
    def __init__(self, class_to_push: str, new_child_element_type: PanfluteElementContainerElementCtor, *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)
        self._class_to_push = class_to_push
        self._new_child_element_type = new_child_element_type

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def valid_for_push_specific_class(element: panflute.Element) -> bool:
            return element_has_specific_class(element, self._class_to_push)
        yield valid_for_push_specific_class

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return f"element has specific class '{self._class_to_push}'"

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def push_specific_class(element: panflute.Element, _: panflute.Doc) -> PanfluteElementLike:
            push_element_content(element, self._new_child_element_type)
            element.classes.remove(self._class_to_push)
            return conclude_element_classes_update(element, classes_changed=True)
        return push_specific_class

    @property
    def _describe_element_filter(self) -> str:
        return f"pushes stylization of children into container '{self._new_child_element_type}'"

    @property
    def _description_emoji_infix(self) -> str:
        return '💄'
