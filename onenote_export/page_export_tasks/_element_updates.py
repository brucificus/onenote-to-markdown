import functools
from typing import Sequence, Tuple

import panflute

from markdown_dom.MarkdownDocument import MarkdownDocument
from markdown_dom.type_variables import PanfluteElementContainerElementCtor, \
    PanfluteElementPredicate, PanfluteElementFilter
from markdown_re import PanfluteElementLike
from onenote_export.page_export_tasks._element_predicates import element_is_valid_for_children_promotion


predicate_filter_pair = Tuple[PanfluteElementPredicate, PanfluteElementFilter]


def push_element_content(element: panflute.Element, new_child_element_type: PanfluteElementContainerElementCtor):
    new_child_element = new_child_element_type(*element.content)
    element.content.clear()
    element.content.append(new_child_element)


def promote_element_children(element: panflute.Element, _: panflute.Doc) -> PanfluteElementLike:
    if not element_is_valid_for_children_promotion(element):
        raise ValueError(f"Element {element} is not valid for children promotion")

    return [*element.content]


def create_predicated_element_filter(predicate: PanfluteElementPredicate, element_filter: PanfluteElementFilter) -> PanfluteElementFilter:
    @functools.wraps(element_filter)
    def predicated_element_filter(element: panflute.Element, doc: panflute.Doc) -> PanfluteElementLike:
        if predicate(element):
            return element_filter(element, doc)
        return None

    return predicated_element_filter


def document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc: MarkdownDocument, predicate_filter_pairs: Sequence[predicate_filter_pair]):
    predicates_and_predicated_filters = ((
        predicate_filter_pairing[0],
        create_predicated_element_filter(predicate_filter_pairing[0], predicate_filter_pairing[1]),
    ) for predicate_filter_pairing in predicate_filter_pairs)

    seen_doc_state_hashes = set()
    seen_doc_state_hashes.add(doc.checksum)
    seen_doc_state_hashes_count_last = 0
    while seen_doc_state_hashes_count_last != len(seen_doc_state_hashes):
        seen_doc_state_hashes_count_last = len(seen_doc_state_hashes)
        for (predicate, predicated_filter) in predicates_and_predicated_filters:
            if doc.any_elements(predicate):
                doc.update_via_panflute_filter(element_filter=predicated_filter)
