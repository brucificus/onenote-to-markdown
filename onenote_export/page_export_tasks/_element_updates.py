from typing import Sequence

import panflute

from markdown_dom.MarkdownDocument import MarkdownDocument
from markdown_dom.PanfluteElementPredicateFilterPair import AbstractPanfluteElementPredicateFilterPair
from markdown_dom.type_variables import PanfluteElementContainerElementCtor
from markdown_re import PanfluteElementLike
from onenote_export.page_export_tasks._element_predicates import element_is_valid_for_children_promotion
from onenote_export.page_export_tasks._style_attribute import build_html_style_attribute


def push_element_content(element: panflute.Element, new_child_element_type: PanfluteElementContainerElementCtor):
    new_child_element = new_child_element_type(*element.content)
    element.content.clear()
    element.content.append(new_child_element)


def promote_element_children(element: panflute.Element, _: panflute.Doc) -> PanfluteElementLike:
    if not element_is_valid_for_children_promotion(element):
        raise ValueError(f"Element {element} is not valid for children promotion")

    return [*element.content]


def document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc: MarkdownDocument, predicate_filter_pairs: Sequence[AbstractPanfluteElementPredicateFilterPair]):
    seen_doc_state_hashes = set()
    seen_doc_state_hashes.add(doc.checksum)
    seen_doc_state_hashes_count_last = 0
    while seen_doc_state_hashes_count_last != len(seen_doc_state_hashes):
        seen_doc_state_hashes_count_last = len(seen_doc_state_hashes)
        for predicated_element_filter in predicate_filter_pairs:
            doc.update_via_panflute_filter(element_filter=predicated_element_filter)


def conclude_element_classes_update(element: panflute.Element, classes_changed: bool) -> PanfluteElementLike:
    # If we made "major" changes to the element, making it redundant, remove it.
    should_promote_children = classes_changed and element_is_valid_for_children_promotion(element)

    if should_promote_children:
        return [*element.content]

    return element


def conclude_element_style_update(element: panflute.Element, style_parsed: dict, style_changed: bool) -> PanfluteElementLike:
    # Clean up the style attribute, and then clean up the attributes dict if we need to, too.
    if style_changed and len(style_parsed) == 0:
        element.attributes.pop("style")
    elif style_changed:
        element.attributes["style"] = build_html_style_attribute(style_parsed)

    # If we made "major" changes to the element, making it redundant, remove it.
    should_promote_children = style_changed and element_is_valid_for_children_promotion(element)

    if should_promote_children:
        return [*element.content]

    return element


def conclude_element_attributes_update(element: panflute.Element, attributes_changed: bool) -> PanfluteElementLike:
    # If we made "major" changes to the element, making it redundant, remove it.
    should_promote_children = attributes_changed and element_is_valid_for_children_promotion(element)
    if should_promote_children:
        return [*element.content]
    return element
