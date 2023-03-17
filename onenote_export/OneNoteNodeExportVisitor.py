import fitz
import os
import pathlib
import pywintypes
import re
import shutil
from logging import info as log
from typing import Callable, Optional

from onenote import *

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


class OneNoteNodeExportVisitor(OneNoteNodeVisitorBase):
    def __init__(self,
                 root_output_dir: str,
                 page_relative_assets_dir: str,
                 convert_node_name_to_path_component: Callable[[str], pathlib.Path],
                 should_visit: Callable[[OneNoteNode], bool] = lambda node: True
                 ):
        super().__init__(should_visit=should_visit)
        self._output_dir_stack = [pathlib.Path(root_output_dir)]
        self._page_relative_assets_dir = page_relative_assets_dir
        self._convert_node_name_to_path_component = convert_node_name_to_path_component

    def _get_working_folder_change(self, node: OneNoteNode) -> Optional[pathlib.Path]:
        if isinstance(node, OneNoteElementBasedNode) and not isinstance(node, OneNotePage):
            return self._output_dir_stack[0] / self._convert_node_name_to_path_component(node.name)
        else:
            return None

    def _invoke_with_working_folder_change(self, new_working_folder: Optional[pathlib.Path], func: Callable):
        if new_working_folder:
            os.makedirs(new_working_folder, exist_ok=True)
            self._output_dir_stack.insert(0, new_working_folder)
        try:
            func()
        finally:
            if new_working_folder:
                self._output_dir_stack.pop(0)

    def visit_children(self, node: OneNoteNode):
        new_working_folder = self._get_working_folder_change(node)
        def super_visit_children():
            super(OneNoteNodeExportVisitor, self).visit_children(node)
        self._invoke_with_working_folder_change(new_working_folder, super_visit_children)

    def visit_application(self, node: OneNoteApplication):
        log('🪟 Found OneNote Application')

    def visit_unfiled_notes(self, node: OneNoteUnfiledNotes):
        log('📂 Found Unfiled Notes')

    def visit_notebook(self, node: OneNoteNotebook):
        log(f'📒 Found Notebook: {node.name}')

    def visit_section(self, node: OneNoteSection):
        log(f'📑 Found Section: {node.name}')

    def visit_section_group(self, node: OneNoteSectionGroup):
        log(f'📑 Found Section Group: {node.name}')

    def visit_page(self, page: OneNotePage):
        log(f'🗒️ Found Page: {page.name}')

        safe_page_name = self._convert_node_name_to_path_component(page.name)
        current_output_dir = self._output_dir_stack[0]
        current_assets_dir = current_output_dir / self._page_relative_assets_dir

        output_file_path_without_suffix = os.path.join(current_output_dir, safe_page_name)
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
            log(f"🖨️ Exporting DOCX: '{path_docx}'")
            page.export_docx(path_docx)
            # Convert docx to markdown
            log(f"⚙️ Generating markdown: '{path_md}'")
            pandoc_command = f'pandoc.exe -i "{path_docx}" -o "{path_md}"'
            pandoc_command = pandoc_command + ' -t markdown-simple_tables-multiline_tables-grid_tables'
            pandoc_command = pandoc_command + ' --wrap=none'
            os.system(pandoc_command)
            # Create pdf (for the picture assets)
            log(f"🖨️ Exporting PDF: '{path_pdf}'")
            page.export_pdf(path_pdf)
            # Output picture assets to folder
            log(f"✂️️ Extracting PDF pictures: '{path_pdf}'")
            image_names = extract_pdf_pictures(path_pdf, current_assets_dir, safe_page_name)
            # Replace image names in markdown file
            log(f"📝️️ Updating image references in markdown: '{path_md}'")
            fix_image_names(path_md, image_names)
        except pywintypes.com_error as e:
            log(f"⚠️ !!WARNING!! Page Failed: '{path_md}'")
        # Clean up docx, html
        if os.path.exists(path_docx):
            log(f"🧹 Cleaning up DOCX: '{path_docx}'")
            os.remove(path_docx)
        if os.path.exists(path_pdf):
            log(f"🧹 Cleaning up PDF: '{path_pdf}'")
            os.remove(path_pdf)


OneNoteNodeVisitorBase.register(OneNoteNodeExportVisitor)
