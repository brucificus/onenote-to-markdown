import fitz
import os
import pathlib
import pywintypes
import re
import shutil
from logging import info as log
from typing import Callable
import urllib

from onenote import OneNotePage
from .OneNoteExportMiddleware import OneNoteExportMiddleware
from .OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from .OneNoteExportMiddlewarePartial import OneNoteExportMiddlewarePartial
from .temporary_file import temporary_file_path
from .type_variables import TReturn, TNode


class OneNotePageExporter(OneNoteExportMiddleware[OneNotePage, None]):
    def __init__(self,
                 *,
                 os_system: Callable[[str], None] = os.system,
                 ):
        self._os_system = os_system

    def __call__(
            self,
            context: OneNoteExportMiddlewareContext[OneNotePage],
            next_middleware: OneNoteExportMiddlewarePartial,
    ) -> TReturn:
        return self.export_page(context, next_middleware)

    def export_page(
        self,
        context: OneNoteExportMiddlewareContext[OneNotePage],
        next_middleware: OneNoteExportMiddlewarePartial,
    ) -> TReturn:
        page: OneNotePage = context.node
        safe_page_name: pathlib.Path = context.convert_node_name_to_path_component(context.node.name)

        def _ensure_output_dir_exists():
            if not os.path.exists(context.output_dir):
                os.makedirs(context.output_dir, exist_ok=True)  # 'exist_ok' is needed for parallel execution.

        def _ensure_assets_dir_exists():
            assets_dir = context.output_dir / context.assets_dir
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir, exist_ok=True)  # 'exist_ok' is needed for parallel execution.

        def _export_temporary_docx_and_use(enclosed_action: Callable[[pathlib.Path], TReturn]) -> TReturn:
            try:
                with temporary_file_path(suffix='.docx') as docx_path:
                    log(f"🖨️ Exporting temporary DOCX: '{docx_path}'")
                    page.export_docx(docx_path)
                    return enclosed_action(docx_path)
            except pywintypes.com_error:
                log(f"⚠️ !!WARNING!! Page Failed: '{page.name}'")
                return None

        def _export_temporary_pdf_and_use(enclosed_action: Callable[[pathlib.Path], TReturn]) -> TReturn:
            try:
                with temporary_file_path(suffix='.pdf') as pdf_path:
                    log(f"🖨️ Exporting temporary PDF: '{pdf_path}'")
                    page.export_pdf(pdf_path)
                    return enclosed_action(pdf_path)
            except pywintypes.com_error:
                log(f"⚠️ !!WARNING!! Page Failed: '{page.name}'")
                return None

        def _convert_docx_to_md_and_use(
            docx_path: pathlib.Path,
            enclosed_action: Callable[[pathlib.Path], TReturn]
        ) -> OneNoteExportMiddleware[TNode, TReturn]:
            md_path = (context.output_dir / safe_page_name).with_suffix('.md')

            # Convert docx to markdown
            log(f"⚙️ Generating markdown: '{md_path}'")
            pandoc_command = f'pandoc.exe -i "{docx_path}" -o "{md_path}"'
            pandoc_command = pandoc_command + ' -t markdown-simple_tables-multiline_tables-grid_tables'
            pandoc_command = pandoc_command + ' --wrap=none'
            self._os_system(pandoc_command)

            enclosed_action(md_path)

        def _pdf_patch_images_into_md(
            md_path: pathlib.Path,
            pdf_path: pathlib.Path
        ) -> TReturn:
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

            def _extract_pdf_pictures() -> list[pathlib.Path]:
                _ensure_assets_dir_exists()
                result_image_names = []
                try:
                    # https://pymupdf.readthedocs.io/en/latest/document.html#Document.__init__
                    doc = fitz.open(pdf_path)
                except fitz.fitz.FileDataError as e:
                    log(f"❗🚫 Error opening PDF for '{md_path}': {e}")
                    return result_image_names
                img_num = 0
                page_index = 0
                try:
                    if len(doc) == 0:
                        log(f"❗🚫 Error opening the PDF for '{md_path}' - it has no pages.")
                        return result_image_names
                    # https://pymupdf.readthedocs.io/en/latest/document.html#Document.pages
                    for pdf_page in doc.pages():
                        # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_images
                        for pdf_page_image in pdf_page.get_images():
                            xref = pdf_page_image[0]
                            pix = fitz.Pixmap(doc, xref)
                            png_name = "%s_%s.png" % (safe_page_name, str(img_num).zfill(3))
                            page_relative_png_path = context.assets_dir / pathlib.Path(png_name)
                            png_output_path = context.output_dir / page_relative_png_path
                            log("🖼️ Writing png: %s" % str(png_output_path))
                            # https://pymupdf.readthedocs.io/en/latest/pixmap.html#Pixmap.n
                            if pix.n < 5:
                                pix.save(str(png_output_path))
                            else:
                                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                                pix1.save(str(png_output_path))
                                pix1 = None
                            pix = None
                            result_image_names.append(page_relative_png_path)
                            img_num += 1
                        count_of_non_ignorable_drawings = _count_non_ignorable_drawings(pdf_page)
                        if count_of_non_ignorable_drawings > 0:
                            log(f"⚠️ !!WARNING!! Page {page_index} of the PDF for '{md_path}' has {count_of_non_ignorable_drawings} non-empty drawings that are not exported.")
                        page_index += 1
                    return result_image_names
                finally:
                    doc.close()

            def _fix_image_names(image_names_to_fix: list[pathlib.Path]):
                tmp_path = md_path.with_suffix(md_path.suffix + '.tmp')
                i = 0
                with open(md_path, 'r', encoding='utf-8') as f_md:
                    with open(tmp_path, 'w', encoding='utf-8') as f_tmp:
                        body_md = f_md.read()
                        for i, path in enumerate(image_names_to_fix):
                            path_str_for_sub = urllib.parse.quote(str(path).encode('utf8'), safe='\\').replace('\\', '/')
                            body_md = re.sub("media/image" + str(i + 1) + r"\.\w+", path_str_for_sub, body_md)
                        f_tmp.write(body_md)
                        body_remaining_broken_image_count = len(re.findall(r"media/image\d+\.\w+", body_md))
                        if body_remaining_broken_image_count > 0:
                            log(f"⚠️ Still has broken images: '{md_path}'")
                shutil.move(tmp_path, md_path)

            # Output picture assets to folder.
            log(f"✂️️ Extracting PDF pictures: '{pdf_path}'")
            image_names_extracted_from_pdf = _extract_pdf_pictures()

            # Replace image names in markdown file.
            log(f"📝️️ Updating image references in markdown: '{md_path}'")
            _fix_image_names(image_names_extracted_from_pdf)

            return next_middleware(context)

        _ensure_output_dir_exists()
        _export_temporary_docx_and_use(
            lambda docx_path: _convert_docx_to_md_and_use(
                docx_path,
                lambda md_path: _export_temporary_pdf_and_use(
                    lambda pdf_path: _pdf_patch_images_into_md(md_path, pdf_path)
                )
            )
        )

        return next_middleware(context)
