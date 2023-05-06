import logging
from typing import Optional

import panflute

from markdown_re import PanfluteElementLike
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.page_export_tasks._element_predicates import element_is_redundant_paragraph
from onenote_export.page_export_tasks._element_updates import \
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state


def _eject_redundant_paragraph_element(element: panflute.Para, _: panflute.Doc) -> Optional[PanfluteElementLike]:
    single_child = element.content[0] if len(element.content) == 1 else None

    if single_child and isinstance(single_child, element.container.oktypes):
        return (single_child,)

    if issubclass(panflute.Plain, element.container.oktypes):
        return (panflute.Plain(*element.content),)

    raise ValueError(f"Element {element} is not valid for children promotion")


def page_eject_redundant_paragraph_elements(context: OneNotePageExportTaskContext, logger: logging.Logger):
    logger.info(f"📼 Ejecting redundant paragraph elements: '{context.output_md_path}'")
    doc = context.output_md_document
    (predicate, element_filter) = (element_is_redundant_paragraph, _eject_redundant_paragraph_element)
    document_apply_element_predicate_filter_pairs_continuously_until_steady_state(doc, ((predicate, element_filter),))
