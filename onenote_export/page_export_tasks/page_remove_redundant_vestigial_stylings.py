import functools
import logging
from collections.abc import Sequence
from typing import Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPair, \
    AbstractPanfluteElementPredicateFilterPair
from markdown_dom.type_variables import PanfluteElementPredicate
from markdown_re import PanfluteElementLike
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporterSettings import OneNotePageExporterSettings, PanfluteElementStyleValuePredicate, \
    OneNotePageContentStyleExportElementStyleElementPushes, OneNotePageContentStyleExportElementStyleRemovals, \
    OneNotePageContentStyleExportElementClassElementPushes, OneNotePageContentStyleExportElementClassRemovals, \
    OneNotePageContentExportStyleSettings, OneNotePageContentExportClassSettings
from onenote_export.page_export_tasks._element_predicates import element_is_table_element_in_gridlike_table, \
    element_is_table_element_in_table, element_has_style, element_has_classes, element_is_div_with_any_style, \
    element_is_div_with_any_classes, element_is_valid_for_children_promotion, element_has_specific_class, \
    element_has_specific_style_value
from onenote_export.page_export_tasks._element_updates import push_element_content, \
    promote_element_children, document_apply_element_predicate_filter_pairs_continuously_until_steady_state
from onenote_export.page_export_tasks._style_attribute import parse_html_style_attribute, build_html_style_attribute


def _create_styling_element_predicate_filter_pairs(style_settings: OneNotePageContentExportStyleSettings, class_settings: OneNotePageContentExportClassSettings) -> Sequence[PanfluteElementPredicateFilterPair]:
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

    def create_stylings_update_filters_for_class_removals(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementClassRemovals) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        @functools.wraps(base_elements_predicate)
        def valid_for_remove_specific_class(element: panflute.Element, class_to_remove: str) -> bool:
            return base_elements_predicate(element) and element_has_specific_class(element, class_to_remove)

        def remove_specific_class(element: panflute.Element, _: panflute.Doc, class_to_remove: str) -> PanfluteElementLike:
            element.classes.remove(class_to_remove)
            return conclude_element_classes_update(element, classes_changed=True)

        for class_to_remove in removals:
            final_predicate = functools.partial(valid_for_remove_specific_class, class_to_remove=class_to_remove)
            final_filter = functools.partial(remove_specific_class, class_to_remove=class_to_remove)
            yield PanfluteElementPredicateFilterPair(final_predicate, final_filter)

    def create_stylings_update_filters_for_class_pushes(base_elements_predicate: PanfluteElementPredicate, pushes: OneNotePageContentStyleExportElementClassElementPushes) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        @functools.wraps(base_elements_predicate)
        def valid_for_push_specific_class(element: panflute.Element, class_to_push: str) -> bool:
            return base_elements_predicate(element) and element_has_specific_class(element, class_to_push)

        def push_specific_class(element: panflute.Element, _: panflute.Doc, class_to_push: str) -> PanfluteElementLike:
            new_child_element_type = pushes[class_to_push]
            push_element_content(element, new_child_element_type)
            element.classes.remove(class_to_push)
            return conclude_element_classes_update(element, classes_changed=True)

        for class_to_push in pushes:
            final_predicate = functools.partial(valid_for_push_specific_class, class_to_push=class_to_push)
            final_filter = functools.partial(push_specific_class, class_to_push=class_to_push)
            yield PanfluteElementPredicateFilterPair(final_predicate, final_filter)

    def create_stylings_update_filters_for_style_removals(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementStyleRemovals) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        @functools.wraps(base_elements_predicate)
        def valid_for_remove_specific_style(element: panflute.Element, style_to_remove: str, style_value_removal_condition: PanfluteElementStyleValuePredicate) -> bool:
            return base_elements_predicate(element) \
                and element_has_specific_style_value(element, style_to_remove, style_value_removal_condition)

        def remove_specific_style(element: panflute.Element, _: panflute.Doc, style_to_remove: str) -> PanfluteElementLike:
            style_parsed = parse_html_style_attribute(element.attributes["style"])
            style_parsed.pop(style_to_remove)
            return conclude_element_style_update(element, style_parsed, style_changed=True)

        for style_to_remove in removals:
            style_value_removal_condition = removals[style_to_remove]
            final_predicate = functools.partial(valid_for_remove_specific_style, style_to_remove=style_to_remove, style_value_removal_condition=style_value_removal_condition)
            final_filter = functools.partial(remove_specific_style, style_to_remove=style_to_remove)
            yield PanfluteElementPredicateFilterPair(final_predicate, final_filter)

    def create_stylings_update_filters_for_style_pushes(base_elements_predicate: PanfluteElementPredicate, pushes: OneNotePageContentStyleExportElementStyleElementPushes) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        @functools.wraps(base_elements_predicate)
        def valid_for_push_specific_style(element: panflute.Element, style_to_push: str, style_value_to_push: PanfluteElementStyleValuePredicate) -> bool:
            return base_elements_predicate(element) \
                and element_has_specific_style_value(element, style_to_push, style_value_to_push)

        def push_specific_style(element: panflute.Element, _: panflute.Doc, style_to_push: str, style_value_to_push: str) -> PanfluteElementLike:
            style_parsed = parse_html_style_attribute(element.attributes["style"])
            style_parsed.pop(style_to_push)
            new_child_element_type = pushes[style_to_push][style_value_to_push]
            push_element_content(element, new_child_element_type)
            return conclude_element_style_update(element, style_parsed, style_changed=True)

        for style_to_push in pushes:
            for style_value_to_push in pushes[style_to_push]:
                final_predicate = functools.partial(valid_for_push_specific_style, style_to_push=style_to_push, style_value_to_push=style_value_to_push)
                final_filter = functools.partial(push_specific_style, style_to_push=style_to_push, style_value_to_push=style_value_to_push)
                yield PanfluteElementPredicateFilterPair(final_predicate, final_filter)

    style_and_class_updating_element_predicate_filter_pairs: Sequence[AbstractPanfluteElementPredicateFilterPair] = (
        *create_stylings_update_filters_for_class_removals(element_is_table_element_in_gridlike_table, class_settings.gridlike_table_elements.removals),
        *create_stylings_update_filters_for_class_removals(element_is_table_element_in_table, class_settings.all_table_elements.removals),
        *create_stylings_update_filters_for_class_removals(element_is_div_with_any_classes, class_settings.divs.removals),
        *create_stylings_update_filters_for_class_removals(element_has_classes, class_settings.all_elements.removals),

        *create_stylings_update_filters_for_class_pushes(element_is_table_element_in_gridlike_table, class_settings.gridlike_table_elements.pushes),
        *create_stylings_update_filters_for_class_pushes(element_is_table_element_in_table, class_settings.all_table_elements.pushes),
        *create_stylings_update_filters_for_class_pushes(element_is_div_with_any_classes, class_settings.divs.pushes),
        *create_stylings_update_filters_for_class_pushes(element_has_classes, class_settings.all_elements.pushes),


        *create_stylings_update_filters_for_style_removals(element_is_table_element_in_gridlike_table, style_settings.gridlike_table_elements.removals),
        *create_stylings_update_filters_for_style_removals(element_is_table_element_in_table, style_settings.all_table_elements.removals),
        *create_stylings_update_filters_for_style_removals(element_is_div_with_any_style, style_settings.divs.removals),
        *create_stylings_update_filters_for_style_removals(element_has_style, style_settings.all_elements.removals),

        *create_stylings_update_filters_for_style_pushes(element_is_table_element_in_gridlike_table, style_settings.gridlike_table_elements.pushes),
        *create_stylings_update_filters_for_style_pushes(element_is_table_element_in_table, style_settings.all_table_elements.pushes),
        *create_stylings_update_filters_for_style_pushes(element_is_div_with_any_style, style_settings.divs.pushes),
        *create_stylings_update_filters_for_style_pushes(element_has_style, style_settings.all_elements.pushes),
    )

    return style_and_class_updating_element_predicate_filter_pairs


def page_remove_redundant_vestigial_stylings(context: OneNotePageExportTaskContext, settings: OneNotePageExporterSettings, logger: logging.Logger):
    style_settings = settings.pages_content_style_settings
    class_settings = settings.pages_content_class_settings

    logger.info(f"💄 Removing redundant vestigial stylings: '{context.output_md_path}'")
    doc = context.output_md_document
    style_and_class_updating_element_predicate_filter_pairs = _create_styling_element_predicate_filter_pairs(style_settings, class_settings)
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, style_and_class_updating_element_predicate_filter_pairs)

    logger.info(f"🔥 Removing redundant vestigial styling elements: '{context.output_md_path}'")
    element_cleanup_predicate_filter_pair = PanfluteElementPredicateFilterPair(element_predicate=element_is_valid_for_children_promotion, element_filter=promote_element_children)
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, [element_cleanup_predicate_filter_pair])
