import functools
import logging
from collections.abc import Sequence
from typing import Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPair, \
    AbstractPanfluteElementPredicateFilterPair
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementAttributeValuePredicate
from markdown_re import PanfluteElementLike
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporterSettings import OneNotePageExporterSettings, \
    OneNotePageContentExportExtraAttributesSettings, OneNotePageContentStyleExportElementDataStyleRemovals
from onenote_export.page_export_tasks._element_predicates import element_is_valid_for_children_promotion, \
    element_has_attributes, element_has_attribute_value
from onenote_export.page_export_tasks._element_updates import \
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state, \
    promote_element_children


def _create_attribute_cleaning_element_predicate_filter_pairs(attribute_settings: OneNotePageContentExportExtraAttributesSettings) -> Sequence[AbstractPanfluteElementPredicateFilterPair]:
    def conclude_element_attributes_update(element: panflute.Element, attributes_changed: bool) -> PanfluteElementLike:
        # If we made "major" changes to the element, making it redundant, remove it.
        should_promote_children = attributes_changed and element_is_valid_for_children_promotion(element)
        if should_promote_children:
            return [*element.content]
        return element

    def create_attributes_update_filters_for_attribute_removals(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementDataStyleRemovals) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        @functools.wraps(base_elements_predicate)
        def valid_for_remove_specific_attribute(element: panflute.Element, attribute_to_remove: str, attribute_removal_condition: PanfluteElementAttributeValuePredicate) -> bool:
            if not base_elements_predicate(element):
                return False
            return element_has_attribute_value(
                element,
                attribute_to_remove,
                attribute_removal_condition
            )

        def remove_specific_attribute(element: panflute.Element, _: panflute.Doc, attribute_to_remove: str) -> PanfluteElementLike:
            element.attributes.pop(attribute_to_remove, None)
            return conclude_element_attributes_update(element, attributes_changed=True)

        for attribute_to_remove in removals:
            attribute_removal_condition_settings = removals[attribute_to_remove]
            final_predicate = functools.partial(valid_for_remove_specific_attribute, attribute_to_remove=attribute_to_remove, attribute_removal_condition=attribute_removal_condition_settings)
            final_filter = functools.partial(remove_specific_attribute, attribute_to_remove=attribute_to_remove)
            yield PanfluteElementPredicateFilterPair(final_predicate, final_filter)

    attribute_cleaning_element_predicate_filter_pairs: Sequence[PanfluteElementPredicateFilterPair] = (
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
    element_cleanup_predicate_filter_pair = PanfluteElementPredicateFilterPair(element_is_valid_for_children_promotion, promote_element_children)
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, [element_cleanup_predicate_filter_pair])
