import functools

import fitz
import os
import pathlib
import re
import shutil
from logging import info as log
from typing import Callable
import urllib

from onenote import OneNotePage
from . import OneNotePageExportError
from .OneNoteExportMiddleware import OneNoteExportMiddleware
from .OneNoteExportMiddlewarePartial import OneNoteExportMiddlewarePartial
from .OneNotePageAssetExportError import OneNotePageAssetExportError
from .OneNotePageExportMiddlewareContext import OneNotePageExportMiddlewareContext
from .type_variables import TReturn


class OneNotePageExporter(OneNoteExportMiddleware[OneNotePage, None]):
    def __init__(self):
        pass

    def __call__(
            self,
            context: OneNotePageExportMiddlewareContext,
            next_middleware: OneNoteExportMiddlewarePartial,
    ) -> TReturn:
        return self.export_page(context, next_middleware)

    def export_page(
        self,
        context: OneNotePageExportMiddlewareContext,
        next_middleware: OneNoteExportMiddlewarePartial,
    ) -> TReturn:
        if not isinstance(context, OneNotePageExportMiddlewareContext):
            raise TypeError(f"Context must be an instance of OneNotePageExportMiddlewareContext, not {type(context)}")

        with context:
            page = context.node
            def _ensure_output_dir_exists():
                if not os.path.exists(context.output_dir):
                    os.makedirs(context.output_dir, exist_ok=True)  # 'exist_ok' is needed for parallel execution.

            def _ensure_assets_dir_exists():
                assets_dir = context.output_dir / context.assets_dir
                if not os.path.exists(assets_dir):
                    os.makedirs(assets_dir, exist_ok=True)  # 'exist_ok' is needed for parallel execution.

            def _pdf_patch_images_into_md() -> TReturn:
                def _count_non_ignorable_drawings(pdf_page: fitz.Page) -> int:
                    count: int = 0
                    for pdf_page_drawing in pdf_page.get_drawings():
                        drawing_items = pdf_page_drawing['items']
                        drawing_items_count = len(drawing_items)
                        if drawing_items_count == 0:
                            continue
                        if drawing_items_count == 1:
                            drawing_item = drawing_items[0]
                            drawing_item_shape = drawing_item[1]
                            is_rect = isinstance(drawing_item_shape, fitz.Rect)
                            if is_rect:
                                rect_height_is_default = abs(drawing_item_shape.height - 0.72) < 0.01
                                rect_width_is_default = abs(drawing_item_shape.width - 100.37) < 0.01
                                if rect_width_is_default or rect_height_is_default:
                                    continue
                        count += 1
                    return count

                def _try_save_pix_image(pix: fitz.Pixmap, png_output_path: pathlib.Path):
                    save_image: callable
                    # https://pymupdf.readthedocs.io/en/latest/pixmap.html#Pixmap.n
                    if pix.n < 5:
                        save_image = functools.partial(pix.save, str(png_output_path))
                        pix = None
                        del pix
                    else:
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        save_image = functools.partial(pix1.save, str(png_output_path))
                        pix1 = None
                        del pix1
                    try:
                        save_image()
                    except Exception as e:
                        raise OneNotePageAssetExportError(page, e) from e
                    finally:
                        save_image = None
                        del save_image

                def _extract_pdf_pictures() -> list[pathlib.Path]:
                    _ensure_assets_dir_exists()
                    result_image_names = []
                    doc = context.pymupdf_document
                    img_num = 0
                    page_index = 0

                    if len(doc) == 0:
                        log(f"❗🚫 Error opening the PDF for '{context.output_md_path}' - it has no pages.")
                        return result_image_names
                    # https://pymupdf.readthedocs.io/en/latest/document.html#Document.pages
                    for pdf_page in doc.pages():
                        # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_images
                        for pdf_page_image in pdf_page.get_images():
                            xref = pdf_page_image[0]
                            pix = fitz.Pixmap(doc, xref)
                            png_name = "%s_%s.png" % (context.safe_page_name, str(img_num).zfill(3))
                            page_relative_png_path = context.assets_dir / pathlib.Path(png_name)
                            png_output_path = context.output_dir / page_relative_png_path
                            log("🖼️ Writing png: %s" % str(png_output_path))
                            _try_save_pix_image(pix, png_output_path)
                            result_image_names.append(page_relative_png_path)
                            img_num += 1
                        count_of_non_ignorable_drawings = _count_non_ignorable_drawings(pdf_page)
                        if count_of_non_ignorable_drawings > 0:
                            log(f"⚠️ !!WARNING!! Page {page_index} of the PDF for '{context.output_md_path}' has {count_of_non_ignorable_drawings} non-empty drawings that are not exported.")
                        page_index += 1
                    return result_image_names

                def _fix_image_names(image_names_to_fix: list[pathlib.Path]):
                    tmp_path = context.output_md_path.with_suffix(context.output_md_path.suffix + '.tmp')
                    i = 0
                    with open(context.output_md_path, 'r', encoding='utf-8') as f_md:
                        with open(tmp_path, 'w', encoding='utf-8') as f_tmp:
                            body_md = f_md.read()
                            for i, path in enumerate(image_names_to_fix):
                                path_str_for_sub = urllib.parse.quote(str(path).encode('utf8'), safe='\\').replace('\\', '/')
                                body_md = re.sub("media/image" + str(i + 1) + r"\.\w+", path_str_for_sub, body_md)
                            f_tmp.write(body_md)
                            body_remaining_broken_image_count = len(re.findall(r"media/image\d+\.\w+", body_md))
                            if body_remaining_broken_image_count > 0:
                                log(f"⚠️ Still has broken images: '{context.output_md_path}'")
                    shutil.move(tmp_path, context.output_md_path)

                # Output picture assets to folder.
                log(f"✂️️ Extracting PDF pictures: '{context.output_md_path}'")
                image_names_extracted_from_pdf = _extract_pdf_pictures()

                # Replace image names in markdown file.
                log(f"📝️️ Updating image references in markdown: '{context.output_md_path}'")
                _fix_image_names(image_names_extracted_from_pdf)

                return next_middleware(context)

            _ensure_output_dir_exists()
            context.run_pandoc_conversion_to_markdown()
            _pdf_patch_images_into_md()

            return next_middleware(context)
