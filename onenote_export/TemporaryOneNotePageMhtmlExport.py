import pathlib
from typing import Optional

from markdown_dom.PandocMarkdownDocumentImportSettings import PandocMarkdownDocumentImportSettings
from onenote import OneNotePage
from onenote_export.Pathlike import Pathlike
from onenote_export.TemporaryOneNotePageExportFile import TemporaryOneNotePageExportFile
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind
from onenote_export.TemporaryPageExportPandocAstJsonContext import TemporaryPageExportPandocAstJsonContext


class TemporaryOneNotePageMhtmlExport(TemporaryPageExportPandocAstJsonContext, TemporaryOneNotePageExportFile):
    def __init__(self, page: OneNotePage, dir: Pathlike = None):
        super().__init__(page, TemporaryOneNotePageExportKind.MHTML, dir)

    def _get_html_file_path(self) -> pathlib.Path:
        mhtml_extraction_dir = self._tempfile_path
        html_files = tuple(mhtml_extraction_dir.glob('*.html')) + tuple(mhtml_extraction_dir.glob('*.htm'))
        assert len(html_files) == 1, f"Expected exactly one HTML file in MHTML export, found {len(html_files)}"
        return html_files[0]

    @staticmethod
    def create_default_import_settings(self) -> PandocMarkdownDocumentImportSettings:
        return PandocMarkdownDocumentImportSettings.create_default_for_onenote_html()

    def create_pandoc_ast_json(self,
                               open_settings: PandocMarkdownDocumentImportSettings = PandocMarkdownDocumentImportSettings.create_default_for_onenote_html(),
                               cworkdir: Optional[Pathlike] = None,
                               ) -> str:
        if not self._tempfile_path:
            raise Exception("Cannot create MarkdownDocument when TemporaryOneNotePageExportFile is not active.")
        if not self._tempfile_path.exists():
            raise FileNotFoundError(f"Path {self._tempfile_path} does not exist")
        if not isinstance(open_settings, PandocMarkdownDocumentImportSettings):
            raise TypeError(f"open_settings must be an instance of PandocMarkdownDocumentImportSettings, not {type(open_settings)}")

        html_file_path = self._get_html_file_path()

        pandoc_ast_json = open_settings.execute_convert_html_file_to_pandoc_ast_json_str(
            input_html_path=html_file_path,
            cworkdir=cworkdir,
        )
        return pandoc_ast_json
