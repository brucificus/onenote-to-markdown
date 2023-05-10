import logging
from collections.abc import Sequence
from typing import Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import AbstractPanfluteElementPredicateFilterPair, \
    PanfluteElementPredicateFilterPair
from markdown_re import PanfluteElementLike
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporterSettings import OneNotePageExporterSettings
from onenote_export.page_export_tasks._element_updates import \
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state

panflute_table_colspec_default_width_specifier = 'ColWidthDefault'


def _create_colspec_cleaning_element_predicate_filter_pairs() -> Sequence[AbstractPanfluteElementPredicateFilterPair]:
    def create_colspec_update_filters_for_colspec_cleanup() -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        def valid_for_update_colspec(element: panflute) -> bool:
            if not isinstance(element, panflute.Table):
                return False
            element: panflute.Table

            if not element.colspec:
                return False

            return not all(c[1] == panflute_table_colspec_default_width_specifier for c in element.colspec)

        def update_colspec(element: panflute.Table, _: panflute.Doc) -> PanfluteElementLike:
            element.colspec = ((c[0], panflute_table_colspec_default_width_specifier) for c in element.colspec)
            return element

        yield PanfluteElementPredicateFilterPair(valid_for_update_colspec, update_colspec)

    colspec_cleaning_element_predicate_filter_pairs: Sequence[AbstractPanfluteElementPredicateFilterPair] = (
        *create_colspec_update_filters_for_colspec_cleanup(),
    )

    return colspec_cleaning_element_predicate_filter_pairs


def page_table_element_colspec_cleanup(context: OneNotePageExportTaskContext, settings: OneNotePageExporterSettings, logger: logging.Logger):
    handling_setting = settings.pages_table_element_colspec_handling
    if not handling_setting:
        logger.info(f"🚫 Skipping vestigial table column specifiers cleanup: '{context.output_md_path}'")
        return

    logger.info(f"💄 Cleaning up vestigial table column specifiers: '{context.output_md_path}'")
    doc = context.output_md_document
    colspec_cleaning_element_predicate_filter_pairs = _create_colspec_cleaning_element_predicate_filter_pairs()
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, colspec_cleaning_element_predicate_filter_pairs)
