import functools
import logging
from collections.abc import Sequence
from typing import Iterable

import panflute

from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementAttributeValuePredicate
from markdown_re import PanfluteElementLike
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporterSettings import OneNotePageExporterSettings, \
    OneNotePageContentExportExtraAttributesSettings, OneNotePageContentStyleExportElementDataStyleRemovals
from onenote_export.page_export_tasks._element_updates import predicate_filter_pair, \
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state, create_predicated_element_filter, \
    promote_element_children
from onenote_export.page_export_tasks._element_predicates import element_is_valid_for_children_promotion, \
    element_has_attributes, element_has_attribute_value


def _create_attribute_cleaning_element_predicate_filter_pairs(attribute_settings: OneNotePageContentExportExtraAttributesSettings) -> Sequence[predicate_filter_pair]:
    def conclude_element_attributes_update(element: panflute.Element, attributes_changed: bool) -> PanfluteElementLike:
        # If we made "major" changes to the element, making it redundant, remove it.
        should_promote_children = attributes_changed and element_is_valid_for_children_promotion(element)
        if should_promote_children:
            return [*element.content]
        return element

    def create_attributes_update_filters_for_attribute_removals(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementDataStyleRemovals) -> Iterable[predicate_filter_pair]:
        @functools.wraps(base_elements_predicate)
        def elements_predicate(element: panflute.Element, attribute_to_remove: str, attribute_removal_condition: PanfluteElementAttributeValuePredicate) -> bool:
            if not base_elements_predicate(element):
                return False
            return element_has_attribute_value(
                element,
                attribute_to_remove,
                attribute_removal_condition
            )

        def remove_element_attribute(element: panflute.Element, _: panflute.Doc, attribute_to_remove: str) -> PanfluteElementLike:
            element.attributes.pop(attribute_to_remove, None)
            return conclude_element_attributes_update(element, attributes_changed=True)

        for attribute_to_remove in removals:
            attribute_removal_condition = removals[attribute_to_remove]
            elements_predicate_final = functools.partial(elements_predicate, attribute_to_remove=attribute_to_remove, attribute_removal_condition=attribute_removal_condition)
            base_filter = functools.partial(remove_element_attribute, attribute_to_remove=attribute_to_remove)
            yield elements_predicate_final, base_filter

    attribute_cleaning_element_predicate_filter_pairs: Sequence[predicate_filter_pair] = (
        *create_attributes_update_filters_for_attribute_removals(element_has_attributes, attribute_settings.all_elements.removals),
    )

    return attribute_cleaning_element_predicate_filter_pairs


def page_remove_extraneous_element_attributes(context: OneNotePageExportTaskContext, settings: OneNotePageExporterSettings, logger: logging.Logger):
    attribute_settings = settings.pages_extra_attributes_settings

    logger.info(f"💄 Removing vestigial element attributes: '{context.output_md_path}'")
    doc = context.output_md_document
    attribute_cleaning_element_predicate_filter_pairs = _create_attribute_cleaning_element_predicate_filter_pairs(attribute_settings)
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, attribute_cleaning_element_predicate_filter_pairs)

    logger.info(f"🔥 Removing redundant vestigial elements: '{context.output_md_path}'")
    element_cleanup_predicate_filter_pair = (
        element_is_valid_for_children_promotion,
        create_predicated_element_filter(element_is_valid_for_children_promotion, promote_element_children)
    )
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, [element_cleanup_predicate_filter_pair])
