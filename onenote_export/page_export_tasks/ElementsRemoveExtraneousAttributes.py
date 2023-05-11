from typing import Optional, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementAttributeValuePredicate, PanfluteElementPredicate, PanfluteElementFilter
from markdown_re import PanfluteElementLike
from onenote_export.page_export_tasks._element_predicates import element_has_attribute_value
from onenote_export.page_export_tasks._element_updates import conclude_element_attributes_update


def _valid_for_remove_specific_attribute(element: panflute.Element, attribute_to_remove: str,
                                         attribute_removal_condition: PanfluteElementAttributeValuePredicate) -> bool:
    return element_has_attribute_value(
        element,
        attribute_to_remove,
        attribute_removal_condition
    )


def _remove_specific_attribute(element: panflute.Element, _: panflute.Doc, attribute_to_remove: str) -> PanfluteElementLike:
    element.attributes.pop(attribute_to_remove, None)
    return conclude_element_attributes_update(element, attributes_changed=True)


class ElementsRemoveExtraneousAttributes(PanfluteElementPredicateFilterPairBase):
    def __init__(self, attribute_name_to_remove: str, attribute_removal_condition: PanfluteElementAttributeValuePredicate, *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)
        self._attribute_name_to_remove = attribute_name_to_remove
        self._attribute_removal_condition = attribute_removal_condition

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def valid_for_remove_element(element: panflute.Element) -> bool:
            return element_has_attribute_value(element, self._attribute_name_to_remove, self._attribute_removal_condition)
        yield valid_for_remove_element

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return f"element has attribute '{self._attribute_name_to_remove}' with value satisfying '{self._attribute_removal_condition}'"

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def remove_attribute(element: panflute.Element, doc: panflute.Doc) -> Optional[PanfluteElementLike]:
            return _remove_specific_attribute(element, doc, attribute_to_remove=self._attribute_name_to_remove)
        return remove_attribute

    @property
    def _describe_element_filter(self) -> str:
        return f"removes attribute '{self._attribute_name_to_remove}'"

    @property
    def _description_emoji_infix(self) -> str:
        return '💄'
