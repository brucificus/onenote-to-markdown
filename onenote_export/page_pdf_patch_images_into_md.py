import functools
import logging
import pathlib
import urllib
from typing import Tuple, Optional

import panflute

from markdown_dom.MarkdownDocument import PanfluteElementFilter
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from pdf_inspection.PdfDocumentPage import PdfDocumentPage


def page_pdf_patch_images_into_md(context: OneNotePageExportTaskContext, logger: logging.Logger):
    def _count_non_ignorable_drawings(pdf_page: PdfDocumentPage) -> int:
        return len([drawing for drawing in pdf_page.drawings if not drawing.is_effectively_empty])

    def _extract_pdf_pictures() -> list[pathlib.Path]:
        result_image_names = []
        doc = context.page_as_pdf_document

        if len(doc.pages) == 0:
            logger.info(f"🚫 Error opening the PDF for '{context.output_md_path}' - it has no pages.")
            return result_image_names

        for pdf_page in doc.pages:
            for pdf_page_image in pdf_page.images:
                img_num_suffix = str(pdf_page_image.document_order_image_index).zfill(3)
                png_name = "%s_%s.png" % (context.safe_filename_base, img_num_suffix)
                page_relative_png_path = context.assets_dir / pathlib.Path(png_name)
                png_output_path = context.output_dir / page_relative_png_path
                logger.debug("🖼️ Writing png: %s" % str(png_output_path))
                pdf_page_image.export_png(png_output_path)
                result_image_names.append(page_relative_png_path)
            count_of_non_ignorable_drawings = _count_non_ignorable_drawings(pdf_page)
            if count_of_non_ignorable_drawings > 0:
                logger.warning(
                    f"⚠️ Page {pdf_page.page_index} of the PDF for '{context.output_md_path}' has {count_of_non_ignorable_drawings} non-empty drawings that are not exported.")
        return result_image_names

    broken_image_url_prefix = "media/image"

    def is_image_with_broken_url(element: panflute.Element, _) -> bool:
        return isinstance(element, panflute.Image) and element.url.startswith(broken_image_url_prefix)

    def _count_broken_images(doc: panflute.Doc) -> int:
        return doc.count_elements(is_image_with_broken_url)

    def _fix_image_names(image_names_to_fix: list[pathlib.Path]):
        doc = context.output_md_document
        element_filters: Tuple[PanfluteElementFilter, ...] = ()

        def update_image_url(element: panflute.Element, _, new_image_url: str, image_index: int) -> Optional[panflute.Element]:
            if is_image_with_broken_url(element, _):
                broken_image_path_without_suffix_letters = broken_image_url_prefix + str(image_index + 1) + "."
                if element.url.startswith(broken_image_path_without_suffix_letters):
                    element.url = new_image_url

        for i, path in enumerate(image_names_to_fix):
            path_str = urllib.parse.quote(str(path).encode('utf8'), safe='\\').replace('\\', '/')
            element_filters += (functools.partial(update_image_url, new_image_url=path_str, image_index=i),)

        doc.update_via_panflute_filters(element_filters=element_filters)
        remaining_broken_image_count = _count_broken_images(doc)

        if remaining_broken_image_count > 0:
            logger.warning(f"⚠️ Still has broken images: '{context.output_md_path}'")

    # Output picture assets to folder.
    logger.info(f"✂️️ Extracting PDF pictures: '{context.output_md_path}'")
    image_names_extracted_from_pdf = _extract_pdf_pictures()

    # Replace image names in markdown file.
    logger.info(f"📝️️ Updating image references in markdown: '{context.output_md_path}'")
    _fix_image_names(image_names_extracted_from_pdf)
