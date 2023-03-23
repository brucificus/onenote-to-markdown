import pathlib
from typing import ContextManager

from onenote import OneNotePage
from onenote_export import temporary_file
from onenote_export.Pathlike import Pathlike
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind


class TemporaryOneNotePageExportFile(temporary_file.TemporaryFilePath, ContextManager[pathlib.Path]):
    def __init__(self, page: OneNotePage, kind: TemporaryOneNotePageExportKind, dir: Pathlike = None):
        if not isinstance(page, OneNotePage):
            raise TypeError(f"Page must be an instance of OneNotePage, not {type(page)}")
        if not isinstance(kind, TemporaryOneNotePageExportKind):
            raise TypeError(f"Kind must be an instance of TemporaryOneNotePageExportKind, not {type(kind)}")
        super().__init__(suffix=f'.{kind.value}', prefix='tmp', dir=dir)
        self._page = page
        self._kind = kind

    def __enter__(self):
        self._tempfile_path = super().__enter__()
        if self._kind == TemporaryOneNotePageExportKind.PDF:
            self._page._export_pdf(self._tempfile_path)
        elif self._kind == TemporaryOneNotePageExportKind.DOCX:
            self._page._export_docx(self._tempfile_path)
        else:
            raise ValueError(f"Unknown kind: {self._kind}")
        return self._tempfile_path

    @property
    def tempfile_path(self) -> pathlib.Path:
        return self._tempfile_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
