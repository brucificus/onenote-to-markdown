import logging

from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporterSettings import OneNotePageExporterSettings
from onenote_export.page_export_tasks.ElementsSimplifyTableColspec import ElementsSimplifyTableColspec
from onenote_export.page_export_tasks._element_updates import \
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state


def page_table_element_colspec_cleanup(context: OneNotePageExportTaskContext, settings: OneNotePageExporterSettings, logger: logging.Logger):
    handling_setting = settings.pages_table_element_colspec_handling
    if not handling_setting:
        logger.info(f"🚫 Skipping vestigial table column specifiers cleanup: '{context.output_md_path}'")
        return

    logger.info(f"💄 Cleaning up vestigial table column specifiers: '{context.output_md_path}'")
    doc = context.output_md_document
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, (ElementsSimplifyTableColspec(),))
