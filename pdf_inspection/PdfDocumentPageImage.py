import functools
import os
import shutil

from typing import Callable, Optional

from fitz import fitz

from onenote_export.Pathlike import Pathlike
from onenote_export.temporary_file import TemporaryFilePath
from pdf_inspection.type_variables import T, fitzImagesEntryResolved


class PdfDocumentPageImage:
    def __init__(self,
                 use_pymupdf_page_image: Callable[[fitzImagesEntryResolved], T],
                 page_images_index: int,
                 parent: 'PdfDocumentPage'
                 ):
        self._use_pymupdf_page_image = use_pymupdf_page_image
        self._page_images_index = page_images_index
        self._parent = parent

    @property
    def parent_page(self) -> 'PdfDocumentPage':
        return self._parent

    @property
    def parent_document(self) -> 'PdfDocument':
        return self.parent_page.parent_document

    @property
    def page_images_index(self) -> int:
        return self._page_images_index

    @property
    def document_order_image_index(self) -> Optional[int]:
        document_order_page_images = self.parent_document._document_order_page_images
        return document_order_page_images.index(self)

    def export_png(self, png_output_path: Pathlike) -> None:
        def _try_save_pix_image(resolved_image_entry: fitzImagesEntryResolved) -> None:
            page_image = resolved_image_entry[0]
            save_image: callable
            with TemporaryFilePath(suffix='.png') as tmp_png_output_path:
                # https://pymupdf.readthedocs.io/en/latest/pixmap.html#Pixmap.n
                if page_image.n < 5:
                    save_image = functools.partial(page_image.save, str(tmp_png_output_path))
                    page_image = None
                else:
                    pix1 = fitz.Pixmap(fitz.csRGB, page_image)
                    save_image = functools.partial(pix1.save, str(tmp_png_output_path))
                    pix1 = None
                try:
                    save_image()
                finally:
                    save_image = None

                if png_output_path.exists():
                    os.remove(str(png_output_path))
                shutil.move(tmp_png_output_path, png_output_path)

        self._use_pymupdf_page_image(_try_save_pix_image)

    def __str__(self):
        return f"{self.__class__.__name__}({self.parent_page}, {self._page_images_index})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.parent_page!r}, {self._page_images_index!r})"

    def __eq__(self, other):
        if not isinstance(other, PdfDocumentPageImage):
            return NotImplemented
        return self.parent_page == other.parent_page and self.page_images_index == other.page_images_index

    def __hash__(self):
        return hash((self.parent_page, self.page_images_index))
