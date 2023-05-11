import logging
from typing import Iterable

from markdown_dom.PanfluteElementPredicateFilterPair import AbstractPanfluteElementPredicateFilterPair
from markdown_dom.type_variables import PanfluteElementPredicate
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporterSettings import OneNotePageExporterSettings, \
    OneNotePageContentStyleExportElementDataStyleRemovals
from onenote_export.page_export_tasks.ElementsPromoteEmptyElementChildren import ElementsPromoteEmptyElementChildren
from onenote_export.page_export_tasks.ElementsRemoveExtraneousAttributes import ElementsRemoveExtraneousAttributes
from onenote_export.page_export_tasks._element_predicates import element_has_attributes
from onenote_export.page_export_tasks._element_updates import \
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state


def _create_attributes_update_filters_for_attribute_removals(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementDataStyleRemovals) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
    for attribute_name_to_remove in removals:
        attribute_removal_condition_settings = removals[attribute_name_to_remove]
        yield ElementsRemoveExtraneousAttributes(
            attribute_name_to_remove=attribute_name_to_remove,
            attribute_removal_condition=attribute_removal_condition_settings,
            base_elements_predicate=base_elements_predicate,
        )


def page_remove_extraneous_element_attributes(context: OneNotePageExportTaskContext, settings: OneNotePageExporterSettings, logger: logging.Logger):
    attribute_settings = settings.pages_extra_attributes_settings

    logger.info(f"💄 Removing vestigial element attributes: '{context.output_md_path}'")
    doc = context.output_md_document
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(
        doc,
        _create_attributes_update_filters_for_attribute_removals(
            element_has_attributes,
            attribute_settings.all_elements.removals,
        ),
    )

    logger.info(f"🔥 Removing redundant vestigial elements: '{context.output_md_path}'")
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, (ElementsPromoteEmptyElementChildren(),))
