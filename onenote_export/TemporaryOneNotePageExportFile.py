import pathlib

from typing import ContextManager

from mhtml_dom.MhtmlContainer import MhtmlContainer
from onenote import OneNotePage
from onenote_export import temporary_file
from onenote_export.Pathlike import Pathlike
from onenote_export.temporary_file import TemporaryFilePath
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind


class TemporaryOneNotePageExportFile(temporary_file.TemporaryFilePath, ContextManager[pathlib.Path]):
    def __init__(self, page: OneNotePage, kind: TemporaryOneNotePageExportKind, dir: Pathlike = None):
        if not isinstance(page, OneNotePage):
            raise TypeError(f"Page must be an instance of OneNotePage, not {type(page)}")
        if not isinstance(kind, TemporaryOneNotePageExportKind):
            raise TypeError(f"Kind must be an instance of TemporaryOneNotePageExportKind, not {type(kind)}")
        super().__init__(suffix=f'.{kind.value}', prefix='tmp', dir=dir)
        self._enters = 0
        self._page = page
        self._kind = kind

    def __enter__(self):
        self._enters += 1
        if self._enters > 1:
            return self._tempfile_path

        if self._kind == TemporaryOneNotePageExportKind.PDF:
            self._tempfile_path = super().__enter__()
            self._page._export_pdf(self._tempfile_path)
            return self._tempfile_path

        if self._kind == TemporaryOneNotePageExportKind.DOCX:
            self._tempfile_path = super().__enter__()
            self._page._export_docx(self._tempfile_path)
            return self._tempfile_path

        if self._kind == TemporaryOneNotePageExportKind.MHTML:
            mhtml_extraction_dir = super().__enter__()
            self._tempfile_path = mhtml_extraction_dir
            with TemporaryFilePath(suffix='.mht') as mhtml_file:
                self._page._export_mhtml(mhtml_file)
                mhtml_container = MhtmlContainer.read_file(mhtml_file)
                mhtml_container.extractall(mhtml_extraction_dir)
            return self._tempfile_path

        raise ValueError(f"Unknown kind: {self._kind}")


    @property
    def tempfile_path(self) -> pathlib.Path:
        return self._tempfile_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._enters -= 1
        if self._enters > 0:
            return

        super().__exit__(exc_type, exc_val, exc_tb)
