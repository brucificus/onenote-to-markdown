from onenote import OneNotePage
from onenote_export.Pathlike import Pathlike
from onenote_export.TemporaryOneNotePageExportFile import TemporaryOneNotePageExportFile
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind


class TemporaryOneNotePagePdfExport(TemporaryOneNotePageExportFile):
    def __init__(self, page: OneNotePage, dir: Pathlike = None):
        super().__init__(page, TemporaryOneNotePageExportKind.PDF, dir)

    def __enter__(self):
        tempfile_path = super().__enter__()
        import fitz
        # https://pymupdf.readthedocs.io/en/latest/document.html#Document.__init__
        self._pymupdf_document = fitz.open(tempfile_path)

    @property
    def pymupdf_document(self) -> 'fitz.Document':
        if self._pymupdf_document is None:
            raise RuntimeError("TemporaryOneNotePagePdfExport must be entered before accessing pymupdf_document")

        return self._pymupdf_document

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pymupdf_document.close()
        self._pymupdf_document = None
        super().__exit__(exc_type, exc_val, exc_tb)
