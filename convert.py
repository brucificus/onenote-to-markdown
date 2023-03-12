import os
import shutil
import sys
import typing
from abc import ABC, abstractmethod
from enum import Enum

import fitz
import win32com.client as win32
import pywintypes
import re
import traceback
from xml.etree import ElementTree

OUTPUT_DIR = os.path.join(os.path.expanduser('~'), "Desktop", "OneNoteExport")
ASSETS_DIR = "assets"
PROCESS_RECYCLE_BIN = False
LOGFILE = 'onenote_to_markdown.log' # Set to None to disable logging
# For debugging purposes, set this variable to limit which pages are exported:
LIMIT_EXPORT = r'' # example: YourNotebook\Notes limits it to the Notes tab/page


def log(message):
    print(message)
    if LOGFILE is not None:
        with open(LOGFILE, 'a', encoding='UTF-8') as lf:
            lf.write(f'{message}\n')

def safe_str(name):
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", name)

def should_handle(path):
    return path.startswith(LIMIT_EXPORT)


class HierarchyScope(Enum):
    Self: int = 0
    '''Gets just the start node specified and no descendants.'''

    Children: int = 1
    '''Gets the immediate child nodes of the start node, and no descendants in higher or lower subsection groups.'''

    Notebooks: int = 2
    '''Gets all notebooks below the start node, or root.'''

    Sections: int = 3
    '''Gets all sections below the start node, including sections in section groups and subsection groups.'''

    Pages: int = 4
    '''Gets all pages below the start node, including all pages in section groups and subsection groups.'''


class OneNoteNode(ABC):
    def __init__(self, app: win32.CDispatch = None):
        self._app = app if app is not None else self._create_onenote_com_object()

    @abstractmethod
    def node_id(self) -> str:
        pass

    def _create_onenote_com_object(self) -> win32.CDispatch:
        try:
            return win32.gencache.EnsureDispatch("OneNote.Application.12")
        except pywintypes.com_error as e:
            traceback.print_exc()
            log("!!!Error!!! Hint: Make sure OneNote is open first.")

    def __get_hierarchy(self, node_id: str, scope: HierarchyScope) -> ElementTree:
        return ElementTree.fromstring(self._app.GetHierarchy(node_id, scope.value, ""))

    def _get_children_xml(self) -> ElementTree:
        return self.__get_hierarchy(self.node_id(), HierarchyScope.Children)

    def _get_pages_xml(self) -> ElementTree:
        return self.__get_hierarchy(self.node_id(), HierarchyScope.Pages)

    def _get_notebooks_xml(self) -> ElementTree:
        return self.__get_hierarchy(self.node_id(), HierarchyScope.Notebooks)

    def _get_sections_xml(self) -> ElementTree:
        return self.__get_hierarchy(self.node_id(), HierarchyScope.Sections)

    def _produce_child_node(self, element: ElementTree, index: int) -> 'OneNoteElementBasedNode':
        if element.tag.endswith('Notebook'):
            return OneNoteNotebook(element, self, index, self._app)
        elif element.tag.endswith('Section'):
            return OneNoteSection(element, self, index, self._app)
        elif element.tag.endswith('SectionGroup'):
            return OneNoteSectionGroup(element, self, index, self._app)
        elif element.tag.endswith('Page'):
            return OneNotePage(element, self, index, self._app)
        elif element.tag.endswith('UnfiledNotes'):
            return OneNoteUnfiledNotes(element, self, index, self._app)
        else:
            raise Exception(f'Unexpected element type: {element.tag}')

    def get_children(self) -> list['OneNoteElementBasedNode']:
        for i, child_element in enumerate(self._get_children_xml()):
            child = self._produce_child_node(child_element, i)
            if isinstance(child, OneNoteElementBasedNode):
                yield child
            else:
                raise Exception(f'Unexpected child type: {child_element.tag}')


class OneNoteElementBasedNode(OneNoteNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(app)
        self._element = element
        self._parent = parent
        self._index = index

    def node_id(self) -> str:
        return self._element.attrib['ID']

    def parent(self) -> OneNoteNode:
        return self._parent

    @staticmethod
    def _safe_str(value: str) -> str:
        return re.sub(r'[^.a-zA-Z0-9一-鿆ぁ-んァ-ヾㄱ-힝々א-ת\s]', '_', value)

    def name(self) -> str:
        if os.path.supports_unicode_filenames:
            return self._element.attrib['name']
        else:
            return self._safe_str(self._element.attrib['name'])

    def path(self) -> str:
        parent_path = self._parent.path() if isinstance(self._parent, OneNoteElementBasedNode) else ''
        return os.path.join(parent_path, self.name())

    def index(self) -> int:
        return self._index


OneNoteNode.register(OneNoteElementBasedNode)


class OneNotePage(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def export_docx(self, path: str):
        self._app.Publish(self.node_id(), path, win32.constants.pfWord, "")

    def export_pdf(self, path: str):
        self._app.Publish(self.node_id(), path, 3, "")


OneNoteElementBasedNode.register(OneNotePage)


class OneNoteSection(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def get_pages(self) -> list[OneNotePage]:
        for child in self.get_children():
            if isinstance(child, OneNotePage):
                yield child
            else:
                raise Exception(f'Unexpected child type: {type(child)}')


OneNoteElementBasedNode.register(OneNoteSection)


class OneNoteUnfiledNotes(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def get_pages(self) -> list[OneNotePage]:
        for child in self.get_children():
            if isinstance(child, OneNotePage):
                yield child
            else:
                raise Exception(f'Unexpected child type: {type(child)}')


OneNoteElementBasedNode.register(OneNoteSection)


class OneNoteSectionGroup(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)

    def get_section_groups(self) -> list['OneNoteSectionGroup']:
        for child in self.get_children():
            if isinstance(child, OneNoteSectionGroup):
                yield child
            elif isinstance(child, OneNoteSection):
                pass
            else:
                raise Exception(f'Unexpected child type: {type(child)}')

    def get_sections(self) -> list[OneNoteSection]:
        for child in self.get_children():
            if isinstance(child, OneNoteSection):
                yield child
            elif isinstance(child, OneNoteSectionGroup):
                pass
            else:
                raise Exception(f'Unexpected child type: {type(child)}')


OneNoteElementBasedNode.register(OneNoteSectionGroup)


class OneNoteNotebook(OneNoteElementBasedNode):
    def __init__(self, element: ElementTree, parent: OneNoteNode, index: int, app: win32.CDispatch = None):
        super().__init__(element, parent, index, app)


OneNoteElementBasedNode.register(OneNoteNotebook)


class OneNoteApplication(OneNoteNode):
    def node_id(self) -> str:
        return ""

    def get_notebooks(self) -> list[OneNoteNotebook]:
        for child in self.get_children():
            if isinstance(child, OneNoteNotebook):
                yield child
            elif isinstance(child, OneNoteUnfiledNotes):
                pass
            else:
                raise Exception(f'Unexpected child type: {type(child)}')

    def get_unfiled_notes(self) -> OneNoteUnfiledNotes:
        for child in self.get_children():
            if isinstance(child, OneNoteUnfiledNotes):
                return child
            elif isinstance(child, OneNoteNotebook):
                pass
            else:
                raise Exception(f'Unexpected child type: {type(child)}')
        return None


OneNoteNode.register(OneNoteApplication)


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
    index_prefixed_page_name = "%s_%s" % (str(page.index()).zfill(3), page.name())
    index_infixed_page_path = os.path.join(page.parent().path(), index_prefixed_page_name)

    if not should_handle(index_infixed_page_path):
        return

    output_folder_path = os.path.join(OUTPUT_DIR, page.parent().path())

    os.makedirs(output_folder_path, exist_ok=True)
    path_assets = os.path.join(output_folder_path, ASSETS_DIR)
    output_file_path_without_suffix = os.path.join(output_folder_path, index_prefixed_page_name)
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
        image_names = extract_pdf_pictures(path_pdf, path_assets, index_prefixed_page_name)
        # Replace image names in markdown file
        log("📝️️ Updating image references in markdown: '%s'" % path_md)
        fix_image_names(path_md, image_names)
    except pywintypes.com_error as e:
        log("!!WARNING!! Page Failed: '%s'" % path_md)
    # Clean up docx, html
    if os.path.exists(path_docx):
        log("🧹 Cleaning up DOCX: '%s'" % path_docx)
        os.remove(path_docx)
    if os.path.exists(path_pdf):
        log("🧹 Cleaning up PDF: '%s'" % path_pdf)
        os.remove(path_pdf)


def handle_section_node(section: OneNoteSection):
    for child_page in section.get_pages():
        handle_node(child_page)


def handle_section_group_node(section_group: OneNoteSectionGroup):
    for child_section_group in section_group.get_section_groups():
        handle_node(child_section_group)

    for child_section in section_group.get_sections():
        handle_node(child_section)


def handle_notebook_node(notebook: OneNoteNotebook):
    for child in notebook.get_children():
        handle_node(child)


def handle_node(node: OneNoteNode):
    if isinstance(node, OneNoteApplication):
        for child in node.get_notebooks():
            handle_node(child)
    elif isinstance(node, OneNoteNotebook):
        handle_notebook_node(node)
    elif isinstance(node, OneNoteSectionGroup):
        handle_section_group_node(node)
    elif isinstance(node, OneNoteSection):
        handle_section_node(node)
    elif isinstance(node, OneNotePage):
        # try:
            handle_page_node(node)
        # except:
        #     print("Page failed unexpectedly: %s" % node, file=sys.stderr)
    else:
        raise Exception("Unknown node type: %s" % type(node))


if __name__ == "__main__":
    try:
        onenote = OneNoteApplication()
        handle_node(onenote)

    except pywintypes.com_error as e:
        traceback.print_exc()
        log("!!!Error!!! Hint: Make sure OneNote is open first.")
