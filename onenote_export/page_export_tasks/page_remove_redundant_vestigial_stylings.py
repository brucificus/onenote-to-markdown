import functools
import inspect
import logging
import re

from collections.abc import Sequence
from typing import Callable, Dict, Iterable, Optional, Tuple

import panflute

from markdown_dom.MarkdownDocument import MarkdownDocument
from markdown_dom.PanfluteElementAccumulatorElementFilterContext import PanfluteElementAccumulatorElementFilterContext
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementContainerElementCtor, PanfluteElementFilter
from markdown_re import PanfluteElementLike
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporterSettings import OneNotePageExporterSettings, PanfluteElementStyleValuePredicate, \
    OneNotePageContentStyleExportElementStyleElementPushes, OneNotePageContentStyleExportElementStyleRemovals, \
    OneNotePageContentStyleExportElementClassElementPushes, OneNotePageContentStyleExportElementClassRemovals, \
    OneNotePageContentExportStyleSettings, OneNotePageContentExportClassSettings


css_unit_pattern = re.compile(r"^(\d*(?:\.\d+)?)\s*(.+)$")


promotion_combinable_element_transitions = (
    (panflute.Div, panflute.Doc),
    (panflute.Span, panflute.Doc),

    (panflute.Div, panflute.Div),
    (panflute.Span, panflute.Span),
    (panflute.Strikeout, panflute.Strikeout),
    (panflute.Strong, panflute.Strong),
    (panflute.Underline, panflute.Underline),
    (panflute.Emph, panflute.Emph),
    (panflute.Subscript, panflute.Subscript),
    (panflute.Superscript, panflute.Superscript),
    (panflute.Plain, panflute.Plain),
    (panflute.Para, panflute.Para),

    (panflute.Span, panflute.Plain),
    (panflute.Span, panflute.Div),
    (panflute.Span, panflute.ListItem),
    (panflute.Span, panflute.Strikeout),
    (panflute.Span, panflute.Strong),
    (panflute.Span, panflute.Underline),
    (panflute.Span, panflute.Emph),
    (panflute.Span, panflute.Subscript),
    (panflute.Span, panflute.Superscript),

    (panflute.Span, panflute.Link),

    (panflute.Span, panflute.Image),
    (panflute.Div, panflute.Image),

    (panflute.Span, panflute.Para),
    (panflute.Plain, panflute.Para),
)


def _is_style_match(style_parsed: Dict[str, str], style_name: str, style_value_condition: Optional[PanfluteElementStyleValuePredicate]) -> bool:
    if style_name not in style_parsed:
        return False

    style_value = style_parsed[style_name]
    if style_value_condition is None:
        return True
    if isinstance(style_value_condition, bool):
        return style_value_condition
    if isinstance(style_value_condition, str):
        return style_value in (style_value_condition, f'"{style_value_condition}"')
    if isinstance(style_value_condition, Sequence):
        return any(
            _is_style_match(style_parsed, style_name, style_value_condition_item) for style_value_condition_item in style_value_condition
        )
    if isinstance(style_value_condition, Iterable):
        return any(
            _is_style_match(style_parsed, style_name, style_value_condition_item) for style_value_condition_item in style_value_condition
        )
    if isinstance(style_value_condition, Callable):
        predicate_param_count = len(inspect.signature(style_value_condition).parameters)
        if predicate_param_count == 1:
            return style_value_condition(style_value)
        elif predicate_param_count == 2:
            (style_value_value, style_value_unit) = css_unit_pattern.match(style_value).groups()
            style_value_value = float(style_value_value)
            return style_value_condition(style_value_value, style_value_unit)
        else:
            raise ValueError(f"Unexpected number of parameters for style_value_condition: {predicate_param_count}")
    raise TypeError(f"Unexpected type for style_value_condition: {type(style_value_condition)}")


def _parse_html_style_attribute(style: str) -> dict:
    style_dict = {}
    for style_pair in style.split(";"):
        if style_pair.strip() == "":
            continue
        style_pair = style_pair.strip()
        style_key, style_value = style_pair.split(":")
        style_dict[style_key.strip()] = style_value.strip()
    return style_dict


def _build_html_style_attribute(style_dict: dict) -> str:
    style_pairs = []
    for style_key, style_value in style_dict.items():
        style_pairs.append(f"{style_key}:{style_value}")
    return "; ".join(style_pairs)


def _push_content(element: panflute.Element, new_child_element_type: PanfluteElementContainerElementCtor):
    new_child_element = new_child_element_type(*element.content)
    element.content.clear()
    element.content.append(new_child_element)

def _is_valid_for_children_promotion(element: panflute.Element) -> bool:
    classes_empty = (not hasattr(element, "classes") or (hasattr(element, "classes") and not element.classes))
    attributes_empty = (not hasattr(element, "attributes") or (hasattr(element, "attributes") and not element.attributes))

    element_type_pairs_valid = any(
        isinstance(element, possible_combo[0]) and isinstance(element.parent, possible_combo[1])
        for possible_combo in promotion_combinable_element_transitions
    )
    return classes_empty and attributes_empty and element_type_pairs_valid


def _promote_element_children(element: panflute.Element, _: panflute.Doc) -> PanfluteElementLike:
    if not _is_valid_for_children_promotion(element):
        raise ValueError(f"Element {element} is not valid for children promotion")

    return [*element.content]


def _create_predicated_element_filter(predicate: PanfluteElementPredicate, element_filter: PanfluteElementFilter) -> PanfluteElementFilter:
    @functools.wraps(element_filter)
    def predicated_element_filter(element: panflute.Element, doc: panflute.Doc) -> PanfluteElementLike:
        if predicate(element):
            return element_filter(element, doc)
        return None

    return predicated_element_filter


predicate_filter_pair = Tuple[PanfluteElementPredicate, PanfluteElementFilter]

all_table_elements: PanfluteElementPredicate = lambda e: isinstance(e, (panflute.Table, panflute.TableCell, panflute.TableRow, panflute.TableFoot, panflute.TableHead, panflute.TableBody))

def _has_nongridlike_nested_elements(table: panflute.Table) -> bool:
    return PanfluteElementAccumulatorElementFilterContext.any_elements(table, lambda e: all_table_elements(e) and ('rowspan' in e.attributes or 'colspan' in e.attributes))

def _has_styled_table_elements(table: panflute.Table) -> bool:
    return PanfluteElementAccumulatorElementFilterContext.any_elements(table, lambda e: all_table_elements(e) and (('style' in e.attributes and e.attributes['style']) or e.classes))

def _get_parent_table(element: panflute.Element) -> Optional[panflute.Table]:
    parent = element.parent
    while parent is not None and not isinstance(parent, panflute.Table):
        parent = parent.parent
    return parent

def _is_gridlike_table(table: panflute.Table) -> bool:
    return isinstance(table, panflute.Table) and not _has_nongridlike_nested_elements(table)

def _is_in_gridlike_table(element: panflute.Element) -> bool:
    return _is_gridlike_table(_get_parent_table(element))

def _create_styling_element_predicate_filter_pairs(style_settings: OneNotePageContentExportStyleSettings, class_settings: OneNotePageContentExportClassSettings) -> Sequence[predicate_filter_pair]:
    all_div_elements: PanfluteElementPredicate = lambda e: isinstance(e, panflute.Div)

    all_table_elements_in_gridlike_tables: PanfluteElementPredicate = lambda e: all_table_elements(e) and (_is_gridlike_table(e) or _is_in_gridlike_table(e))
    all_table_elements_in_tables: PanfluteElementPredicate = lambda e: all_table_elements(e) and (isinstance(e, panflute.Table) or _get_parent_table(e))

    all_elements_with_style: PanfluteElementPredicate = lambda e: isinstance(e, panflute.Element) and hasattr(e, "attributes") and "style" in e.attributes and e.attributes["style"]
    all_elements_with_classes: PanfluteElementPredicate = lambda e: isinstance(e, panflute.Element) and hasattr(e, "classes") and e.classes

    all_div_elements_with_style: PanfluteElementPredicate = lambda e: all_elements_with_style(e) and all_div_elements(e)
    all_div_elements_with_classes: PanfluteElementPredicate = lambda e: all_elements_with_classes(e) and all_div_elements(e)

    def conclude_element_classes_update(element: panflute.Element, classes_changed: bool) -> PanfluteElementLike:
        # If we made "major" changes to the element, making it redundant, remove it.
        should_promote_children = classes_changed and _is_valid_for_children_promotion(element)

        if should_promote_children:
            return [*element.content]

        return element

    def conclude_element_style_update(element: panflute.Element, style_parsed: dict, style_changed: bool) -> PanfluteElementLike:
        # Clean up the style attribute, and then clean up the attributes dict if we need to, too.
        if style_changed and len(style_parsed) == 0:
            element.attributes.pop("style")
        elif style_changed:
            element.attributes["style"] = _build_html_style_attribute(style_parsed)

        # If we made "major" changes to the element, making it redundant, remove it.
        should_promote_children = style_changed and _is_valid_for_children_promotion(element)

        if should_promote_children:
            return [*element.content]

        return element

    def create_stylings_update_filters_for_class_removals(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementClassRemovals) -> Iterable[predicate_filter_pair]:
        @functools.wraps(base_elements_predicate)
        def elements_predicate(element: panflute.Element, class_to_remove: str) -> bool:
            return base_elements_predicate(element) and class_to_remove in element.classes

        def update_stylings_class_removals(element: panflute.Element, _: panflute.Doc, class_to_remove: str) -> PanfluteElementLike:
            element.classes.remove(class_to_remove)
            return conclude_element_classes_update(element, classes_changed=True)

        for class_to_remove in removals:
            elements_predicate_final = functools.partial(elements_predicate, class_to_remove=class_to_remove)
            base_filter = functools.partial(update_stylings_class_removals, class_to_remove=class_to_remove)
            yield elements_predicate_final, base_filter

    def create_stylings_update_filters_for_class_pushes(base_elements_predicate: PanfluteElementPredicate, pushes: OneNotePageContentStyleExportElementClassElementPushes) -> Iterable[predicate_filter_pair]:
        @functools.wraps(base_elements_predicate)
        def elements_predicate(element: panflute.Element, class_to_push: str) -> bool:
            return base_elements_predicate(element) and class_to_push in element.classes

        def update_stylings_class_pushes(element: panflute.Element, _: panflute.Doc, class_to_push: str) -> PanfluteElementLike:
            element.classes.remove(class_to_push)
            new_child_element_type = pushes[class_to_push]
            _push_content(element, new_child_element_type)
            return conclude_element_classes_update(element, classes_changed=True)

        for class_to_push in pushes:
            elements_predicate_final = functools.partial(elements_predicate, class_to_push=class_to_push)
            base_filter = functools.partial(update_stylings_class_pushes, class_to_push=class_to_push)
            yield elements_predicate_final, base_filter

    def create_stylings_update_filters_for_style_removals(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementStyleRemovals) -> Iterable[predicate_filter_pair]:
        @functools.wraps(base_elements_predicate)
        def elements_predicate(element: panflute.Element, style_to_remove: str, style_value_removal_condition: PanfluteElementStyleValuePredicate) -> bool:
            if not base_elements_predicate(element):
                return False
            if "style" not in element.attributes:
                return False
            style_parsed = _parse_html_style_attribute(element.attributes["style"])
            if style_to_remove not in style_parsed:
                return False
            return _is_style_match(style_parsed, style_to_remove, style_value_removal_condition)

        def update_stylings_style_removals(element: panflute.Element, _: panflute.Doc, style_to_remove: str) -> PanfluteElementLike:
            style_parsed = _parse_html_style_attribute(element.attributes["style"])
            style_parsed.pop(style_to_remove)
            return conclude_element_style_update(element, style_parsed, style_changed=True)

        for style_to_remove in removals:
            style_value_removal_condition = removals[style_to_remove]
            elements_predicate_final = functools.partial(elements_predicate, style_to_remove=style_to_remove, style_value_removal_condition=style_value_removal_condition)
            base_filter = functools.partial(update_stylings_style_removals, style_to_remove=style_to_remove)
            yield elements_predicate_final, base_filter

    def create_stylings_update_filters_for_style_pushes(base_elements_predicate: PanfluteElementPredicate, pushes: OneNotePageContentStyleExportElementStyleElementPushes) -> Iterable[predicate_filter_pair]:
        @functools.wraps(base_elements_predicate)
        def elements_predicate(element: panflute.Element, style_to_push: str, style_value_to_push: PanfluteElementStyleValuePredicate) -> bool:
            if not base_elements_predicate(element):
                return False
            style_parsed = _parse_html_style_attribute(element.attributes["style"])
            if style_to_push not in style_parsed:
                return False
            return _is_style_match(style_parsed, style_to_push, style_value_to_push)

        def update_stylings_style_pushes(element: panflute.Element, _: panflute.Doc, style_to_push: str, style_value_to_push: str) -> PanfluteElementLike:
            style_parsed = _parse_html_style_attribute(element.attributes["style"])
            style_parsed.pop(style_to_push)
            new_child_element_type = pushes[style_to_push][style_value_to_push]
            _push_content(element, new_child_element_type)
            return conclude_element_style_update(element, style_parsed, style_changed=True)

        for style_to_push in pushes:
            for style_value_to_push in pushes[style_to_push]:
                elements_predicate_final = functools.partial(elements_predicate, style_to_push=style_to_push, style_value_to_push=style_value_to_push)
                base_filter = functools.partial(update_stylings_style_pushes, style_to_push=style_to_push, style_value_to_push=style_value_to_push)
                yield elements_predicate_final, base_filter

    style_and_class_updating_element_predicate_filter_pairs: Sequence[predicate_filter_pair] = (
        *create_stylings_update_filters_for_class_removals(all_table_elements_in_gridlike_tables, class_settings.gridlike_table_elements.removals),
        *create_stylings_update_filters_for_class_removals(all_table_elements_in_tables, class_settings.all_table_elements.removals),
        *create_stylings_update_filters_for_class_removals(all_div_elements_with_classes, class_settings.divs.removals),
        *create_stylings_update_filters_for_class_removals(all_elements_with_classes, class_settings.all_elements.removals),

        *create_stylings_update_filters_for_class_pushes(all_table_elements_in_gridlike_tables, class_settings.gridlike_table_elements.pushes),
        *create_stylings_update_filters_for_class_pushes(all_table_elements_in_tables, class_settings.all_table_elements.pushes),
        *create_stylings_update_filters_for_class_pushes(all_div_elements_with_classes, class_settings.divs.pushes),
        *create_stylings_update_filters_for_class_pushes(all_elements_with_classes, class_settings.all_elements.pushes),


        *create_stylings_update_filters_for_style_removals(all_table_elements_in_gridlike_tables, style_settings.gridlike_table_elements.removals),
        *create_stylings_update_filters_for_style_removals(all_table_elements_in_tables, style_settings.all_table_elements.removals),
        *create_stylings_update_filters_for_style_removals(all_div_elements_with_style, style_settings.divs.removals),
        *create_stylings_update_filters_for_style_removals(all_elements_with_style, style_settings.all_elements.removals),

        *create_stylings_update_filters_for_style_pushes(all_table_elements_in_gridlike_tables, style_settings.gridlike_table_elements.pushes),
        *create_stylings_update_filters_for_style_pushes(all_table_elements_in_tables, style_settings.all_table_elements.pushes),
        *create_stylings_update_filters_for_style_pushes(all_div_elements_with_style, style_settings.divs.pushes),
        *create_stylings_update_filters_for_style_pushes(all_elements_with_style, style_settings.all_elements.pushes),
    )

    return style_and_class_updating_element_predicate_filter_pairs


def _apply_predicate_filter_pairs_continuously_until_steady_state(doc: MarkdownDocument, predicate_filter_pairs: Sequence[predicate_filter_pair]):
    predicates_and_predicated_filters = ((
        predicate_filter_pair[0],
        _create_predicated_element_filter(predicate_filter_pair[0], predicate_filter_pair[1]),
    ) for predicate_filter_pair in predicate_filter_pairs)

    seen_doc_state_hashes = set()
    seen_doc_state_hashes.add(doc.checksum)
    seen_doc_state_hashes_count_last = 0
    while seen_doc_state_hashes_count_last != len(seen_doc_state_hashes):
        seen_doc_state_hashes_count_last = len(seen_doc_state_hashes)
        for (predicate, predicated_filter) in predicates_and_predicated_filters:
            if doc.any_elements(predicate):
                doc.update_via_panflute_filter(element_filter=predicated_filter)


def page_remove_redundant_vestigial_stylings(context: OneNotePageExportTaskContext, settings: OneNotePageExporterSettings, logger: logging.Logger):
    style_settings = settings.pages_content_style_settings
    class_settings = settings.pages_content_class_settings

    logger.info(f"💄 Removing redundant vestigial stylings: '{context.output_md_path}'")
    doc = context.output_md_document
    style_and_class_updating_element_predicate_filter_pairs = _create_styling_element_predicate_filter_pairs(style_settings, class_settings)
    _apply_predicate_filter_pairs_continuously_until_steady_state(doc, style_and_class_updating_element_predicate_filter_pairs)

    logger.info(f"🔥 Removing redundant vestigial styling elements: '{context.output_md_path}'")
    element_cleanup_predicate_filter_pair = (
        _is_valid_for_children_promotion,
        _create_predicated_element_filter(_is_valid_for_children_promotion, _promote_element_children)
    )
    _apply_predicate_filter_pairs_continuously_until_steady_state(doc, [element_cleanup_predicate_filter_pair])
