import logging
from typing import Optional

import panflute

from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext


def page_reparse_embedded_html(context: OneNotePageExportTaskContext, logger: logging.Logger):
    def update_raw_block(element: panflute.Element, _) -> Optional[panflute.Element]:
        if isinstance(element, panflute.RawBlock):
            if element.format == "html":
                new_element = panflute.convert_text(
                    text=element.text,
                    input_format="html",
                    standalone=False,
                    output_format="panflute",
                    extra_args=[
                        "--wrap=preserve",
                    ]
                )
                return new_element
        return element

    logger.info(f"💫️️ Reparsing embedded raw HTML: '{context.output_md_path}'")
    doc = context.output_md_document
    doc.update_via_panflute_filters(element_filters=(update_raw_block,))
