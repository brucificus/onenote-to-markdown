import logging
import re

from markdown_dom.MarkdownDocument import MarkdownDocument
from markdown_re.MarkdownDocumentTextPattern import MarkdownDocumentTextPattern
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext


footer_text_pattern = MarkdownDocumentTextPattern(r'\s*Created with OneNote\.\s*', flags=re.MULTILINE)


def _eliminate_footer_text(doc: MarkdownDocument):
    footer_text_pattern.rm(doc)


def page_remove_onenote_footer(context: OneNotePageExportTaskContext, logger: logging.Logger):
    logger.info(f"📝️ Removing vestigial OneNote footer: '{context.output_md_path}'")

    _eliminate_footer_text(context.output_md_document)
