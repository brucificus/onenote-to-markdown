import functools
from typing import Iterable, Callable, Tuple, Sequence

import fitz

from onenote_export.Pathlike import Pathlike
from pdf_inspection.PdfDocumentContextManager import PdfDocumentContextManager
from pdf_inspection.PdfDocumentPage import PdfDocumentPage
from pdf_inspection.PdfDocumentPageImage import PdfDocumentPageImage
from pdf_inspection.type_variables import T


class PdfDocument:
    def __init__(self, file_path: Pathlike):
        self._document_context_manager = PdfDocumentContextManager(file_path)
        self._pages: Sequence[PdfDocumentPage] = None
        self.__document_order_page_images: Sequence[PdfDocumentPageImage] = None

    def _use_pymupdf_document(self, func: Callable[[fitz.fitz.Document], T]) -> T:
        with self._document_context_manager as document:
            assert document is not None
            assert document.is_closed is False
            return func(document)

    def _use_pymupdf_pages(self, func: Callable[[Sequence[fitz.fitz.Page]], T]) -> T:
        def apply_func(document: fitz.fitz.Document) -> T:
            pages = tuple(document.pages())
            return func(pages)
        return self._use_pymupdf_document(apply_func)

    def _use_pymupdf_page(self, func: Callable[[fitz.fitz.Page], T], page_index: int) -> T:
        def apply_func(pages: Sequence[fitz.fitz.Page]) -> T:
            return func(pages[page_index])
        return self._use_pymupdf_pages(apply_func)

    @property
    def _document_order_page_images(self) -> Sequence[PdfDocumentPageImage]:
        def yield_document_order_page_image_wrappers() -> Iterable[PdfDocumentPageImage]:
            for page in self.pages:
                yield from page.images

        def get_document_order_page_image_wrappers() -> Tuple[PdfDocumentPageImage]:
            return tuple(yield_document_order_page_image_wrappers())

        if self.__document_order_page_images is None:
            self.__document_order_page_images = get_document_order_page_image_wrappers()

        return self.__document_order_page_images

    @property
    def pages(self) -> Sequence[PdfDocumentPage]:
        def create_page_wrapper(page_index: int) -> PdfDocumentPage:
            page_broker = functools.partial(self._use_pymupdf_page, page_index=page_index)
            return PdfDocumentPage(page_broker, page_index, self)

        def yield_page_wrappers(doc: fitz.fitz.Document) -> Tuple[PdfDocumentPage]:
            for page_index in range(len(doc)):
                yield create_page_wrapper(page_index)

        def create_page_wrappers(doc: fitz.fitz.Document) -> Tuple[PdfDocumentPage]:
            return tuple(yield_page_wrappers(doc))

        if self._pages is None:
            self._pages = self._use_pymupdf_document(create_page_wrappers)

        return self._pages

    def __str__(self):
        return f"{self.__class__.__name__}({self._document_context_manager.file_path})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self._document_context_manager.file_path!r})"

    def __eq__(self, other):
        if not isinstance(other, PdfDocument):
            return NotImplemented
        return self._document_context_manager.file_path == other._document_context_manager.file_path

    def __hash__(self):
        return hash((self._document_context_manager.file_path, self.__class__.__name__))
