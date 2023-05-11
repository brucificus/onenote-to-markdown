from typing import Optional, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementFilter
from markdown_re import PanfluteElementLike
from onenote_export.page_export_tasks._element_predicates import element_has_classes, \
    element_has_attributes


class EjectRedundantParagraphElements(PanfluteElementPredicateFilterPairBase):
    def __init__(self, *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def element_is_paragraph(element: panflute.Element) -> bool:
            return isinstance(element, panflute.Para)

        def element_has_approved_parent_type(element: panflute.Element) -> bool:
            return isinstance(element.parent, (
                panflute.Span,
                panflute.ListItem,
                panflute.TableCell,
                panflute.TableHead,
                panflute.TableBody,
                panflute.TableFoot
            ))

        def element_has_no_meaningful_attributes_or_classes(element: panflute.Element) -> bool:
            return not element_has_classes(element) and not element_has_attributes(element)

        def element_is_only_child(element: panflute.Element) -> bool:
            return len(element.parent.content) == 1

        def element_has_child_promotion_strategy(element: panflute.Element) -> bool:
            single_child = element.content[0] if len(element.content) == 1 else None
            if single_child and isinstance(single_child, element.container.oktypes):
                return True
            return issubclass(panflute.Plain, element.container.oktypes)

        yield element_is_paragraph
        yield element_is_only_child
        yield element_has_approved_parent_type
        yield element_has_no_meaningful_attributes_or_classes
        yield element_has_child_promotion_strategy

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return 'element is paragraph and is only child and has parent of approved type and has no meaningful attributes or classes and has child promotion strategy'

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def eject_redundant_paragraph_element(element: panflute.Element, _: panflute.Doc) -> Optional[PanfluteElementLike]:
            element: panflute.Para
            single_child: Optional[panflute.Element] = element.content[0] if len(element.content) == 1 else None

            if single_child and isinstance(single_child, element.container.oktypes):
                return (single_child,)

            if issubclass(panflute.Plain, element.container.oktypes):
                return (panflute.Plain(*element.content),)

            raise ValueError(f"Element {element} is not valid for children promotion")
        return eject_redundant_paragraph_element

    @property
    def _describe_element_filter(self) -> str:
        return 'eject redundant paragraph element'

    @property
    def _description_emoji_infix(self) -> str:
        return '📼'
