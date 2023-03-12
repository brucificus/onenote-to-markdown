import enum
from enum import Enum


@enum.unique
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
