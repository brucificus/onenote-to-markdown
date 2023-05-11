from typing import Optional, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementStyleValuePredicate, PanfluteElementFilter
from markdown_re import PanfluteElementLike
from onenote_export.page_export_tasks._element_predicates import element_has_specific_style_value
from onenote_export.page_export_tasks._element_updates import conclude_element_style_update
from onenote_export.page_export_tasks._style_attribute import parse_html_style_attribute


class ElementsRemoveSpecificStyle(PanfluteElementPredicateFilterPairBase):
    def __init__(self, style_to_remove: str, style_value_removal_condition: PanfluteElementStyleValuePredicate, *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)
        self._style_to_remove = style_to_remove
        self._style_value_removal_condition = style_value_removal_condition

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def valid_for_remove_specific_style(element: panflute.Element) -> bool:
            return element_has_specific_style_value(element, self._style_to_remove, self._style_value_removal_condition)
        yield valid_for_remove_specific_style

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return f"element has style item '{self._style_to_remove}' with value satisfying '{self._style_value_removal_condition}'"

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def remove_specific_style(element: panflute.Element, _: panflute.Doc) -> PanfluteElementLike:
            style_parsed = parse_html_style_attribute(element.attributes["style"])
            style_parsed.pop(self._style_to_remove)
            return conclude_element_style_update(element, style_parsed, style_changed=True)
        return remove_specific_style

    @property
    def _describe_element_filter(self) -> str:
        return f"removes style '{self._style_to_remove}'"

    @property
    def _description_emoji_infix(self) -> str:
        return '💄'
