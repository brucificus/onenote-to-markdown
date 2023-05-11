from typing import Optional, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementFilter
from markdown_re import PanfluteElementLike

panflute_table_colspec_default_width_specifier = 'ColWidthDefault'


class ElementsSimplifyTableColspec(PanfluteElementPredicateFilterPairBase):
    def __init__(self, *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def element_is_table(element: panflute.Element) -> bool:
            return isinstance(element, panflute.Table)

        def element_has_colspec(element: panflute.Table) -> bool:
            return element.colspec is not None

        def element_has_any_colspec_item_with_non_default_width_specifier(element: panflute.Table) -> bool:
            return any(c[1] != panflute_table_colspec_default_width_specifier for c in element.colspec)

        yield element_is_table
        yield element_has_colspec
        yield element_has_any_colspec_item_with_non_default_width_specifier

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return f"element is Table with non-default colspec"

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def update_colspec(element: panflute.Table, _: panflute.Doc) -> PanfluteElementLike:
            element.colspec = ((c[0], panflute_table_colspec_default_width_specifier) for c in element.colspec)
            return element
        return update_colspec

    @property
    def _describe_element_filter(self) -> str:
        return "sets colspec to default"

    @property
    def _description_emoji_infix(self) -> str:
        return '💄'
