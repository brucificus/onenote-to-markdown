from xml.etree import ElementTree

from .OneNoteNode import OneNoteNode


def create_onenote_node_from_xml_element(element: ElementTree, index: int, parent: OneNoteNode, app: 'win32.CDispatch'):
    if element.tag.endswith('Notebook'):
        from .OneNoteNotebook import OneNoteNotebook
        return OneNoteNotebook(element, parent, index, app)
    elif element.tag.endswith('Section'):
        from .OneNoteSection import OneNoteSection
        return OneNoteSection(element, parent, index, app)
    elif element.tag.endswith('SectionGroup'):
        from .OneNoteSectionGroup import OneNoteSectionGroup
        return OneNoteSectionGroup(element, parent, index, app)
    elif element.tag.endswith('Page'):
        from .OneNotePage import OneNotePage
        return OneNotePage(element, parent, index, app)
    elif element.tag.endswith('UnfiledNotes'):
        from .OneNoteUnfiledNotes import OneNoteUnfiledNotes
        return OneNoteUnfiledNotes(element, parent, index, app)
    else:
        raise Exception(f'Unexpected element type: {element.tag}')
