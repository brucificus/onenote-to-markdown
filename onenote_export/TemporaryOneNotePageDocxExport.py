from typing import Optional

from markdown_dom.PandocMarkdownDocumentImportSettings import PandocMarkdownDocumentImportSettings
from onenote import OneNotePage
from onenote_export.Pathlike import Pathlike
from onenote_export.TemporaryOneNotePageExportFile import TemporaryOneNotePageExportFile
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind


class TemporaryOneNotePageDocxExport(TemporaryOneNotePageExportFile):
    def __init__(self, page: OneNotePage, dir: Pathlike = None):
        super().__init__(page, TemporaryOneNotePageExportKind.DOCX, dir)

    def create_pandoc_ast_json(self,
                               open_settings: PandocMarkdownDocumentImportSettings = PandocMarkdownDocumentImportSettings.create_default_for_onenote_docx(),
                               cworkdir: Optional[Pathlike] = None,
                               ) -> str:
        if not self._tempfile_path:
            raise Exception("Cannot create MarkdownDocument when TemporaryOneNotePageExportFile is not active.")
        if not self._tempfile_path.exists():
            raise FileNotFoundError(f"File {self._tempfile_path} does not exist")
        if not isinstance(open_settings, PandocMarkdownDocumentImportSettings):
            raise TypeError(f"open_settings must be an instance of PandocMarkdownDocumentImportSettings, not {type(open_settings)}")

        pandoc_ast_json = open_settings.execute_convert_docx_file_to_pandoc_ast_json_str(
            input_docx_path=self._tempfile_path,
            cworkdir=cworkdir,
        )
        return pandoc_ast_json
