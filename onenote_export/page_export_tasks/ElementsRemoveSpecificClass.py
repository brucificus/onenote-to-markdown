from typing import Optional, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementFilter
from markdown_re import PanfluteElementLike
from onenote_export.page_export_tasks._element_predicates import element_has_specific_class
from onenote_export.page_export_tasks._element_updates import conclude_element_classes_update


class ElementsRemoveSpecificClass(PanfluteElementPredicateFilterPairBase):
    def __init__(self, class_to_remove: str, *, base_elements_predicate: PanfluteElementPredicate = None):
        super().__init__(base_elements_predicate=base_elements_predicate)
        self._class_to_remove = class_to_remove

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def valid_for_remove_specific_class(element: panflute.Element) -> bool:
            return element_has_specific_class(element, self._class_to_remove)
        yield valid_for_remove_specific_class

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return f"element has specific class '{self._class_to_remove}'"

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def remove_specific_class(element: panflute.Element, _: panflute.Doc) -> PanfluteElementLike:
            element.classes.remove(self._class_to_remove)
            return conclude_element_classes_update(element, classes_changed=True)
        return remove_specific_class

    @property
    def _describe_element_filter(self) -> str:
        return f"removes specific class '{self._class_to_remove}'"

    @property
    def _description_emoji_infix(self) -> str:
        return '💄'
