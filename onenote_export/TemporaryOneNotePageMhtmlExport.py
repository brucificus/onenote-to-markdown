import pathlib
import shutil

from typing import Optional, Callable, Sequence

from markdown_dom.PandocMarkdownDocumentImportSettings import PandocMarkdownDocumentImportSettings
from onenote import OneNotePage
from onenote_export.PageExportAssetExtraction import PageExportAssetExtraction
from onenote_export.Pathlike import Pathlike
from onenote_export.TemporaryOneNotePageExportFile import TemporaryOneNotePageExportFile
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind
from onenote_export.TemporaryPageExportPandocAstJsonContext import TemporaryPageExportPandocAstJsonContext


class TemporaryOneNotePageMhtmlExport(TemporaryPageExportPandocAstJsonContext, PageExportAssetExtraction, TemporaryOneNotePageExportFile):
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

    def extract_assets_to(self,
                          target_dir: Pathlike,
                          map_extraction_path: Optional[Callable[[pathlib.Path], Optional[pathlib.Path]]] = None,
                          ) -> Sequence[pathlib.Path]:
        """
        Extracts assets from the page export to the target directory.
        :param target_dir: The directory to extract assets to.
        :param map_extraction_path: A function that takes a path to an asset and returns the path to which the asset should be extracted. If None, the asset will not be extracted.
        :return: The paths to the extracted assets.
        """
        if not self._tempfile_path:
            raise Exception("Cannot create MarkdownDocument when TemporaryOneNotePageExportFile is not active.")
        if not self._tempfile_path.exists():
            raise FileNotFoundError(f"Path {self._tempfile_path} does not exist")
        if isinstance(target_dir, str):
            target_dir = pathlib.Path(target_dir)
        if not isinstance(target_dir, pathlib.Path):
            raise TypeError(f"target_dir must be an instance of pathlib.Path or str, not {type(target_dir)}")

        extracted_files = ()

        mhtml_extraction_dir = self._tempfile_path
        for asset_file in mhtml_extraction_dir.glob('**/*.*'):
            if asset_file.is_file():
                asset_file_relative_path = pathlib.Path(asset_file.relative_to(mhtml_extraction_dir))
                if map_extraction_path is not None:
                    asset_file_relative_path = map_extraction_path(asset_file_relative_path)

                if asset_file_relative_path:
                    asset_file_target_path = target_dir / asset_file_relative_path
                    asset_file_target_path.parent.mkdir(parents=True, exist_ok=True)
                    if asset_file_target_path.exists():
                        with asset_file_target_path.open('w+b') as target:
                            target.write(asset_file.read_bytes())
                    else:
                        shutil.copy2(asset_file, asset_file_target_path)

                    asset_file_target_path = asset_file_target_path.relative_to(target_dir)
                    extracted_files += (asset_file_target_path,)

        return extracted_files
