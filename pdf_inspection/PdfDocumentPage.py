import functools

from typing import Callable, Iterable, Sequence, Tuple

from fitz import fitz

from pdf_inspection.PdfDocumentPageDrawing import PdfDocumentPageDrawing
from pdf_inspection.PdfDocumentPageImage import PdfDocumentPageImage
from pdf_inspection.type_variables import T, fitzDrawings, fitzImagesEntryRaw, fitzImagesEntryResolved, fitzDrawingsEntry


class PdfDocumentPage:
    def __init__(self, use_pymupdf_page: Callable[[fitz.Page], T], page_index: int, parent: 'PdfDocument'):
        self._use_pymupdf_page = use_pymupdf_page
        self._page_index = page_index
        self._drawings: Sequence[PdfDocumentPageDrawing] = None
        self._images: Sequence[PdfDocumentPageImage] = None
        self._parent = parent

    @property
    def parent_document(self) -> 'PdfDocument':
        return self._parent

    def _use_pymupdf_page_images_raw(self, func: Callable[[Sequence[fitzImagesEntryRaw]], T]) -> T:
        def get_images(pymupdf_page: fitz.Page) -> Sequence[fitz.Pixmap]:
            # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_images
            return pymupdf_page.get_images()  # TODO: parameter 'full'.

        def apply_func(pymupdf_page: fitz.Page) -> T:
            return func(get_images(pymupdf_page))

        return self._use_pymupdf_page(apply_func)

    def _use_pymupdf_page_image_entry_resolved(self, func: Callable[[fitzImagesEntryResolved], T], page_images_index: int) -> T:
        def resolve_pixmap_from_page_images_entry(page_images_entry: fitzImagesEntryRaw) -> fitzImagesEntryResolved:
            xref = page_images_entry[0]
            pixmap = self._parent._use_pymupdf_document(lambda document: fitz.Pixmap(document, xref))
            return (pixmap, *page_images_entry[1:])

        def apply_func(page_images: Sequence[fitzImagesEntryRaw]) -> T:
            return func(resolve_pixmap_from_page_images_entry(page_images[page_images_index]))

        return self._use_pymupdf_page_images_raw(apply_func)

    def _use_pymupdf_page_drawings(self, func: Callable[[fitzDrawings], T]) -> T:
        def get_drawings(pymupdf_page: fitz.Page) -> fitzDrawings:
            # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_drawings
            return pymupdf_page.get_drawings()  # TODO: parameter 'extended'.

        def apply_func(pymupdf_page: fitz.Page) -> T:
            return func(get_drawings(pymupdf_page))

        return self._use_pymupdf_page(apply_func)

    def _use_pymupdf_page_drawing_entry(self, func: Callable[[fitzDrawingsEntry], T], drawing_index: int) -> T:
        def apply_func(drawings: fitzDrawings) -> T:
            return func(drawings[drawing_index])

        return self._use_pymupdf_page_drawings(apply_func)

    @property
    def page_index(self) -> int:
        return self._page_index

    @property
    def drawings(self) -> Sequence[PdfDocumentPageDrawing]:
        def create_drawing_wrapper(drawing_index: int) -> PdfDocumentPageDrawing:
            drawings_entry_broker = functools.partial(self._use_pymupdf_page_drawing_entry, drawing_index=drawing_index)
            return PdfDocumentPageDrawing(drawings_entry_broker, drawing_index, self)

        def yield_drawings_wrappers(drawings: fitzDrawings) -> Iterable[PdfDocumentPageDrawing]:
            for drawing_index in range(len(drawings)):
                yield create_drawing_wrapper(drawing_index)

        def create_drawings_wrappers(drawings: fitzDrawings) -> Tuple[PdfDocumentPageDrawing]:
            return tuple(yield_drawings_wrappers(drawings))

        if self._drawings is None:
            self._drawings = self._use_pymupdf_page_drawings(create_drawings_wrappers)

        assert self._drawings is not None
        return self._drawings

    @property
    def images(self) -> Sequence[PdfDocumentPageImage]:
        def create_image_wrapper(image_index: int) -> PdfDocumentPageImage:
            image_broker = functools.partial(self._use_pymupdf_page_image_entry_resolved, page_images_index=image_index)
            return PdfDocumentPageImage(image_broker, image_index, self)

        def yield_images_wrappers(images: Sequence[fitzImagesEntryRaw]) -> Iterable[PdfDocumentPageImage]:
            for image_index in range(len(images)):
                yield create_image_wrapper(image_index)

        def create_images_wrappers(images: Sequence[fitzImagesEntryRaw]) -> Tuple[PdfDocumentPageImage]:
            return tuple(yield_images_wrappers(images))

        if self._images is None:
            self._images = self._use_pymupdf_page_images_raw(create_images_wrappers)

        assert self._images is not None
        return self._images

    def __str__(self):
        return f"{self.__class__.__name__}({self.parent_document}, {self._page_index})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.parent_document!r}, {self._page_index!r})"

    def __eq__(self, other):
        if not isinstance(other, PdfDocumentPage):
            return NotImplemented
        return self.parent_document == other.parent_document and self._page_index == other._page_index

    def __hash__(self):
        return hash((self.parent_document, self._page_index, self.__class__.__name__))
