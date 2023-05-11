import logging

from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.page_export_tasks.ElementsReparseEmbeddedHtml import ElementsReparseEmbeddedHtml


def page_reparse_embedded_html(context: OneNotePageExportTaskContext, logger: logging.Logger):
    logger.info(f"💫️️ Reparsing embedded raw HTML: '{context.output_md_path}'")
    doc = context.output_md_document
    doc.update_via_panflute_filters(element_filters=(ElementsReparseEmbeddedHtml(),))
