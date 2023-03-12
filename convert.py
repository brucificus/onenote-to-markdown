import fitz
import os
import pywintypes
import re
import shutil
import traceback
from logging import info as log
import logging
from onenote import *


OUTPUT_DIR = os.path.join(os.path.expanduser('~'), "Desktop", "OneNoteExport")
ASSETS_DIR = "assets"
PROCESS_RECYCLE_BIN = False
LOGFILE = 'onenote_to_markdown.log' # Set to None to disable logging
logging.basicConfig(level=logging.INFO)
if LOGFILE:
    logging.Logger.addHandler = logging.FileHandler(LOGFILE)
# For debugging purposes, set this variable to limit which pages are exported:
LIMIT_EXPORT = r'' # example: YourNotebook\Notes limits it to the Notes tab/page


def should_handle(path):
    return path.startswith(LIMIT_EXPORT)


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
            log("Writing png: %s" % png_path)
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


def handle_page_node(page: OneNotePage):
    page_name = page.name()
    page_path = page.path()

    if not should_handle(page_path):
        return

    output_folder_path = os.path.join(OUTPUT_DIR, page.parent().path())

    os.makedirs(output_folder_path, exist_ok=True)
    path_assets = os.path.join(output_folder_path, ASSETS_DIR)
    output_file_path_without_suffix = os.path.join(output_folder_path, page_name)
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
        os.system('pandoc.exe -i "%s" -o "%s" -t markdown-simple_tables-multiline_tables-grid_tables --wrap=none' % (path_docx, path_md))
        # Create pdf (for the picture assets)
        log("🖨️ Exporting PDF: '%s'" % path_pdf)
        page.export_pdf(path_pdf)
        # Output picture assets to folder
        log("✂️️ Extracting PDF pictures: '%s'" % path_pdf)
        image_names = extract_pdf_pictures(path_pdf, path_assets, page_name)
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


def handle_node(node: OneNoteNode):
    if isinstance(node, OneNoteApplication):
        for child in node.get_notebooks():
            handle_node(child)
        for child in node.get_unfiled_notes():
            handle_node(child)
    if isinstance(node, OneNoteUnfiledNotes):
        for child in node.get_children():
            handle_node(child)
    elif isinstance(node, OneNoteNotebook):
        for child in node.get_children():
            handle_node(child)
    elif isinstance(node, OneNoteSectionGroup):
        for child in node.get_section_groups():
            handle_node(child)
        for child in node.get_sections():
            handle_node(child)
    elif isinstance(node, OneNoteSection):
        for child in node.get_pages():
            handle_node(child)
    elif isinstance(node, OneNotePage):
        handle_page_node(node)
        for child in node.get_subpages():
            handle_node(child)
    else:
        raise Exception("Unknown node type: %s" % type(node))


if __name__ == "__main__":
    try:
        onenote = OneNoteApplication()
        handle_node(onenote)

    except pywintypes.com_error as e:
        traceback.print_exc()
        log("!!!Error!!! Hint: Make sure OneNote is open first.")
