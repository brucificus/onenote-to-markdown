import fitz
import os
import pathlib
import pywintypes
import re
import shutil
from logging import info as log
from typing import Callable

from onenote import OneNotePage
from .OneNoteExportMiddleware import OneNoteExportMiddleware
from .OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from .OneNoteExportMiddlewarePartial import OneNoteExportMiddlewarePartial
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
            docx_path = (context.output_dir / safe_page_name).with_suffix('.docx')

            # Remove temp file if exists from previous run.
            if os.path.exists(docx_path):
                os.remove(docx_path)

            try:
                log(f"🖨️ Exporting temporary DOCX: '{docx_path}'")
                page.export_docx(docx_path)

                return enclosed_action(docx_path)
            except pywintypes.com_error:
                log(f"⚠️ !!WARNING!! Page Failed: '{page.name}'")
                return None
            finally:
                # Clean up docx
                if os.path.exists(docx_path):
                    log(f"🧹 Cleaning up DOCX: '{docx_path}'")
                    os.remove(docx_path)

        def _export_temporary_pdf_and_use(enclosed_action: Callable[[pathlib.Path], TReturn]) -> TReturn:
            pdf_path = (context.output_dir / safe_page_name).with_suffix('.pdf')

            # Remove temp file if exists from previous run.
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            try:
                log(f"🖨️ Exporting temporary PDF: '{pdf_path}'")
                page.export_pdf(pdf_path)

                return enclosed_action(pdf_path)
            except pywintypes.com_error:
                log(f"⚠️ !!WARNING!! Page Failed: '{page.name}'")
                return None
            finally:
                # Clean up docx
                if os.path.exists(pdf_path):
                    log(f"🧹 Cleaning up PDF: '{pdf_path}'")
                    os.remove(pdf_path)

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
            def _extract_pdf_pictures():
                _ensure_assets_dir_exists()
                result_image_names = []
                try:
                    doc = fitz.open(pdf_path)
                except fitz.fitz.FileDataError as e:
                    if e.args[0] == "cannot open broken document":
                        log("🚫 Error opening pdf: %s" % pdf_path)
                        return result_image_names
                img_num = 0
                for i in range(len(doc)):
                    for img in doc.get_page_images(i):
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        png_name = "%s_%s.png" % (safe_page_name, str(img_num).zfill(3))
                        png_path = context.assets_dir / pathlib.Path(png_name)
                        log("🖼️ Writing png: %s" % png_path)
                        if pix.n < 5:
                            pix.save(str(png_path))
                        else:
                            pix1 = fitz.Pixmap(fitz.csRGB, pix)
                            pix1.save(str(png_path))
                            pix1 = None
                        pix = None
                        result_image_names.append(png_name)
                        img_num += 1
                return result_image_names

            def _fix_image_names(image_names_to_fix):
                tmp_path = md_path.with_suffix(md_path.suffix + '.tmp')
                i = 0
                with open(md_path, 'r', encoding='utf-8') as f_md:
                    with open(tmp_path, 'w', encoding='utf-8') as f_tmp:
                        body_md = f_md.read()
                        for i, name in enumerate(image_names_to_fix):
                            body_md = re.sub("media\/image" + str(i + 1) + "\.[a-zA-ZА-Яа-яЁё]+", name, body_md)
                        f_tmp.write(body_md)
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
