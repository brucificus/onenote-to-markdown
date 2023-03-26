from onenote import OneNotePage
from onenote_export.Pathlike import Pathlike
from onenote_export.TemporaryOneNotePageExportFile import TemporaryOneNotePageExportFile
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind
from pdf_inspection.PdfDocument import PdfDocument


class TemporaryOneNotePagePdfExport(TemporaryOneNotePageExportFile):
    def __init__(self, page: OneNotePage, dir: Pathlike = None):
        super().__init__(page, TemporaryOneNotePageExportKind.PDF, dir)

    def __enter__(self):
        tempfile_path = super().__enter__()
        self._pdf_document = PdfDocument(tempfile_path)

    @property
    def pdf_document(self) -> PdfDocument:
        if self._pdf_document is None:
            raise RuntimeError("TemporaryOneNotePagePdfExport must be entered before accessing pdf_document")
        return self._pdf_document

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pdf_document = None
        super().__exit__(exc_type, exc_val, exc_tb)
