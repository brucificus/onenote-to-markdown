from typing import Optional, Iterable

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementFilter
from onenote_export.page_export_tasks._element_predicates import element_is_valid_for_children_promotion
from onenote_export.page_export_tasks._element_updates import promote_element_children


class ElementsPromoteEmptyElementChildren(PanfluteElementPredicateFilterPairBase):
    def __init__(self, *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        yield element_is_valid_for_children_promotion

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return 'element has no meaningful attributes and has a parent-child relationship whitelisted for child promotion'

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        return promote_element_children

    @property
    def _describe_element_filter(self) -> str:
        return 'promotes element children into parent element'

    @property
    def _description_emoji_infix(self) -> str:
        return '🔥'
