import logging
import os
import pathlib
import re
import shutil
import traceback
from logging import info as log
from typing import Callable, Optional

import fitz
import pywintypes

from onenote import *
from path_scrubbing import *


OUTPUT_DIR = os.path.join(os.path.expanduser('~'), "Desktop", "OneNoteExport")
ASSETS_DIR = "assets"
PROCESS_RECYCLE_BIN = False
LOGFILE = 'onenote_to_markdown.log' # Set to None to disable logging
logging.basicConfig(level=logging.INFO)
if LOGFILE:
    logging.Logger.addHandler = logging.FileHandler(LOGFILE)
# For debugging purposes, set this variable to limit which pages are exported:
EXPORT_EXCLUSION_FILTER = r''


def should_handle(node: OneNoteNode) -> bool:
    if not EXPORT_EXCLUSION_FILTER or len(EXPORT_EXCLUSION_FILTER) == 0:
        return True
    if isinstance(node, OneNoteElementBasedNode):
        path_as_lines = os.linesep.join(node.path)
        search_result = re.findall(pattern=EXPORT_EXCLUSION_FILTER, string=path_as_lines, flags= re.IGNORECASE | re.MULTILINE)
        return not search_result or len(search_result) == 0
    return True


def extract_pdf_pictures(pdf_path, assets_path, page_name):
    os.makedirs(assets_path, exist_ok=True)
    image_names = []
    try:
        doc = fitz.open(pdf_path)
    except:
        return []
    img_num = 0
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            png_name = "%s_%s.png" % (page_name, str(img_num).zfill(3))
            png_path = os.path.join(assets_path, png_name)
            log("🖼️ Writing png: %s" % png_path)
            if pix.n < 5:
                pix.save(png_path)
            else:
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.save(png_path)
                pix1 = None
            pix = None
            image_names.append(png_name)
            img_num += 1
    return image_names


def fix_image_names(md_path, image_names):
    tmp_path = md_path + '.tmp'
    i = 0
    with open(md_path, 'r', encoding='utf-8') as f_md:
        with open(tmp_path, 'w', encoding='utf-8') as f_tmp:
            body_md = f_md.read()
            for i,name in enumerate(image_names):
                body_md = re.sub("media\/image" + str(i+1) + "\.[a-zA-ZА-Яа-яЁё]+", name, body_md)
            f_tmp.write(body_md)
    shutil.move(tmp_path, md_path)


class OneNoteNodeConversionVisitor(OneNoteNodeVisitorBase):
    def __init__(self, output_dir: str = OUTPUT_DIR, should_visit: Callable[[OneNoteNode], bool] = lambda node: True):
        super().__init__(should_visit=should_visit)
        self._current_output_folder = [pathlib.Path(output_dir)]
        self._path_component_scrubber = PathComponentScrubber()

    def _get_working_folder_change(self, node: OneNoteNode) -> Optional[pathlib.Path]:
        if isinstance(node, OneNoteElementBasedNode) and not isinstance(node, OneNotePage):
            return self._current_output_folder[0] / self._path_component_scrubber.cleanup_path_component(node.name)
        else:
            return None

    def _invoke_with_working_folder_change(self, new_working_folder: Optional[pathlib.Path], func: Callable):
        if new_working_folder:
            os.makedirs(new_working_folder, exist_ok=True)
            self._current_output_folder.insert(0, new_working_folder)
        try:
            func()
        finally:
            if new_working_folder:
                self._current_output_folder.pop(0)

    def visit_children(self, node: OneNoteNode):
        new_working_folder = self._get_working_folder_change(node)
        self._invoke_with_working_folder_change(new_working_folder, lambda: super(OneNoteNodeConversionVisitor, self).visit_children(node))

    def visit_application(self, node: OneNoteApplication):
        log('🪟 Found OneNote Application')

    def visit_unfiled_notes(self, node: OneNoteUnfiledNotes):
        log('📂 Found Unfiled Notes')

    def visit_notebook(self, node: OneNoteNotebook):
        log('📒 Found Notebook: %s' % node.name)

    def visit_section(self, node: OneNoteSection):
        log('📑 Found Section: %s' % node.name)

    def visit_section_group(self, node: OneNoteSectionGroup):
        log('📑 Found Section Group: %s' % node.name)

    def visit_page(self, node: OneNotePage):
        log('🗒️ Found Page: %s' % node.name)

        page = node
        safe_page_name = self._path_component_scrubber.cleanup_path_component(page.name)

        output_folder_path = str(self._current_output_folder[0])

        path_assets = os.path.join(output_folder_path, ASSETS_DIR)
        output_file_path_without_suffix = os.path.join(output_folder_path, safe_page_name)
        path_docx = output_file_path_without_suffix + '.docx'
        path_pdf = output_file_path_without_suffix + '.pdf'
        path_md = output_file_path_without_suffix + '.md'
        # Remove temp files if exist
        if os.path.exists(path_docx):
            os.remove(path_docx)
        if os.path.exists(path_pdf):
            os.remove(path_pdf)
        try:
            # Create docx
            log("🖨️ Exporting DOCX: '%s'" % path_docx)
            page.export_docx(path_docx)
            # Convert docx to markdown
            log("⚙️ Generating markdown: '%s'" % path_md)
            os.system(
                'pandoc.exe -i "%s" -o "%s" -t markdown-simple_tables-multiline_tables-grid_tables --wrap=none' % (
                path_docx, path_md))
            # Create pdf (for the picture assets)
            log("🖨️ Exporting PDF: '%s'" % path_pdf)
            page.export_pdf(path_pdf)
            # Output picture assets to folder
            log("✂️️ Extracting PDF pictures: '%s'" % path_pdf)
            image_names = extract_pdf_pictures(path_pdf, path_assets, safe_page_name)
            # Replace image names in markdown file
            log("📝️️ Updating image references in markdown: '%s'" % path_md)
            fix_image_names(path_md, image_names)
        except pywintypes.com_error as e:
            log("⚠️ !!WARNING!! Page Failed: '%s'" % path_md)
        # Clean up docx, html
        if os.path.exists(path_docx):
            log("🧹 Cleaning up DOCX: '%s'" % path_docx)
            os.remove(path_docx)
        if os.path.exists(path_pdf):
            log("🧹 Cleaning up PDF: '%s'" % path_pdf)
            os.remove(path_pdf)


OneNoteNodeVisitorBase.register(OneNoteNodeConversionVisitor)


if __name__ == "__main__":
    try:
        onenote = OneNoteApplication()
        visitor = OneNoteNodeConversionVisitor(should_visit=should_handle)
        onenote.accept(visitor)

    except pywintypes.com_error as e:
        traceback.print_exc()
        log("!!!Error!!! Hint: Make sure OneNote is open first.")
