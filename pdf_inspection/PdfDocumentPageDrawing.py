from functools import cache
from typing import Callable

from fitz import fitz

from pdf_inspection.type_variables import T, fitzDrawingsEntry, fitzDrawingsEntryItems


class PdfDocumentPageDrawing:
    def __init__(self,
                 use_pymupdf_page_drawings_entry: Callable[[fitzDrawingsEntry], T],
                 page_drawings_index: int,
                 parent: 'PdfDocumentPage',
                 ):
        self._use_pymupdf_page_drawings_entry = use_pymupdf_page_drawings_entry
        self._page_drawings_index = page_drawings_index
        self._parent = parent
        self._is_effectively_empty: bool = None

    @property
    def parent_page(self) -> 'PdfDocumentPage':
        return self._parent

    @property
    def parent_document(self) -> 'PdfDocument':
        return self.parent_page.parent_document

    @property
    def is_effectively_empty(self) -> bool:
        def determine_is_effectively_empty(pymupdf_page_drawings_entry: fitzDrawingsEntry) -> bool:
            drawings_entry_items: fitzDrawingsEntryItems = pymupdf_page_drawings_entry['items']
            drawings_entry_items_count = len(drawings_entry_items)
            if drawings_entry_items_count == 0:
                return True  # Literally nothing here.
            if drawings_entry_items_count == 1:  # There's only one item, so it might be a default rectangle.
                drawings_entry_item = drawings_entry_items[0]
                drawings_entry_item_shape = drawings_entry_item[1]
                is_rect = isinstance(drawings_entry_item_shape, fitz.Rect)
                if is_rect:
                    rect_height_is_default = abs(drawings_entry_item_shape.height - 0.72) < 0.01
                    rect_width_is_default = abs(drawings_entry_item_shape.width - 100.37) < 0.01
                    if rect_width_is_default or rect_height_is_default:
                        return True
            return False

        if self._is_effectively_empty is None:
            self._is_effectively_empty = self._use_pymupdf_page_drawings_entry(determine_is_effectively_empty)

        assert self._is_effectively_empty is not None
        return self._is_effectively_empty

    def __str__(self):
        return f"{self.__class__.__name__}({self.parent_page}, {self._page_drawings_index})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.parent_page!r}, {self._page_drawings_index!r})"

    def __eq__(self, other):
        if not isinstance(other, PdfDocumentPageDrawing):
            return NotImplemented
        return self.parent_page == other.parent_page and self._page_drawings_index == other._page_drawings_index

    def __hash__(self):
        return hash((self.parent_page, self._page_drawings_index, self.__class__.__name__))
