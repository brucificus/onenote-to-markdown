import pathlib

import fitz

from onenote_export.Pathlike import Pathlike


class PdfDocumentContextManager:
    def __init__(self, file_path: Pathlike):
        if isinstance(file_path, str):
            file_path = pathlib.Path(file_path)
        if not isinstance(file_path, pathlib.Path):
            raise TypeError(f"file_path must be a str or pathlib.Path, not {type(file_path)}")

        self._file_path = file_path
        self._pymupdf_document = None

    _enters: int = 0

    @property
    def file_path(self) -> Pathlike:
        return self._file_path

    def __enter__(self) -> fitz.Document:
        if self._pymupdf_document is None:
            assert self._enters == 0
            assert self._file_path.exists()
            file_path = str(self._file_path)
            # https://pymupdf.readthedocs.io/en/latest/document.html#Document.__init__
            self._pymupdf_document = fitz.Document(file_path)

        self._enters += 1
        assert self._pymupdf_document is not None
        return self._pymupdf_document

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._enters > 0
        self._enters -= 1
        if self._enters == 0:
            assert self._pymupdf_document is not None
            self._pymupdf_document.close()
            self._pymupdf_document = None
