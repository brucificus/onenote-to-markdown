from xml.etree import ElementTree

from .OneNoteAPI import OneNoteAPI
from .OneNoteNode import OneNoteNode


def create_onenote_node_from_xml_element(element: ElementTree, index: int, parent: OneNoteNode, onenote_api: OneNoteAPI):
    if element.tag.endswith('Notebook'):
        from .OneNoteNotebook import OneNoteNotebook
        return OneNoteNotebook(element, parent, index, onenote_api)
    if element.tag.endswith('Section'):
        from .OneNoteSection import OneNoteSection
        return OneNoteSection(element, parent, index, onenote_api)
    if element.tag.endswith('SectionGroup'):
        from .OneNoteSectionGroup import OneNoteSectionGroup
        return OneNoteSectionGroup(element, parent, index, onenote_api)
    if element.tag.endswith('Page'):
        from .OneNotePage import OneNotePage
        return OneNotePage(element, parent, index, onenote_api)
    if element.tag.endswith('UnfiledNotes'):
        from .OneNoteUnfiledNotes import OneNoteUnfiledNotes
        return OneNoteUnfiledNotes(element, parent, index, onenote_api)
    if element.tag.endswith('OpenSections'):
        from .OneNoteOpenSections import OneNoteOpenSections
        return OneNoteOpenSections(element, parent, index, onenote_api)
    raise ValueError(f'Unexpected element type: {element.tag}')
