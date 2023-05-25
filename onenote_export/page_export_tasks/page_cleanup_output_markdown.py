import logging
from typing import Tuple, Iterable

from markdown_dom.PanfluteElementPredicateFilterPair import AbstractPanfluteElementPredicateFilterPair
from markdown_dom.type_variables import PanfluteElementPredicate
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporterSettings import OneNotePageExporterSettings, \
    OneNotePageContentStyleExportElementDataStyleRemovals
from onenote_export.page_export_tasks.ElementsEjectRedundantParagraphs import EjectRedundantParagraphElements
from onenote_export.page_export_tasks.ElementsPromoteEmptyElementChildren import ElementsPromoteEmptyElementChildren
from onenote_export.page_export_tasks.ElementsRemoveExtraneousAttributes import ElementsRemoveExtraneousAttributes
from onenote_export.page_export_tasks.ElementsReparseEmbeddedHtml import ElementsReparseEmbeddedHtml
from onenote_export.page_export_tasks.ElementsSimplifyTableColspec import ElementsSimplifyTableColspec
from onenote_export.page_export_tasks._create_styling_element_predicate_filter_pairs import \
    _create_styling_element_predicate_filter_pairs
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


def page_cleanup_output_markdown(context: OneNotePageExportTaskContext, settings: OneNotePageExporterSettings, logger: logging.Logger):
    logger.info(f"💄 Applying page element cleanup: '{context.output_md_path}'")
    doc = context.output_md_document
    element_predicate_filter_pairs: Tuple[AbstractPanfluteElementPredicateFilterPair, ...] = ()

    # 💫️️ Reparse embedded raw HTML.
    element_predicate_filter_pairs += (ElementsReparseEmbeddedHtml(),)

    # 💄 Remove vestigial element attributes.
    if settings.pages_extra_attributes_settings is not None:
        element_predicate_filter_pairs += tuple(_create_attributes_update_filters_for_attribute_removals(
            element_has_attributes,
            settings.pages_extra_attributes_settings.all_elements.removals,
        ))

    # 💄 Clean up vestigial table column specifiers.
    if settings.pages_table_element_colspec_handling is not None:
        element_predicate_filter_pairs += (ElementsSimplifyTableColspec(),)

    # 💄 Remove redundant vestigial stylings.
    if settings.pages_content_style_settings or settings.pages_content_class_settings:
        style_settings = settings.pages_content_style_settings
        class_settings = settings.pages_content_class_settings
        element_predicate_filter_pairs += tuple(_create_styling_element_predicate_filter_pairs(style_settings, class_settings))

    # 🔥 Remove redundant vestigial elements.
    element_predicate_filter_pairs += (ElementsPromoteEmptyElementChildren(),)

    # 📼 Eject redundant paragraph elements.
    element_predicate_filter_pairs += (EjectRedundantParagraphElements(),)

    # 💫💄🔥📼 Execute the element predicate filter pairs until the document is stable.
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, predicate_filter_pairs=element_predicate_filter_pairs)
