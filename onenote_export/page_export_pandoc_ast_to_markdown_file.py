import logging

from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext


def page_export_pandoc_ast_to_markdown_file(context: OneNotePageExportTaskContext, logger: logging.Logger):
    if context.output_md_document.is_dirty:
        logger.info(f"💾 ️Saving updated markdown: '{context.output_md_path}'")
        context.output_md_document.save()
    else:
        logger.info(f"✅ No changes to save for markdown: '{context.output_md_path}'")
