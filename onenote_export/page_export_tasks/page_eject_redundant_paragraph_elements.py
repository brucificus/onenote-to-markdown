import logging

from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.page_export_tasks.ElementsEjectRedundantParagraphs import EjectRedundantParagraphElements
from onenote_export.page_export_tasks._element_updates import \
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state


def page_eject_redundant_paragraph_elements(context: OneNotePageExportTaskContext, logger: logging.Logger):
    logger.info(f"📼 Ejecting redundant paragraph elements: '{context.output_md_path}'")
    doc = context.output_md_document
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, (EjectRedundantParagraphElements(),))
